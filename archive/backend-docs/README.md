# DeepShell 🐚

## Your AI Second Opinion for the Command Line

Ever wish you could get a second (or third) opinion before running a risky command or deploying a new script?  
DeepShell brings the power of OpenAI’s GPT models right to your terminal.

Don’t just ask one AI—get a smarter, confident answer.  
DeepShell is your trusted assistant for Linux, coding, and automation.

## Features

- 🤖 AI-Powered Assistance: Leverage OpenAI’s advanced language models  
- 🐚 Shell Command Generation: Generate and execute shell commands with AI  
- 🎭 Persona System: Specialized AI behaviors for different tasks  
- ⚡ Streaming Responses: Real-time response generation  
- 💾 Smart Caching: Reduce API costs with intelligent caching  
- 🔧 Function Calling: Extensible tool integration  
- 🎨 Rich Formatting: Beautiful markdown and syntax highlighting

## Why DeepShell?

Just like you’d get a second opinion from another expert before a big decision, DeepShell lets you cross-check your sysadmin moves, scripts, and troubleshooting steps with AI-powered answers.

- Reduce risk by verifying commands before you run them  
- Build confidence in your DevOps and coding work  
- Powered by OpenAI’s reliable GPT models

## Installation

Compatibility: Tested on RHEL 9.6, Ubuntu 22.04, Debian 11, and should work on most major Linux distributions with Docker installed.
### From PyPI (Recommended)

```bash
pip install deepshell

```

From Source

```bash

git clone https://github.com/muralipala1504/deepshell.git
cd deepshell
pip install -e .

```

Quick Start

Get your OpenAI API key.

Set your API key:

```bash

export OPENAI_API_KEY="sk-your-openai-key"

```

Start using DeepShell with prompts:

```bash

deepshell --provider openai "How do I list all files in a directory?"

```
Or simply:

```bash
deepshell "How do I list all files in a directory?"
```
Usage Examples

Shell Command Generation

```bash
deepshell --provider openai --shell "compress all .log files"
```

Personas (Specialized AI Behaviors)

```bash

deepshell --provider openai --persona shell "optimize this command: find . -name '*.py'"

```

Configuration

DeepShell uses a configuration file at ~/.config/deepshell/.deepshellrc:

# Provider Configuration
PROVIDER=openai

# API Key
OPENAI_API_KEY=sk-your-openai-key

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo

# Display Options
PRETTIFY_MARKDOWN=true
DEFAULT_COLOR=cyan
CODE_THEME=monokai
DISABLE_STREAMING=false

# Cache Settings
ENABLE_CACHE=true
CACHE_LENGTH=100
CHAT_CACHE_LENGTH=100

# Advanced Options
REQUEST_TIMEOUT=60
MAX_RETRIES=3
USE_FUNCTIONS=true

Environment Variables

All configuration options can be overridden with environment variables:

```bash

export PROVIDER="openai"
export OPENAI_API_KEY="sk-your-key"
export DEFAULT_MODEL="gpt-3.5-turbo"

```

Supported Models

Model	Notes
        
        gpt-3.5-turbo	Most users, reliable
        gpt-4	Advanced capabilities

Command Reference
Basic Commands

```bash
deepshell [OPTIONS] [PROMPT]
```

Options

Option	Description

    --provider	LLM provider to use (only openai)
    --model, -m	Model to use (see above)
    --temperature, -t	Randomness (0.0-2.0)
    --top-p	Nucleus sampling (0.0-1.0)
    --max-tokens	Maximum response tokens
    --shell, -s	Generate shell commands
    --describe-shell, -d	Describe shell commands
    --code, -c	Generate code only
    --interactive	Interactive shell execution
    --persona, -p	AI persona to use
    --functions	Enable function calling
    --stream/--no-stream	Enable/disable streaming
    --cache/--no-cache	Enable/disable caching
    --md/--no-md	Enable/disable markdown
    --editor	Use $EDITOR for input

Input Methods

DeepShell supports multiple input methods:

```bash

deepshell "your prompt here"
echo "analyze this" | deepshell
deepshell "explain this code" < script.py
deepshell --editor
deepshell <<< "your prompt"

```

Error Handling

DeepShell provides helpful error messages and suggestions:

    API Key Issues: Clear instructions for setting up authentication
    Rate Limits: Automatic retry with exponential backoff
    Network Issues: Connection troubleshooting tips
    Model Errors: Model availability and parameter validation

Performance Tips

    Use Caching: Keep caching enabled for repeated queries
    Choose Right Model: Use gpt-3.5-turbo or gpt-4 for most tasks
    Optimize Prompts: Be specific and clear in your requests
    Batch Operations: Use chat sessions for related queries
    Stream Responses: Enable streaming for better perceived performance


Troubleshooting

Common Issues

API Key Not Found

```bash

export OPENAI_API_KEY="sk-your-key-here"
# or add to ~/.config/deepshell/.deepshellrc

```

Connection Issues

    Check your internet connection
    Verify API endpoint accessibility
    Run deepshell --version to test basic functionality

Cache Issues

```bash

rm -rf ~/.cache/deepshell/

```

Permission Issues

```bash
chmod 755 ~/.config/deepshell/
```

Contributing

    We welcome contributions! Please see our Contributing Guide for details.

```bash

git clone https://github.com/muralipala1504/deepshell.git
cd deepshell
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]

```

Running Tests

```bash

pytest
pytest --cov=deepshell  # With coverage
black deepshell/
isort deepshell/
flake8 deepshell/

```
Docker Usage

    Pull the official DeepShell image from Docker Hub

```bash
docker pull moorelee/deepshell:latest

```
Or build the Docker image locally

```bash

docker build -t deepshell:latest .

```
Run DeepShell with an interactive shell

```bash

docker run -it --rm --entrypoint /bin/bash moorelee/deepshell:latest

```

Inside the container shell

    Set your OpenAI API key:

```bash

export OPENAI_API_KEY="your_api_key_here"

```

Run DeepShell commands:

```bash

deepshell "your prompt here"

```

Optional: Persist logs or config

```bash

docker run -it --rm -e OPENAI_API_KEY="your_api_key_here" -v /path/on/host:/app/logs moorelee/deepshell:latest "your prompt"

```

License

MIT License - see LICENSE file for details.

    Changelog

    See CHANGELOG.md for version history and updates.

Support

    🐛 Bug Reports: GitHub Issues
    💬 Discussions: GitHub Discussions
    📧 Email: muralipala1504@gmail.com

Acknowledgments

    Inspired by Shell GPT for natural language shell command generation.
    Powered by OpenAI
    Built with LiteLLM
    CLI framework: Typer
    Rich formatting: Rich



Sponsor / Support

    If you find DeepShell helpful and want to support its ongoing development, consider becoming a sponsor! Your support helps improve features, maintain hosting costs, and fuel innovation.

    Buy Me a Coffee: https://buymeacoffee.com/muralipala
    
    Patreon: https://www.patreon.com/TheDeepShellForge
    
    GitHub Sponsors: https://github.com/sponsors/muralipala1504


Thank you for your support! 🙌

