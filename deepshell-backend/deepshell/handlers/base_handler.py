"""
Base handler class for DeepShell interaction modes.

Provides common functionality for API communication, caching,
function calling, and response processing.
"""

import json
from typing import Any, Dict, Generator, List, Optional, Union

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text

from ..cache import cache_response
from ..config import config
from ..llm import get_client
from ..persona import Persona

console = Console()


class BaseHandler:
    """
    Base class for all interaction handlers.

    Provides common functionality for API communication, response formatting,
    caching, and function calling support.
    """

    def __init__(self, persona: Persona, markdown: bool = True) -> None:
        """
        Initialize base handler.

        Args:
            persona: AI persona to use
            markdown: Whether to enable markdown formatting
        """
        self.persona = persona
        self.markdown = markdown and "APPLY MARKDOWN" in persona.system_prompt
        self.client = get_client()

        # Display configuration
        self.color = config.get("DEFAULT_COLOR")
        self.code_theme = config.get("CODE_THEME")

    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        """
        Create message list for API call.

        Args:
            prompt: User prompt

        Returns:
            List of message dictionaries
        """
        raise NotImplementedError("Subclasses must implement make_messages")

    @cache_response
    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.0,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Union[Any, Generator[str, None, None]]:
        """
        Get completion from OpenAI API with caching.

        Args:
            messages: Message history
            model: Model to use
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response
            functions: Function definitions
            **kwargs: Additional parameters

        Returns:
            Completion response or generator for streaming
        """
        return self.client.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stream=stream,
            functions=functions,
            **kwargs
        )

    def handle_function_call(
        self,
        messages: List[Dict[str, Any]],
        function_name: str,
        function_args: str
    ) -> Generator[str, None, None]:
        """
        Handle function call execution.

        Args:
            messages: Current message history
            function_name: Name of function to call
            function_args: Function arguments as JSON string

        Yields:
            Function call status and results
        """
        # Add function call to messages
        messages.append({
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": function_args
                }
            }]
        })

        yield f"\n🔧 Calling function: {function_name}\n"

        try:
            # Parse function arguments
            args = json.loads(function_args)
            args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
            yield f"Arguments: {args_str}\n\n"

            # Execute function (placeholder - would need actual function registry)
            result = f"Function {function_name} executed successfully"

            # Add function result to messages
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": "call_1"  # Would be generated in real implementation
            })

            yield f"Result: {result}\n\n"

        except json.JSONDecodeError as e:
            error_msg = f"Error parsing function arguments: {e}"
            yield f"❌ {error_msg}\n\n"

            messages.append({
                "role": "tool",
                "content": error_msg,
                "tool_call_id": "call_1"
            })

        except Exception as e:
            error_msg = f"Error executing function: {e}"
            yield f"❌ {error_msg}\n\n"

            messages.append({
                "role": "tool",
                "content": error_msg,
                "tool_call_id": "call_1"
            })

    def format_response(self, content: str) -> Union[Markdown, Syntax, Text]:
        """
        Format response content for display.

        Args:
            content: Raw response content

        Returns:
            Formatted content for Rich display
        """
        if self.markdown:
            return Markdown(content)
        else:
            return Text(content, style=self.color)

    def stream_response(
        self,
        response_generator: Generator[str, None, None],
        show_cursor: bool = True
    ) -> str:
        """
        Display streaming response with live updates.

        Args:
            response_generator: Generator yielding response chunks
            show_cursor: Whether to show typing cursor

        Returns:
            Complete response text
        """
        full_response = ""

        with Live(console=console, refresh_per_second=10) as live:
            for chunk in response_generator:
                full_response += chunk

                # Format and display current response
                if self.markdown:
                    display_content = Markdown(full_response)
                else:
                    display_content = Text(full_response, style=self.color)

                if show_cursor:
                    # Add typing cursor
                    cursor = Text("▋", style="bold white")
                    if isinstance(display_content, Text):
                        display_content.append(cursor)
                    else:
                        # For Markdown, we'll add cursor as separate element
                        live.update(display_content)
                        continue

                live.update(display_content)

        return full_response

    def print_response(self, content: str) -> None:
        """
        Print formatted response.

        Args:
            content: Response content to print
        """
        formatted_content = self.format_response(content)
        console.print(formatted_content)

    def handle_error(self, error: Exception) -> None:
        """
        Handle and display errors.

        Args:
            error: Exception that occurred
        """
        error_msg = str(error)

        # Provide helpful error messages for common issues
        if "api key" in error_msg.lower():
            console.print("[red]❌ API Key Error[/red]")
            console.print("Please check your OpenAI API key configuration.")
            console.print("Set OPENAI_API_KEY environment variable or run 'deepshell --help' for setup instructions.")

        elif "rate limit" in error_msg.lower():
            console.print("[red]❌ Rate Limit Exceeded[/red]")
            console.print("Please wait a moment before making another request.")

        elif "timeout" in error_msg.lower():
            console.print("[red]❌ Request Timeout[/red]")
            console.print("The request took too long. Try again or check your connection.")

        elif "connection" in error_msg.lower():
            console.print("[red]❌ Connection Error[/red]")
            console.print("Could not connect to OpenAI API. Check your internet connection.")

        else:
            console.print(f"[red]❌ Error: {error_msg}[/red]")

    def validate_options(self, **options) -> Dict[str, Any]:
        """
        Validate and normalize handler options.

        Args:
            **options: Handler options to validate

        Returns:
            Validated options dictionary
        """
        validated = {}

        # Model validation
        model = options.get("model", config.get("DEFAULT_MODEL"))
        if not self.client.validate_model(model):
            console.print(f"[yellow]Warning: Unknown model '{model}', using default[/yellow]")
            model = config.get("DEFAULT_MODEL")
        validated["model"] = model

        # Temperature validation
        temperature = options.get("temperature", 0.0)
        if not 0.0 <= temperature <= 2.0:
            console.print(f"[yellow]Warning: Temperature {temperature} out of range, clamping to 0.0-2.0[/yellow]")
            temperature = max(0.0, min(2.0, temperature))
        validated["temperature"] = temperature

        # Top-p validation
        top_p = options.get("top_p", 1.0)
        if not 0.0 <= top_p <= 1.0:
            console.print(f"[yellow]Warning: top_p {top_p} out of range, clamping to 0.0-1.0[/yellow]")
            top_p = max(0.0, min(1.0, top_p))
        validated["top_p"] = top_p

        # Max tokens validation
        max_tokens = options.get("max_tokens")
        if max_tokens is not None and max_tokens <= 0:
            console.print(f"[yellow]Warning: max_tokens must be positive, ignoring[/yellow]")
            max_tokens = None
        validated["max_tokens"] = max_tokens

        # Boolean options
        validated["stream"] = bool(options.get("stream", True))
        validated["cache"] = bool(options.get("cache", True))

        funcs = options.get("functions")
        if funcs is None or isinstance(funcs, list):
            validated["functions"] = funcs
        else:
            # Defensive fallback
            validated["functions"] = None

        return validated
