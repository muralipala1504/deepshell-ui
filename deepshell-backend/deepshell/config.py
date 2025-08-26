"""
Configuration management for DeepShell.

Handles environment variables, configuration files, and default settings
with a priority system: environment variables > config file > defaults.
Supports OpenAI LLM provider only.
"""

import os
from getpass import getpass
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Dict

from rich.console import Console
from rich.prompt import Prompt

console = Console()

# Configuration paths
CONFIG_FOLDER = os.path.expanduser("~/.config")
DEEPSHELL_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "deepshell"
DEEPSHELL_CONFIG_PATH = DEEPSHELL_CONFIG_FOLDER / ".deepshellrc"
PERSONA_STORAGE_PATH = DEEPSHELL_CONFIG_FOLDER / "personas"
FUNCTIONS_PATH = DEEPSHELL_CONFIG_FOLDER / "functions"
CHAT_CACHE_PATH = Path(gettempdir()) / "deepshell_chat_cache"
CACHE_PATH = Path(gettempdir()) / "deepshell_cache"

# Default configuration
DEFAULT_CONFIG = {
    # Provider Configuration
    "PROVIDER": os.getenv("PROVIDER", "openai"),  # openai only

    # API Keys
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),

    # Model Configuration
    "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo"),
    "API_BASE_URL": os.getenv("API_BASE_URL", ""),
    "USE_LITELLM": os.getenv("USE_LITELLM", "true"),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "60")),

    # Cache Configuration
    "CHAT_CACHE_PATH": os.getenv("CHAT_CACHE_PATH", str(CHAT_CACHE_PATH)),
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CHAT_CACHE_LENGTH": int(os.getenv("CHAT_CACHE_LENGTH", "100")),
    "CACHE_LENGTH": int(os.getenv("CACHE_LENGTH", "100")),
    "ENABLE_CACHE": os.getenv("ENABLE_CACHE", "true"),

    # Display Configuration
    "PRETTIFY_MARKDOWN": os.getenv("PRETTIFY_MARKDOWN", "true"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "cyan"),
    "CODE_THEME": os.getenv("CODE_THEME", "monokai"),
    "DISABLE_STREAMING": os.getenv("DISABLE_STREAMING", "false"),

    # Persona Configuration
    "PERSONA_STORAGE_PATH": os.getenv("PERSONA_STORAGE_PATH", str(PERSONA_STORAGE_PATH)),
    "DEFAULT_PERSONA": os.getenv("DEFAULT_PERSONA", "default"),

    # Function Configuration
    "FUNCTIONS_PATH": os.getenv("FUNCTIONS_PATH", str(FUNCTIONS_PATH)),
    "USE_FUNCTIONS": os.getenv("USE_FUNCTIONS", "true"),
    "SHOW_FUNCTIONS_OUTPUT": os.getenv("SHOW_FUNCTIONS_OUTPUT", "false"),

    # Shell Integration
    "SHELL_INTERACTION": os.getenv("SHELL_INTERACTION", "true"),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    "OS_NAME": os.getenv("OS_NAME", "auto"),
    "SHELL_NAME": os.getenv("SHELL_NAME", "auto"),

    # Advanced Configuration
    "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
    "RETRY_DELAY": float(os.getenv("RETRY_DELAY", "1.0")),
    "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),
}


