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
    "linux", "bash", "shell", "command", "script", "terminal", "cli",
    "devops", "docker", "kubernetes", "k8s", "container", "pod",
    "cloud", "aws", "azure", "gcp", "ec2", "s3", "lambda",
    "ansible", "terraform", "iac", "playbook", "manifest",
    "infrastructure", "sysadmin", "server", "vm", "instance",
    "ci", "cd", "pipeline", "build", "deploy", "deployment",
    "jenkins", "gitlab", "github actions", "circleci", "travis",
    "helm", "istio", "rancher", "openshift", "kubectl",
    "vagrant", "packer", "consul", "vault", "nomad",
    "nginx", "apache", "haproxy", "firewall", "iptables", "ufw",
    "ssl", "tls", "certificate", "https", "security",
    "mysql", "postgresql", "mongodb", "redis", "database", "db",
    "git", "svn", "version control", "repository", "commit",
    "monitoring", "logging", "prometheus", "grafana", "elk",
    "network", "dns", "load balancer", "proxy", "vpn",
    "backup", "restore", "snapshot", "volume", "storage",
    "systemd", "service", "daemon", "cron", "systemctl",
    "package", "yum", "apt", "rpm", "dpkg", "install",
    "lvm", "filesystem", "mount", "disk", "partition"
]

# ✅ Chef/Puppet require context keywords
CHEF_TERMS = ["chef recipe", "chef cookbook", "chef resource", "chef file", "chef node"]
PUPPET_TERMS = ["puppet manifest", "puppet module", "puppet class", "puppet agent"]

# ✅ Excluded obvious non-tech words (to avoid false positives)
EXCLUDED_CONTEXT = [
    "food", "cooking", "kitchen", "biryani", "chicken", "mutton", "pasta", "recipe",
    "oil pipeline", "business", "finance", "company fraud", "movie", "song", "music",
    "love", "poem", "poetry", "story", "novel", "romance", "dating",
    "game", "sports", "football", "cricket", "entertainment",
    "health", "medicine", "doctor", "hospital", "treatment",
    "travel", "vacation", "holiday", "tourism", "hotel"
]

def is_allowed_query(query: str) -> bool:
    """
    Strict domain filtering: ONLY allow DevOps/Infra/Cloud/IaC queries.
    Default deny everything else.
    """
    query_lower = query.lower()

    # 🚫 First block obvious nonsense
    if any(bad in query_lower for bad in EXCLUDED_CONTEXT):
        return False

    # ✅ Allow Chef/Puppet in infra context
    if any(term in query_lower for term in CHEF_TERMS + PUPPET_TERMS):
        return True

    # ✅ Allow if contains DevOps/infra keywords
    if any(kw in query_lower for kw in ALLOWED_KEYWORDS):
        return True

    # 🚫 DEFAULT DENY: If no infra keywords found, reject
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
    # ✅ STRICT: Reject non-domain queries
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
