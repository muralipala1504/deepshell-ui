"""
Main CLI application for DeepShell.

This module defines the command-line interface using Typer, handling all
user interactions and routing to appropriate handlers.
"""

import sys
from typing import Optional

import typer
from rich.console import Console

from .config import config
from .handlers.chat_handler import ChatHandler
from .handlers.default_handler import DefaultHandler
from .handlers.repl_handler import ReplHandler
from .persona import get_persona, list_personas, create_persona, show_persona
from .utils import (
    get_edited_prompt,
    install_shell_integration,
    detect_stdin,
)

app = typer.Typer(
    name="deepshell",
    help="A command-line productivity tool powered by OpenAI LLMs",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()

@app.command()
def main(
    prompt: str = typer.Argument(
        "",
        show_default=False,
        help="The prompt to generate completions for.",
    ),
    provider: str = typer.Option(
        "openai",
        "--provider",
        help="LLM provider to use (only 'openai' supported).",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use (e.g., gpt-3.5-turbo).",
    ),
    temperature: float = typer.Option(
        0.0,
        "--temperature",
        "-t",
        min=0.0,
        max=2.0,
        help="Randomness of generated output (0.0-2.0).",
    ),
    top_p: float = typer.Option(
        1.0,
        "--top-p",
        min=0.0,
        max=1.0,
        help="Limits highest probable tokens (0.0-1.0).",
    ),
    max_tokens: Optional[int] = typer.Option(
        None,
        "--max-tokens",
        help="Maximum tokens in response.",
    ),
    markdown: bool = typer.Option(
        config.get("PRETTIFY_MARKDOWN") == "true",
        "--md/--no-md",
        help="Enable/disable markdown formatting.",
    ),
    cache: bool = typer.Option(
        True,
        "--cache/--no-cache",
        help="Enable/disable response caching.",
    ),
    stream: bool = typer.Option(
        config.get("DISABLE_STREAMING") != "true",
        "--stream/--no-stream",
        help="Enable/disable streaming responses.",
    ),
    shell: bool = typer.Option(
        False,
        "--shell",
        "-s",
        help="Generate shell commands.",
    ),
    describe_shell: bool = typer.Option(
        False,
        "--describe-shell",
        "-d",
        help="Describe shell commands.",
    ),
    code: bool = typer.Option(
        False,
        "--code",
        "-c",
        help="Generate only code.",
    ),
    interactive: bool = typer.Option(
        config.get("SHELL_INTERACTION") == "true",
        "--interactive/--no-interactive",
        help="Interactive shell command execution.",
    ),
    functions: bool = typer.Option(
        config.get("USE_FUNCTIONS") == "true",
        "--functions/--no-functions",
        help="Enable function calling.",
    ),
    editor: bool = typer.Option(
        False,
        "--editor",
        help="Use $EDITOR for prompt input.",
    ),
    # chat: Optional[str] = typer.Option(
    #     None,
    #     "--chat",
    #     help="Chat session ID ('temp' for temporary).",
    # ),
    # repl: Optional[str] = typer.Option(
    #     None,
    #     "--repl",
    #     help="Start REPL mode with session ID.",
    # ),
    # show_chat: Optional[str] = typer.Option(
    #     None,
    #     "--show-chat",
    #     help="Display chat history.",
    # ),
    # list_chats: bool = typer.Option(
    #     False,
    #     "--list-chats",
    #     "-lc",
    #     help="List all chat sessions.",
    # ),
    persona: Optional[str] = typer.Option(
        None,
        "--persona",
        "-p",
        help="AI persona to use.",
    ),
    create_persona_name: Optional[str] = typer.Option(
        None,
        "--create-persona",
        help="Create new persona.",
    ),
    show_persona_name: Optional[str] = typer.Option(
        None,
        "--show-persona",
        help="Display persona content.",
    ),
    list_personas_flag: bool = typer.Option(
        False,
        "--list-personas",
        "-lp",
        help="List available personas.",
    ),
    install_integration: bool = typer.Option(
        False,
        "--install-integration",
        help="Install shell integration.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information.",
    ),
) -> None:
    """
    DeepShell - AI-powered command-line assistant using OpenAI LLM.

    Examples:
        deepshell --provider openai "list all files in current directory"
        # deepshell --repl coding
        deepshell --persona shell-expert "optimize this command"
    """

    # Handle version flag
    if version:
        from . import __version__
        console.print(f"DeepShell version {__version__}")
        return

    # Handle installation
    if install_integration:
        install_shell_integration()
        return

    # Handle persona management
    if create_persona_name:
        create_persona(create_persona_name)
        return

    if show_persona_name:
        show_persona(show_persona_name)
        return

    if list_personas_flag:
        list_personas()
        return

    # Handle chat management
    # if list_chats:
    #     ChatHandler.list_sessions()
    #     return

    # if show_chat:
    #     ChatHandler.show_session(show_chat)
    #     return

    # Validate provider (only openai supported)
    if provider != "openai":
        console.print("[red]Error: Only 'openai' provider is supported.[/red]")
        raise typer.Exit(1)

    # Determine model - if not specified, use default
    if model is None:
        model = "gpt-3.5-turbo"

    # Validate mutually exclusive options
    mode_options = [shell, describe_shell, code]
    if sum(mode_options) > 1:
        console.print("[red]Error: --shell, --describe-shell, and --code are mutually exclusive[/red]")
        raise typer.Exit(1)

    # Handle input sources
    stdin_content = ""
    if detect_stdin():
        stdin_content = sys.stdin.read().strip()

    if editor and not prompt and not stdin_content:
        prompt = get_edited_prompt()

    # Combine prompt sources
    full_prompt = ""
    if stdin_content:
        full_prompt = stdin_content
        if prompt:
            full_prompt += f"\n\n{prompt}"
    else:
        full_prompt = prompt

    if not full_prompt and not False:  # repl is commented out
        console.print("[red]Error: No prompt provided. Use --help for usage information.[/red]")
        raise typer.Exit(1)

    # Determine persona
    if shell:
        persona_obj = get_persona("shell")
    elif describe_shell:
        persona_obj = get_persona("describe-shell")
    elif code:
        persona_obj = get_persona("code")
    elif persona:
        persona_obj = get_persona(persona)
    else:
        persona_obj = get_persona("default")

    # Create handler options
    handler_options = {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": stream,
        "cache": cache,
        "functions": functions,
        "interactive": interactive and shell,
    }

    # Route to appropriate handler
    try:
        # if repl:
        #     handler = ReplHandler(repl, persona_obj, markdown)
        #     handler.handle(**handler_options)
        # elif chat:
        #     handler = ChatHandler(chat, persona_obj, markdown)
        #     handler.handle(full_prompt, **handler_options)
        # else:
        handler = DefaultHandler(persona_obj, markdown)
        handler.handle(full_prompt, **handler_options)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(130)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and not sys.argv[1].startswith("-") and sys.argv[1] not in app.registered_commands):
        # Insert 'main' as the default command if no command is given
        sys.argv.insert(1, "main")
    app()
