from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    prompt: str

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    return {"output": f"Received: {request.prompt}"}
