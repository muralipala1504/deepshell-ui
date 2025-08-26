
"""
Entry point for running DeepShell as a module.

Usage:
    python -m deepshell [OPTIONS] [PROMPT]
"""

from .cli import app

if __name__ == "__main__":
    app()
