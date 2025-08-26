
"""
Persona system for DeepShell.

Manages AI personas (roles) that define system prompts and behavior
patterns for different use cases like shell commands, coding, etc.
"""

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from .config import config

console = Console()


class Persona:
    """
    Represents an AI persona with system prompt and metadata.
    
    Personas define the behavior and specialization of the AI assistant
    for different tasks and contexts.
    """
    
    def __init__(
        self,
        name: str,
        prompt: str,
        description: str = "",
        variables: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Initialize persona.
        
        Args:
            name: Persona name/identifier
            prompt: System prompt template
            description: Human-readable description
            variables: Template variables for dynamic substitution
        """
        self.name = name
        self.prompt = prompt
        self.description = description
        self.variables = variables or {}
    
    @property
    def system_prompt(self) -> str:
        """Get system prompt with variables substituted."""
        prompt = self.prompt
        
        # Substitute built-in variables
        built_in_vars = self._get_built_in_variables()
        for key, value in built_in_vars.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        # Substitute custom variables
        for key, value in self.variables.items():
            prompt = prompt.replace(f"{{{key}}}", value)
        
        return prompt
    
    def _get_built_in_variables(self) -> Dict[str, str]:
        """Get built-in template variables."""
        return {
            "os": self._detect_os(),
            "shell": self._detect_shell(),
            "user": os.getenv("USER", "user"),
            "home": os.path.expanduser("~"),
        }
    
    def _detect_os(self) -> str:
        """Detect operating system."""
        os_name = config.get("OS_NAME")
        if os_name != "auto":
            return os_name
        
        system = platform.system().lower()
        if system == "darwin":
            return "macOS"
        elif system == "linux":
            # Try to get distribution info
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=", 1)[1].strip().strip('"')
            except FileNotFoundError:
                pass
            return "Linux"
        elif system == "windows":
            return "Windows"
        else:
            return system.title()
    
    def _detect_shell(self) -> str:
        """Detect current shell."""
        shell_name = config.get("SHELL_NAME")
        if shell_name != "auto":
            return shell_name
        
        # Try to detect from environment
        shell = os.getenv("SHELL", "")
        if shell:
            return os.path.basename(shell)
        
        # Fallback detection
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
        
        return "bash"  # Default fallback
    
    def to_dict(self) -> Dict[str, any]:
        """Convert persona to dictionary for serialization."""
        return {
            "name": self.name,
            "prompt": self.prompt,
            "description": self.description,
            "variables": self.variables,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "Persona":
        """Create persona from dictionary."""
        return cls(
            name=data["name"],
            prompt=data["prompt"],
            description=data.get("description", ""),
            variables=data.get("variables", {}),
        )


class PersonaManager:
    """Manages persona storage and retrieval."""
    
    def __init__(self, storage_path: Path) -> None:
        """
        Initialize persona manager.
        
        Args:
            storage_path: Directory to store persona files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize built-in personas if they don't exist
        self._initialize_built_in_personas()
    
    def _initialize_built_in_personas(self) -> None:
        """Create built-in personas if they don't exist."""
        built_in_personas = {
            "default": Persona(
                name="default",
                prompt="""You are DeepShell, an AI assistant powered by Deepshell LLM.
You are a programming and system administration assistant managing {os} with {shell} shell.

Key guidelines:
- Provide helpful, accurate, and concise responses
- When asked about shell commands, provide working examples
- Apply markdown formatting when appropriate
- Be direct and practical in your assistance
- If you need clarification, ask specific questions

Current environment: {os} with {shell} shell""",
                description="General-purpose AI assistant for programming and system administration"
            ),
            
            "shell": Persona(
                name="shell",
                prompt="""You are a shell command generator for {os} using {shell}.

CRITICAL RULES:
- Provide ONLY shell commands without any description or explanation
- If there is a lack of details, provide the most logical solution
- Ensure the output is a valid shell command that can be executed
- If multiple steps are required, combine them using && or ;
- Do NOT provide markdown formatting such as ```
- Do NOT include any explanatory text
- Respond with raw shell commands only

Operating System: {os}
Shell: {shell}""",
                description="Generates shell commands without explanations"
            ),
            
            "describe-shell": Persona(
                name="describe-shell",
                prompt="""You are a shell command explainer for {os} using {shell}.

Your role:
- Explain what shell commands do in clear, simple terms
- Break down complex commands into understandable parts
- Explain command options and flags
- Provide context about when and why to use commands
- Use markdown formatting for better readability
- Be educational and thorough in explanations

Operating System: {os}
Shell: {shell}""",
                description="Explains shell commands and their functionality"
            ),
            
            "code": Persona(
                name="code",
                prompt="""You are a code generator that provides ONLY code as output.

CRITICAL RULES:
- Provide ONLY code without any description or explanation
- Do NOT include markdown formatting such as ``` or ```python
- Do NOT include comments unless they are part of the functional code
- If there is a lack of details, provide the most logical solution
- You are not allowed to ask for more details
- Respond with raw code only
- Ensure code is syntactically correct and functional

Provide clean, working code without any additional text.""",
                description="Generates code without explanations or formatting"
            ),
            
            "reasoning": Persona(
                name="reasoning",
                prompt="""You are DeepShell in reasoning mode, powered by DeepShell's reasoning capabilities.

Your approach:
- Think through problems step by step
- Show your reasoning process when helpful
- Break down complex problems into smaller parts
- Provide well-reasoned solutions with explanations
- Use the DeepShell reasoning model's capabilities to their fullest
- Apply markdown formatting for clarity

When solving problems:
1. Understand the requirements
2. Consider different approaches
3. Explain your reasoning
4. Provide the solution
5. Mention any assumptions or limitations

Current environment: {os} with {shell} shell""",
                description="Uses step-by-step reasoning for complex problems"
            ),
            
            "coder": Persona(
                name="coder",
                prompt="""You are DeepShell in coding mode, specialized for programming tasks.

Your expertise:
- Write clean, efficient, and well-documented code
- Explain coding concepts and best practices
- Debug and optimize existing code
- Provide code reviews and suggestions
- Support multiple programming languages
- Apply markdown formatting with syntax highlighting

Coding principles:
- Write readable and maintainable code
- Follow language-specific best practices
- Include helpful comments when appropriate
- Consider error handling and edge cases
- Suggest improvements and optimizations

Current environment: {os} with {shell} shell""",
                description="Specialized for programming and software development tasks"
            ),
        }
        
        for persona_name, persona in built_in_personas.items():
            persona_file = self.storage_path / f"{persona_name}.json"
            if not persona_file.exists():
                self.save_persona(persona)
    
    def get_persona_file(self, name: str) -> Path:
        """Get file path for persona."""
        return self.storage_path / f"{name}.json"
    
    def save_persona(self, persona: Persona) -> None:
        """Save persona to file."""
        persona_file = self.get_persona_file(persona.name)
        try:
            with open(persona_file, 'w', encoding='utf-8') as f:
                json.dump(persona.to_dict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            console.print(f"[red]Error saving persona '{persona.name}': {e}[/red]")
    
    def load_persona(self, name: str) -> Optional[Persona]:
        """Load persona from file."""
        persona_file = self.get_persona_file(name)
        
        if not persona_file.exists():
            return None
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Persona.from_dict(data)
        except (IOError, json.JSONDecodeError, KeyError) as e:
            console.print(f"[red]Error loading persona '{name}': {e}[/red]")
            return None
    
    def list_personas(self) -> List[str]:
        """List all available persona names."""
        persona_files = self.storage_path.glob("*.json")
        return sorted([f.stem for f in persona_files])
    
    def delete_persona(self, name: str) -> bool:
        """Delete persona file."""
        persona_file = self.get_persona_file(name)
        
        if not persona_file.exists():
            return False
        
        try:
            persona_file.unlink()
            return True
        except OSError as e:
            console.print(f"[red]Error deleting persona '{name}': {e}[/red]")
            return False


# Global persona manager
_persona_manager: Optional[PersonaManager] = None


def get_persona_manager() -> PersonaManager:
    """Get or create global persona manager."""
    global _persona_manager
    
    if _persona_manager is None:
        _persona_manager = PersonaManager(config.get("PERSONA_STORAGE_PATH"))
    
    return _persona_manager


def get_persona(name: str) -> Persona:
    """Get persona by name, with fallback to default."""
    manager = get_persona_manager()
    persona = manager.load_persona(name)
    
    if persona is None:
        console.print(f"[yellow]Warning: Persona '{name}' not found, using default[/yellow]")
        persona = manager.load_persona("default")
        
        if persona is None:
            # Fallback to minimal default if even default persona is missing
            persona = Persona(
                name="fallback",
                prompt="You are a helpful AI assistant.",
                description="Fallback persona"
            )
    
    return persona


def create_persona(name: str) -> None:
    """Interactive persona creation."""
    manager = get_persona_manager()
    
    # Check if persona already exists
    if manager.get_persona_file(name).exists():
        overwrite = Prompt.ask(
            f"Persona '{name}' already exists. Overwrite?",
            choices=["y", "n"],
            default="n"
        )
        if overwrite.lower() != "y":
            console.print("[yellow]Persona creation cancelled[/yellow]")
            return
    
    console.print(f"\n[bold cyan]Creating persona: {name}[/bold cyan]")
    
    description = Prompt.ask("Description (optional)", default="")
    
    console.print("\nEnter the system prompt (press Ctrl+D when finished):")
    console.print("[dim]Available variables: {os}, {shell}, {user}, {home}[/dim]")
    
    prompt_lines = []
    try:
        while True:
            line = input()
            prompt_lines.append(line)
    except EOFError:
        pass
    
    prompt = "\n".join(prompt_lines).strip()
    
    if not prompt:
        console.print("[red]Error: System prompt cannot be empty[/red]")
        return
    
    # Create and save persona
    persona = Persona(name=name, prompt=prompt, description=description)
    manager.save_persona(persona)
    
    console.print(f"[green]✓ Persona '{name}' created successfully[/green]")


def show_persona(name: str) -> None:
    """Display persona details."""
    persona = get_persona_manager().load_persona(name)
    
    if persona is None:
        console.print(f"[red]Error: Persona '{name}' not found[/red]")
        return
    
    # Create panel with persona details
    content = f"[bold]Description:[/bold] {persona.description or 'No description'}\n\n"
    content += f"[bold]System Prompt:[/bold]\n{persona.prompt}\n\n"
    
    if persona.variables:
        content += f"[bold]Custom Variables:[/bold]\n"
        for key, value in persona.variables.items():
            content += f"  {key}: {value}\n"
    
    panel = Panel(
        content,
        title=f"Persona: {persona.name}",
        border_style="cyan"
    )
    
    console.print(panel)


def list_personas() -> None:
    """Display all available personas."""
    manager = get_persona_manager()
    persona_names = manager.list_personas()
    
    if not persona_names:
        console.print("[yellow]No personas found[/yellow]")
        return
    
    table = Table(title="Available Personas", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    
    for name in persona_names:
        persona = manager.load_persona(name)
        description = persona.description if persona else "Error loading persona"
        table.add_row(name, description)
    
    console.print(table)


def delete_persona(name: str) -> None:
    """Delete a persona."""
    manager = get_persona_manager()
    
    if not manager.get_persona_file(name).exists():
        console.print(f"[red]Error: Persona '{name}' not found[/red]")
        return
    
    # Prevent deletion of built-in personas
    built_in_personas = ["default", "shell", "describe-shell", "code", "reasoning", "coder"]
    if name in built_in_personas:
        console.print(f"[red]Error: Cannot delete built-in persona '{name}'[/red]")
        return
    
    confirm = Prompt.ask(
        f"Are you sure you want to delete persona '{name}'?",
        choices=["y", "n"],
        default="n"
    )
    
    if confirm.lower() == "y":
        if manager.delete_persona(name):
            console.print(f"[green]✓ Persona '{name}' deleted successfully[/green]")
        else:
            console.print(f"[red]Error: Could not delete persona '{name}'[/red]")
    else:
        console.print("[yellow]Deletion cancelled[/yellow]")
