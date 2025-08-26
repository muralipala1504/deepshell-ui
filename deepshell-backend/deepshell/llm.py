"""
OpenAI LLM client integration using LiteLLM.

This module provides a unified interface for interacting with OpenAI language models.
"""

import json
import os
import time
from typing import Any, Dict, Generator, List, Optional, Union
from abc import ABC, abstractmethod

import litellm
from litellm import completion
from rich.console import Console

from .config import config

console = Console()

# Configure LiteLLM
litellm.suppress_debug_info = True
litellm.drop_params = True  # Drop unsupported parameters


class MockResponse:
    """Mock response object for error handling."""
    def __init__(self, content: str):
        self.choices = [MockChoice(content)]

class MockChoice:
    """Mock choice object for error handling."""
    def __init__(self, content: str):
        self.message = MockMessage(content)

class MockMessage:
    """Mock message object for error handling."""
    def __init__(self, content: str):
        self.content = content


class BaseLLMClient(ABC):
    """Base class for all LLM clients."""

    def __init__(self, api_key: Optional[str] = None, timeout: int = 60, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = 1.0

    @abstractmethod
    def get_model_prefix(self) -> str:
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        pass

    def validate_model(self, model: str) -> bool:
        available_models = self.get_available_models()
        return model in available_models

    def _create_error_response(self, error_message: str) -> Any:
        return MockResponse(f"❌ Error: {error_message}")

    def _retry_with_backoff(self, func, *args, **kwargs) -> Any:
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if result is None:
                    raise ValueError("API returned None response")
                if isinstance(result, bool):
                    raise ValueError(f"API returned boolean: {result}")
                if not kwargs.get('stream', False):
                    if not hasattr(result, 'choices'):
                        raise ValueError("API response missing 'choices' attribute")
                    if not result.choices:
                        raise ValueError("API response has empty choices")
                return result
            except Exception as e:
                last_exception = e
                console.print(f"DEBUG: Exception in attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries:
                    break
                delay = self.retry_delay * (2 ** attempt)
                console.print(f"[yellow]Retry {attempt + 1}/{self.max_retries} in {delay:.1f}s...[/yellow]")
                time.sleep(delay)
        console.print(f"DEBUG: All retries failed, raising: {str(last_exception)}")
        return self._create_error_response(str(last_exception))

    def complete(
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
        model_name = model or self.get_default_model()
        valid_keys = {
            "model", "messages", "temperature", "top_p", "stream", "timeout", "max_tokens", "tools", "tool_choice"
        }
        completion_kwargs = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "stream": stream,
            "timeout": self.timeout,
        }
        if max_tokens is not None:
            completion_kwargs["max_tokens"] = max_tokens
        if functions:
            completion_kwargs["tools"] = [
                {"type": "function", "function": func} for func in functions
            ]
            completion_kwargs["tool_choice"] = "auto"
        for k, v in kwargs.items():
            if k in valid_keys:
                completion_kwargs[k] = v
        if stream:
            return self._stream_completion(**completion_kwargs)
        else:
            return self._retry_with_backoff(completion, **completion_kwargs)

    def _stream_completion(self, **kwargs) -> Generator[str, None, None]:
        try:
            stream = self._retry_with_backoff(completion, **kwargs)
            if not hasattr(stream, '__iter__'):
                yield f"❌ Streaming Error: {getattr(stream, 'content', str(stream))}"
                return
            for chunk in stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                    elif hasattr(delta, 'tool_calls') and delta.tool_calls:
                        for tool_call in delta.tool_calls:
                            if tool_call.function.name:
                                yield f"\n🔧 Calling function: {tool_call.function.name}\n"
        except Exception as e:
            console.print(f"[red]Streaming error: {str(e)}[/red]")
            yield f"❌ Streaming Error: {str(e)}"

    def chat(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Union[str, Generator[str, None, None]]:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.complete(messages, **kwargs)
            if kwargs.get("stream", False):
                return response
            else:
                if not response or not hasattr(response, 'choices'):
                    return self._create_error_response("Invalid API response structure")
                if not response.choices:
                    return self._create_error_response("Empty choices in API response")
                if not hasattr(response.choices[0], 'message'):
                    return self._create_error_response("Invalid message structure in API response")
                if not hasattr(response.choices[0].message, 'content'):
                    return self._create_error_response("No content in API response message")
                return response
        except Exception as e:
            console.print(f"[red]Chat error: {str(e)}[/red]")
            return self._create_error_response(f"Chat failed: {str(e)}")

    def test_connection(self) -> bool:
        try:
            response = self.complete(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            if not response or not hasattr(response, 'choices') or not response.choices:
                return False
            if not hasattr(response.choices[0], 'message') or not response.choices[0].message:
                return False
            return bool(response.choices[0].message.content)
        except Exception as e:
            console.print(f"[red]Connection test failed: {str(e)}[/red]")
            return False


class OpenAIClient(BaseLLMClient):
    """OpenAI LLM client."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self.api_key = api_key or config.get("OPENAI_API_KEY")
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment "
                "variable or provide api_key parameter."
            )

    def get_model_prefix(self) -> str:
        return "openai/"

    def get_available_models(self) -> List[str]:
        return [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ]

    def get_default_model(self) -> str:
        return "gpt-3.5-turbo"


# Provider registry (OpenAI only)
PROVIDERS = {
    "openai": OpenAIClient,
}


def get_client(provider: Optional[str] = None) -> BaseLLMClient:
    """Get LLM client for OpenAI."""
    provider_name = provider or config.get("PROVIDER", "openai")
    if provider_name != "openai":
        raise ValueError("Only 'openai' provider is supported in this version.")
    client_class = PROVIDERS[provider_name]
    return client_class(
        timeout=config.get("REQUEST_TIMEOUT", 60),
        max_retries=config.get("MAX_RETRIES", 3),
    )


def get_available_providers() -> List[str]:
    """Get list of available providers (OpenAI only)."""
    return ["openai"]


def validate_provider(provider: str) -> bool:
    """Validate if provider is available (OpenAI only)."""
    return provider == "openai"


# Global client instance
_client: Optional[BaseLLMClient] = None
_current_provider: Optional[str] = None


def get_global_client(provider: Optional[str] = None) -> BaseLLMClient:
    """Get or create global client instance."""
    global _client, _current_provider
    provider_name = provider or config.get("PROVIDER", "openai")
    if provider_name != "openai":
        raise ValueError("Only 'openai' provider is supported in this version.")
    if _client is None or _current_provider != provider_name:
        _client = get_client(provider_name)
        _current_provider = provider_name
    return _client


def reset_client() -> None:
    """Reset global client instance."""
    global _client, _current_provider
    _client = None
    _current_provider = None
