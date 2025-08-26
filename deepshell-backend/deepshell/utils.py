"""
Utility functions for DeepShell.

Provides helper functions for shell integration, file operations,
input handling, and system detection.
"""

import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax

console = Console()


def detect_stdin() -> bool:
    """
    Detect if there's input available on stdin.

    Returns:
        True if stdin has data available
    """
    return not sys.stdin.isatty()


def get_edited_prompt() -> str:
    """
    Open user's preferred editor for prompt input.

    Returns:
        Content from editor
    """
    editor = os.getenv("EDITOR", "nano")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False) as f:
        temp_file = f.name

    try:
        # Open editor
        subprocess.run([editor, temp_file], check=True)

        # Read content
        with open(temp_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        return content

    except subprocess.CalledProcessError:
        console.print(f"[red]Error: Could not open editor '{editor}'[/red]")
        return ""

    except FileNotFoundError:
        console.print(f"[red]Error: Editor '{editor}' not found[/red]")
        return ""

    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file)
        except OSError:
            pass


def run_shell_command(command: str, interactive: bool = False) -> Optional[str]:
    """
    Execute shell command with optional interactive confirmation.

    Args:
        command: Shell command to execute
        interactive: Whether to prompt for confirmation

    Returns:
        Command output if successful, None otherwise
    """
    if not command.strip():
        return None

    # Display command with syntax highlighting
    syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
    console.print("\n[bold]Generated Command:[/bold]")
    console.print(syntax)

    if interactive:
        # Interactive confirmation
        console.print("\n[bold]Options:[/bold]")
        console.print("  [green]e[/green] - Execute command")
        console.print("  [yellow]m[/yellow] - Modify command")
        console.print("  [blue]d[/blue] - Describe command")
        console.print("  [red]a[/red] - Abort")

        choice = Prompt.ask(
            "Choose action",
            choices=["e", "m", "d", "a"],
            default="e"
        )

        if choice == "a":
            console.print("[yellow]Command execution aborted[/yellow]")
            return None

        elif choice == "m":
            # Allow user to modify command
            modified_command = Prompt.ask("Enter modified command", default=command)
            return run_shell_command(modified_command, interactive=True)

        elif choice == "d":
            # Describe command using describe-shell persona
            from .persona import get_persona
            from .handlers.default_handler import DefaultHandler

            describe_persona = get_persona("describe-shell")
            handler = DefaultHandler(describe_persona, markdown=True)
            handler.handle(f"Explain this command: {command}")

            # Ask again after description
            return run_shell_command(command, interactive=True)

    # Execute command
    try:
        console.print(f"\n[dim]Executing: {command}[/dim]")

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.stdout:
            console.print("\n[bold green]Output:[/bold green]")
            console.print(result.stdout)

        if result.stderr:
            console.print("\n[bold red]Error:[/bold red]")
            console.print(result.stderr)

        if result.returncode != 0:
            console.print(f"\n[red]Command failed with exit code {result.returncode}[/red]")
        else:
            console.print("\n[green]✓ Command executed successfully[/green]")

        return result.stdout

    except subprocess.TimeoutExpired:
        console.print("\n[red]Command timed out after 30 seconds[/red]")
        return None

    except Exception as e:
        console.print(f"\n[red]Error executing command: {e}[/red]")
        return None


def install_shell_integration() -> None:
    """Install shell integration for hotkey access."""
    shell = detect_shell()
    home = Path.home()

    console.print(f"[cyan]Installing shell integration for {shell}...[/cyan]")

    if shell == "bash":
        rc_file = home / ".bashrc"
        integration_code = '''
# DeepShell integration
function ds_suggest() {
    local cmd=$(deepshell --shell "$@")
    if [ -n "$cmd" ]; then
        echo "$cmd"
        read -p "Execute? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            eval "$cmd"
        fi
    fi
}

# Bind Ctrl+G to DeepShell suggestion
bind -x '"\\C-g":"ds_suggest"'
'''

    elif shell == "zsh":
        rc_file = home / ".zshrc"
        integration_code = '''
# DeepShell integration
function ds_suggest() {
    local cmd=$(deepshell --shell "$@")
    if [ -n "$cmd" ]; then
        echo "$cmd"
        read "reply?Execute? (y/N): "
        if [[ $reply =~ ^[Yy]$ ]]; then
            eval "$cmd"
        fi
    fi
}

# Bind Ctrl+G to DeepShell suggestion
bindkey -s '^G' 'ds_suggest '
'''

    else:
        console.print(f"[yellow]Shell integration not available for {shell}[/yellow]")
        return

    # Check if integration already exists
    if rc_file.exists():
        content = rc_file.read_text()
        if "DeepShell integration" in content:
            console.print("[yellow]Shell integration already installed[/yellow]")
            return

    # Add integration
    try:
        with open(rc_file, "a", encoding="utf-8") as f:
            f.write(integration_code)

        console.print(f"[green]✓ Shell integration added to {rc_file}[/green]")
        console.print("[dim]Restart your shell or run 'source ~/.bashrc' (or ~/.zshrc) to activate[/dim]")
        console.print("[dim]Use Ctrl+G to trigger DeepShell suggestions[/dim]")

    except IOError as e:
        console.print(f"[red]Error installing shell integration: {e}[/red]")


def detect_shell() -> str:
    """
    Detect current shell.

    Returns:
        Shell name (bash, zsh, fish, etc.)
    """
    # Try environment variable first
    shell = os.getenv("SHELL", "")
    if shell:
        return os.path.basename(shell)

    # Try parent process detection
    try:
        result = subprocess.run(
            ["ps", "-p", str(os.getppid()), "-o", "comm="],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Default fallback
    return "bash"


def detect_os() -> str:
    """
    Detect operating system with detailed information.

    Returns:
        OS name and version
    """
    system = platform.system()

    if system == "Darwin":
        version = platform.mac_ver()[0]
        return f"macOS {version}"

    elif system == "Linux":
        try:
            # Try to get distribution info
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=", 1)[1].strip().strip('"')
        except FileNotFoundError:
            pass

        # Fallback to generic Linux
        return f"Linux {platform.release()}"

    elif system == "Windows":
        version = platform.version()
        return f"Windows {version}"

    else:
        return f"{system} {platform.release()}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_api_key(api_key: str) -> bool:
    """
    Validate OpenAI API key format.

    Args:
        api_key: API key to validate

    Returns:
        True if format appears valid
    """
    if not api_key:
        return False

    # OpenAI API keys typically start with 'sk-'
    if not api_key.startswith("sk-"):
        return False

    # Should be reasonably long
    if len(api_key) < 20:
        return False

    return True


def get_system_info() -> dict:
    """
    Get comprehensive system information.

    Returns:
        Dictionary with system details
    """
    return {
        "os": detect_os(),
        "shell": detect_shell(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor() or "Unknown",
        "user": os.getenv("USER", os.getenv("USERNAME", "Unknown")),
        "home": str(Path.home()),
        "cwd": str(Path.cwd()),
    }


def print_system_info() -> None:
    """Print system information in a formatted table."""
    from rich.table import Table

    info = get_system_info()

    table = Table(title="System Information", show_header=True, header_style="bold cyan")
    table.add_column("Property", style="green")
    table.add_column("Value", style="white")

    for key, value in info.items():
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)
