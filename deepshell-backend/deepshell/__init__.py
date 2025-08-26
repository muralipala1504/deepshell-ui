
"""
DeepShell - A command-line productivity tool powered by OpenAI LLM

DeepShell is a Shell GPT-inspired CLI tool that leverages OpenAI's powerful
language models to provide AI-powered assistance for shell commands, code
generation, and general queries.

Key Features:
- Shell command generation and explanation
- Interactive chat sessions
- REPL mode for continuous interaction
- Role-based AI personas
- Function calling capabilities
- Streaming responses
- Comprehensive caching system
"""

__version__ = "1.0.0"
__author__ = "DeepShell Team"
__email__ = "muralipala1504@gmail.com"
__license__ = "MIT"

from .cli import app
from .config import config

__all__ = ["app", "config",  "__version__"]
