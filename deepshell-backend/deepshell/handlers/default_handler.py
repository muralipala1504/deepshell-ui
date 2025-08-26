"""
Default handler for single prompt/response interactions.

Handles one-shot queries without conversation history or persistence.
"""

from typing import Any, Dict, List

from rich.console import Console

from .base_handler import BaseHandler
from ..persona import Persona
from ..llm import get_global_client

console = Console()


class DefaultHandler(BaseHandler):
    """
    Handler for single prompt/response interactions.

    This is the simplest handler that processes a single prompt and
    returns a response without maintaining conversation history.
    """

    def __init__(self, persona: Persona, markdown: bool = True) -> None:
        """
        Initialize default handler.

        Args:
            persona: AI persona to use
            markdown: Whether to enable markdown formatting
        """
        super().__init__(persona, markdown)

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create message list for single interaction.

        Args:
            prompt: User prompt

        Returns:
            List containing system message and user prompt
        """
        messages = [
            {"role": "system", "content": self.persona.system_prompt},
            {"role": "user", "content": prompt}
        ]

        return messages

    def get_completion(self, messages, provider=None, **options):
        """
        Get completion from the selected LLM provider.
        """
        # Debug print to see what's being sent
        #console.print(f"[dim]DEBUG: Provider={provider}, Model={options.get('model')}, Stream={options.get('stream')}[/dim]")

        client = get_global_client(provider)
        return client.complete(messages, **options)

    def handle(self, prompt: str, provider=None, **options) -> None:
        """
        Handle single prompt/response interaction.

        Args:
            prompt: User prompt to process
            provider: LLM provider to use (openai)
            **options: Handler options (model, temperature, etc.)
        """
        if not prompt.strip():
            console.print("[red]Error: Empty prompt provided[/red]")
            return

        try:
            # Validate options
            validated_options = self.validate_options(**options)

            # Create messages
            messages = self.make_messages(prompt)

            # Get response
            if validated_options["stream"]:
                # Streaming response
                response_generator = self.get_completion(
                    messages=messages,
                    provider=provider,
                    **validated_options
                )

                # Check if response_generator is actually iterable
                if not hasattr(response_generator, '__iter__'):
                    console.print(f"[red]Error: Expected streaming response, got: {type(response_generator)}[/red]")
                    return

                full_response = self.stream_response(response_generator)

                # Handle shell command execution if requested
                if validated_options.get("interactive", False):
                    self._handle_shell_interaction(full_response)

            else:
                # Non-streaming response
                response = self.get_completion(
                    messages=messages,
                    provider=provider,
                    **validated_options
                )

                # Defensive: check for response structure
                if not response:
                    console.print("[red]Error: No response from LLM[/red]")
                    return

                # Check if it's a MockResponse (error case)
                if hasattr(response, 'choices') and hasattr(response.choices[0], 'message'):
                    if hasattr(response.choices[0].message, 'content'):
                        content = response.choices[0].message.content

                        # Check if it's an error message
                        if content.startswith("❌ Error:"):
                            console.print(f"[red]{content}[/red]")
                            return

                        self.print_response(content)

                        # Handle shell command execution if requested
                        if validated_options.get("interactive", False):
                            self._handle_shell_interaction(content)
                    else:
                        console.print("[red]Error: No content in response message[/red]")
                        return
                else:
                    console.print(f"[red]Error: Invalid response structure: {type(response)}[/red]")
                    return

        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")

        except Exception as e:
            console.print(f"[red]Handler Error: {str(e)}[/red]")
            self.handle_error(e)

    def _handle_shell_interaction(self, response: str) -> None:
        """
        Handle interactive shell command execution.

        Args:
            response: AI response containing potential shell commands
        """
        # Only handle shell interaction for shell persona
        if self.persona.name != "shell":
            return

        # Extract potential shell command (simple heuristic)
        command = response.strip()

        # Skip if response doesn't look like a shell command
        if not command or "\n" in command or len(command) > 200:
            return

        from ..utils import run_shell_command

        try:
            run_shell_command(command, interactive=True)
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
