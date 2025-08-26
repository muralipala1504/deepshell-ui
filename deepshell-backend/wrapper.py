import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# CORS setup (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your UI folder
ui_path = os.path.join(os.path.dirname(__file__), '..')

# Serve static files (JS, CSS, etc.) under /static
app.mount("/static", StaticFiles(directory=ui_path), name="static")

# Serve index.html on root
@app.get("/")
async def root():
    return FileResponse(os.path.join(ui_path, "index.html"))

class AgentRequest(BaseModel):
    prompt: str

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    try:
        result = subprocess.run(
            ["deepshell", request.prompt],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        output = result.stdout.strip()
        if not output:
            output = "No output from deepshell CLI."
        return {"output": output}
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "Unknown error"
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wrapper:app", host="0.0.0.0", port=8001, reload=True)