class Config(dict):
    """Configuration manager with file persistence and environment override."""

    def __init__(self, config_path: Path, **defaults: Any) -> None:
        super().__init__()
        self.config_path = config_path

        # Load configuration with priority: env vars > config file > defaults
        self.update(defaults)

        if self._exists:
            self._read()
            # Add any new default keys that don't exist
            has_new_config = False
            for key, value in defaults.items():
                if key not in self:
                    has_new_config = True
                    self[key] = value
            if has_new_config:
                self._write()
        else:
            # Create config directory and file
            config_path.parent.mkdir(parents=True, exist_ok=True)

            # Prompt for API key if not in environment
            if not self.get("OPENAI_API_KEY"):
                self._prompt_api_key()

            self._write()

    @property
    def _exists(self) -> bool:
        """Check if configuration file exists."""
        return self.config_path.exists()

    def _read(self) -> None:
        """Read configuration from file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')

                        # Convert to appropriate type
                        if value.lower() in ("true", "false"):
                            value = value.lower() == "true"
                        elif value.isdigit():
                            value = int(value)
                        elif value.replace(".", "").isdigit():
                            value = float(value)

                        self[key] = value
        except Exception as e:
            console.print(f"[yellow]Warning: Could not read config file: {e}[/yellow]")

    def _write(self) -> None:
        """Write configuration to file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write("# DeepShell Configuration File\n")
                f.write("# This file is automatically generated and updated\n\n")

                for key, value in sorted(self.items()):
                    if isinstance(value, str) and " " in value:
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f"{key}={value}\n")
        except Exception as e:
            console.print(f"[red]Error: Could not write config file: {e}[/red]")

    def _prompt_api_key(self) -> None:
        """Prompt user for OpenAI API key."""
        console.print("\n[bold cyan]DeepShell Setup[/bold cyan]")
        console.print("To use DeepShell, you need an OpenAI API key.")
        console.print("Get your key from:")
        console.print("  • OpenAI: [link]https://platform.openai.com/account/api-keys[/link]\n")

        openai_key = Prompt.ask("Enter your OpenAI API key (leave blank to skip)", password=True, show_default=False)

        if openai_key:
            self["OPENAI_API_KEY"] = openai_key
            console.print("[green]✓ OpenAI API key saved[/green]")

        if not openai_key:
            console.print("[yellow]Warning: No API key provided. Set your API key in your environment or config file.[/yellow]")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable override."""
        # Environment variables take precedence
        env_value = os.getenv(key)
        if env_value is not None:
            # Convert string environment variables to appropriate types
            if env_value.lower() in ("true", "false"):
                return env_value.lower() == "true"
            elif env_value.isdigit():
                return int(env_value)
            elif env_value.replace(".", "").replace("-", "").isdigit():
                return float(env_value)
            return env_value

        # Fall back to config file or default
        return super().get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and persist to file."""
        self[key] = value
        self._write()

    def validate(self) -> bool:
        """Validate configuration and return True if valid."""
        errors = []

        # Check OpenAI API key
        if not self.get("OPENAI_API_KEY"):
            errors.append("OPENAI_API_KEY is required")

        # Check model name (basic check)
        valid_models = [
            "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini"
        ]
        if self.get("DEFAULT_MODEL") not in valid_models:
            errors.append(f"DEFAULT_MODEL must be one of: {', '.join(valid_models)}")

        # Check numeric values
        try:
            timeout = int(self.get("REQUEST_TIMEOUT"))
            if timeout <= 0:
                errors.append("REQUEST_TIMEOUT must be positive")
        except (ValueError, TypeError):
            errors.append("REQUEST_TIMEOUT must be a valid integer")

        if errors:
            console.print("[red]Configuration errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            return False

        return True


# Global configuration instance
config = Config(DEEPSHELL_CONFIG_PATH, **DEFAULT_CONFIG)


def get_config_info() -> Dict[str, Any]:
    """Get configuration information for debugging."""
    return {
        "config_path": str(config.config_path),
        "config_exists": config._exists,
        "provider": config.get("PROVIDER"),
        "openai_key_set": bool(config.get("OPENAI_API_KEY")),
        "model": config.get("DEFAULT_MODEL"),
        "api_base": config.get("API_BASE_URL"),
        "use_litellm": config.get("USE_LITELLM"),
        "cache_enabled": config.get("ENABLE_CACHE"),
        "streaming_enabled": config.get("DISABLE_STREAMING") != "true",
    }


def reset_config() -> None:
    """Reset configuration to defaults."""
    if config.config_path.exists():
        config.config_path.unlink()

    # Reinitialize with defaults
    config.clear()
    config.update(DEFAULT_CONFIG)
    config._write()

    console.print("[green]✓ Configuration reset to defaults[/green]")
