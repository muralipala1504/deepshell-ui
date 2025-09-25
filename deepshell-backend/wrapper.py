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

# ✅ Primary allowed keywords (broad DevOps/infra domain)
ALLOWED_KEYWORDS = [
    "linux", "bash", "shell", "command",
    "devops", "docker", "kubernetes", "k8s",
    "cloud", "aws", "azure", "gcp",
    "ansible", "terraform", "iac",
    "infrastructure", "sysadmin",
    "ci", "cd", "pipeline",
    "jenkins", "gitlab", "github actions", "circleci", "travis",
    "helm", "istio", "rancher", "openshift",
    "vagrant", "packer", "consul", "vault",
    "nginx", "apache", "haproxy", "firewall", "iptables",
    "ssl", "tls", "mysql", "postgresql", "mongodb", "redis",
    "git", "svn"
]

# ✅ Chef/Puppet require context keywords
CHEF_TERMS = ["chef recipe", "chef cookbook", "chef resource", "chef file"]
PUPPET_TERMS = ["puppet manifest", "puppet module", "puppet class"]

# ✅ Excluded obvious non-tech words (to avoid false positives)
EXCLUDED_CONTEXT = [
    "food", "cooking", "kitchen", "biryani", "chicken", "mutton", "pasta",
    "oil pipeline", "business", "finance", "company fraud", "movie", "song"
]

def is_allowed_query(query: str) -> bool:
    query_lower = query.lower()

    # Excluded words take priority
    if any(bad in query_lower for bad in EXCLUDED_CONTEXT):
        return False

    # Chef/Puppet context check
    if any(term in query_lower for term in CHEF_TERMS + PUPPET_TERMS):
        return True

    # General DevOps/infra keywords check
    if any(kw in query_lower for kw in ALLOWED_KEYWORDS):
        return True

    return False

def clean_output(raw: str) -> str:
    """Ensure response is copy-ready command/script only."""
    raw = raw.strip()
    if not raw:
        return "No output from deepshell CLI."

    # If there are code fences, extract the first fenced block
    if "```" in raw:
        parts = raw.split("```")
        if len(parts) >= 2:
            code = parts[1].strip()
            return f"```bash\n{code}\n```"

    # If multi-line or short one-liner, wrap as bash
    if "\n" in raw or len(raw.split()) <= 8:
        return f"```bash\n{raw}\n```"

    # Default: return as-is (plain text, no copy button)
    return raw

@app.post("/run-agent")
async def run_agent(request: AgentRequest):
    # ✅ Reject non-domain queries
    if not is_allowed_query(request.prompt):
        return {"output": "⚠️ Deepshell is specialized for Linux, Infra, DevOps, Cloud, and IaC tasks only. General Q&A is not supported here."}

    try:
        result = subprocess.run(
            ["python3", "-m", "deepshell", request.prompt],
            capture_output=True,
            text=True,
            check=True,
            env=os.environ
        )
        cleaned = clean_output(result.stdout)
        return {"output": cleaned}
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or e.stdout.strip() or "Unknown error"
        raise HTTPException(status_code=500, detail=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("wrapper:app", host="0.0.0.0", port=8001, reload=True)
