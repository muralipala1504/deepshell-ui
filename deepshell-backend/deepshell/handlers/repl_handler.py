
"""
REPL handler for interactive command-line sessions.

Provides a Read-Eval-Print Loop interface for continuous interaction
with the AI assistant.
"""

import sys
from typing import Any, Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .chat_handler import ChatHandler
from ..persona import Persona
from ..utils import run_shell_command

console = Console()


class ReplHandler(ChatHandler):
    """
    REPL (Read-Eval-Print Loop) handler for interactive sessions.
    
    Extends ChatHandler to provide an interactive command-line interface
    with special commands and multiline input support.
    """
    
    def __init__(self, session_id: str, persona: Persona, markdown: bool = True) -> None:
        """
        Initialize REPL handler.
        
        Args:
            session_id: Chat session identifier
            persona: AI persona to use
            markdown: Whether to enable markdown formatting
        """
        super().__init__(session_id, persona, markdown)
        
        # REPL-specific state
        self.last_shell_command: Optional[str] = None
        self.multiline_mode = False
        
        # Setup prompt session
        self.prompt_session = PromptSession(
            history=InMemoryHistory(),
            key_bindings=self._create_key_bindings(),
            multiline=False,
        )
    
    def _create_key_bindings(self) -> KeyBindings:
        """Create custom key bindings for REPL."""
        bindings = KeyBindings()
        
        @bindings.add('c-d')  # Ctrl+D
        def _(event):
            """Exit REPL on Ctrl+D."""
            event.app.exit()
        
        @bindings.add('c-c')  # Ctrl+C
        def _(event):
            """Cancel current input on Ctrl+C."""
            event.app.output.write('\n')
            event.app.exit(exception=KeyboardInterrupt)
        
        return bindings
    
    def handle(self, **options) -> None:
        """
        Start REPL session.
        
        Args:
            **options: Handler options (model, temperature, etc.)
        """
        # Validate options once
        validated_options = self.validate_options(**options)
        
        # Display welcome message
        self._show_welcome()
        
        try:
            while True:
                try:
                    # Get user input
                    prompt_text = self._get_prompt_text()
                    user_input = self.prompt_session.prompt(prompt_text)
                    
                    # Handle empty input
                    if not user_input.strip():
                        continue
                    
                    # Handle special commands
                    if self._handle_special_command(user_input, **validated_options):
                        continue
                    
                    # Handle multiline input
                    if user_input == '"""':
                        user_input = self._get_multiline_input()
                        if not user_input:
                            continue
                    
                    # Process normal input
                    self._process_input(user_input, **validated_options)
                
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'exit' or Ctrl+D to quit[/yellow]")
                    continue
                
                except EOFError:
                    break
        
        except Exception as e:
            self.handle_error(e)
        
        finally:
            console.print("\n[dim]Goodbye![/dim]")
    
    def _show_welcome(self) -> None:
        """Display REPL welcome message."""
        welcome_text = f"""[bold cyan]DeepShell REPL[/bold cyan]
Session: {self.session.session_id}
Persona: {self.persona.name}

[dim]Commands:
  exit, quit    - Exit REPL
  clear         - Clear session history
  help          - Show this help
  \"\"\"           - Enter multiline mode
  e             - Execute last shell command (shell persona only)
  d             - Describe last shell command (shell persona only)

Press Ctrl+D to exit, Ctrl+C to cancel input[/dim]
"""
        
        panel = Panel(
            welcome_text,
            title="Welcome to DeepShell REPL",
            border_style="cyan"
        )
        console.print(panel)
    
    def _get_prompt_text(self) -> str:
        """Get prompt text for current state."""
        if self.persona.name == "shell":
            return "🐚 "
        elif self.persona.name == "code" or self.persona.name == "coder":
            return "💻 "
        elif self.persona.name == "reasoning":
            return "🧠 "
        else:
            return "🤖 "
    
    def _get_multiline_input(self) -> str:
        """Get multiline input from user."""
        console.print("[dim]Entering multiline mode. Type '\"\"\"' on a new line to finish.[/dim]")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip() == '"""':
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                console.print("\n[yellow]Multiline input cancelled[/yellow]")
                return ""
        
        return "\n".join(lines)
    
    def _handle_special_command(self, user_input: str, **options) -> bool:
        """
        Handle special REPL commands.
        
        Args:
            user_input: User input to check
            **options: Handler options
            
        Returns:
            True if input was a special command, False otherwise
        """
        command = user_input.strip().lower()
        
        # Exit commands
        if command in ("exit", "quit", "exit()", "quit()"):
            raise EOFError
        
        # Clear session
        elif command == "clear":
            self.session.clear()
            # Re-add system message
            self.session.add_message("system", self.persona.system_prompt)
            console.print("[green]✓ Session history cleared[/green]")
            return True
        
        # Help command
        elif command == "help":
            self._show_help()
            return True
        
        # Execute last shell command (shell persona only)
        elif command == "e" and self.persona.name == "shell":
            if self.last_shell_command:
                try:
                    run_shell_command(self.last_shell_command, interactive=True)
                except Exception as e:
                    console.print(f"[red]Error executing command: {e}[/red]")
            else:
                console.print("[yellow]No shell command to execute[/yellow]")
            return True
        
        # Describe last shell command (shell persona only)
        elif command == "d" and self.persona.name == "shell":
            if self.last_shell_command:
                # Switch to describe-shell persona temporarily
                from ..persona import get_persona
                describe_persona = get_persona("describe-shell")
                
                describe_prompt = f"Explain this shell command: {self.last_shell_command}"
                
                # Create temporary handler for description
                temp_handler = ReplHandler("temp", describe_persona, self.markdown)
                temp_handler._process_input(describe_prompt, **options)
            else:
                console.print("[yellow]No shell command to describe[/yellow]")
            return True
        
        return False
    
    def _show_help(self) -> None:
        """Show REPL help information."""
        help_text = """[bold]DeepShell REPL Commands[/bold]

[cyan]General Commands:[/cyan]
  exit, quit    - Exit the REPL
  clear         - Clear conversation history
  help          - Show this help message
  \"\"\"           - Enter multiline input mode

[cyan]Shell Persona Commands:[/cyan]
  e             - Execute the last generated shell command
  d             - Describe/explain the last generated shell command

[cyan]Input Methods:[/cyan]
  • Single line: Type your prompt and press Enter
  • Multi line: Type '\"\"\"', enter your text, then '\"\"\"' on a new line
  • Cancel: Press Ctrl+C to cancel current input
  • Exit: Press Ctrl+D or type 'exit' to quit

[cyan]Tips:[/cyan]
  • Conversation history is maintained throughout the session
  • Use different personas for specialized tasks
  • Shell commands can be executed directly with 'e' command
"""
        
        panel = Panel(
            help_text,
            title="REPL Help",
            border_style="cyan"
        )
        console.print(panel)
    
    def _process_input(self, user_input: str, **options) -> None:
        """
        Process user input and generate response.
        
        Args:
            user_input: User input to process
            **options: Handler options
        """
        try:
            # Create messages with history
            messages = self.make_messages(user_input)
            
            # Get response
            if options["stream"]:
                # Streaming response
                response_generator = self.get_completion(
                    messages=messages,
                    **options
                )
                
                full_response = self.stream_response(response_generator)
                
                # Add assistant response to session
                self.session.add_message("assistant", full_response)
                
                # Store shell command if applicable
                if self.persona.name == "shell":
                    self.last_shell_command = full_response.strip()
            
            else:
                # Non-streaming response
                response = self.get_completion(
                    messages=messages,
                    **options
                )
                
                content = response.choices[0].message.content
                self.print_response(content)
                
                # Add assistant response to session
                self.session.add_message("assistant", content)
                
                # Store shell command if applicable
                if self.persona.name == "shell":
                    self.last_shell_command = content.strip()
        
        except Exception as e:
            self.handle_error(e)
    
    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create message list including conversation history.
        
        Args:
            prompt: User prompt
            
        Returns:
            List of messages including history and new prompt
        """
        # Add user message to session
        self.session.add_message("user", prompt)
        
        # Return all messages for API call
        return self.session.get_messages()
