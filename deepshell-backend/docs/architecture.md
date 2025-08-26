
# DeepShell Architecture Documentation

## Overview

DeepShell is a command-line productivity tool that leverages DeepSeek's language models to provide AI-powered assistance for shell commands, code generation, and general queries. This document outlines the system architecture, design patterns, and implementation details.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DeepShell CLI                            │
├─────────────────────────────────────────────────────────────┤
│  Entry Points: deepshell, ds                               │
│  CLI Framework: Typer                                      │
│  Main Module: deepshell.cli                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Handler System                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐ │
│  │ DefaultHandler  │ │  ChatHandler    │ │ ReplHandler   │ │
│  │ Single Q&A      │ │ Persistent      │ │ Interactive   │ │
│  │                 │ │ Conversations   │ │ REPL Mode     │ │
│  └─────────────────┘ └─────────────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Core Components                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ LLM Client  │ │ Persona     │ │ Cache       │ │ Config  │ │
│  │ DeepSeek    │ │ System      │ │ System      │ │ Manager │ │
│  │ Integration │ │             │ │             │ │         │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                External Dependencies                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ LiteLLM     │ │ Rich        │ │ Typer       │ │ Others  │ │
│  │ API Client  │ │ Formatting  │ │ CLI         │ │         │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   DeepSeek API                              │
├─────────────────────────────────────────────────────────────┤
│  Models: deepseek-chat, deepseek-reasoner, deepseek-coder  │
│  Endpoint: https://api.deepseek.com                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Design Patterns

### 1. Handler Pattern

The handler pattern is the central architectural pattern in DeepShell, providing different interaction modes:

```python
class BaseHandler:
    """Base class for all interaction handlers"""
    
    def __init__(self, persona: Persona, markdown: bool = True):
        self.persona = persona
        self.markdown = markdown
        self.client = get_client()
    
    def handle(self, prompt: str, **options) -> None:
        """Main entry point for handling requests"""
        raise NotImplementedError
    
    def make_messages(self, prompt: str) -> List[Dict[str, str]]:
        """Create message list for API call"""
        raise NotImplementedError
```

**Handler Types:**
- **DefaultHandler**: Single prompt/response interactions
- **ChatHandler**: Persistent conversation sessions with history
- **ReplHandler**: Interactive REPL mode extending ChatHandler

### 2. Persona System

Personas define AI behavior and specialization:

```python
class Persona:
    """Represents an AI persona with system prompt and metadata"""
    
    def __init__(self, name: str, prompt: str, description: str = ""):
        self.name = name
        self.prompt = prompt  # System prompt template
        self.description = description
    
    @property
    def system_prompt(self) -> str:
        """Get system prompt with variables substituted"""
        # Substitute {os}, {shell}, {user}, etc.
        return self._substitute_variables(self.prompt)
```

**Built-in Personas:**
- `default`: General-purpose assistant
- `shell`: Shell command generation
- `describe-shell`: Command explanation
- `code`: Code generation
- `reasoning`: Step-by-step problem solving
- `coder`: Programming assistance

### 3. Configuration Management

Hierarchical configuration with environment variable override:

```python
class Config(dict):
    """Configuration with env override and file persistence"""
    
    def get(self, key: str, default: Any = None) -> Any:
        # Priority: env vars > config file > defaults
        env_value = os.getenv(key)
        if env_value is not None:
            return self._convert_type(env_value)
        return super().get(key, default)
```

**Configuration Sources (Priority Order):**
1. Environment variables
2. Configuration file (`~/.config/deepshell/.deepshellrc`)
3. Default values

### 4. Caching System

Decorator-based caching with LRU eviction:

```python
@cache_response
def get_completion(self, messages, **kwargs):
    """Cached API completion method"""
    return self.client.complete(messages=messages, **kwargs)
```

**Cache Features:**
- MD5-based cache keys
- File-based storage
- LRU eviction policy
- Configurable size limits
- Automatic cleanup

### 5. LLM Client Abstraction

Unified interface for DeepSeek API access:

```python
class DeepSeekClient:
    """DeepSeek LLM client with streaming and error handling"""
    
    def complete(self, messages, **kwargs):
        """Generate completion with retry logic"""
        return self._retry_with_backoff(
            lambda: completion(model=f"deepseek/{model}", messages=messages, **kwargs)
        )
```

## Module Structure

### Core Modules

```
deepshell/
├── __init__.py          # Package initialization and exports
├── __main__.py          # Module execution entry point
├── cli.py               # Main CLI application (Typer-based)
├── config.py            # Configuration management
├── llm.py               # DeepSeek LLM client integration
├── persona.py           # Persona system implementation
├── cache.py             # Caching system
├── utils.py             # Utility functions
└── handlers/            # Handler implementations
    ├── __init__.py
    ├── base_handler.py  # Base handler class
    ├── default_handler.py
    ├── chat_handler.py
    └── repl_handler.py
```

### Handler System Details

#### BaseHandler

Provides common functionality:
- API communication
- Response formatting
- Error handling
- Option validation
- Streaming support

#### DefaultHandler

Simplest handler for one-shot interactions:
```python
def make_messages(self, prompt: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": self.persona.system_prompt},
        {"role": "user", "content": prompt}
    ]
```

#### ChatHandler

Manages persistent conversations:
- Session storage in JSON files
- Message history truncation
- Conversation continuity
- Session management commands

#### ReplHandler

Interactive REPL extending ChatHandler:
- Prompt toolkit integration
- Special commands (`exit`, `clear`, `help`, `e`, `d`)
- Multiline input support
- Key bindings (Ctrl+D, Ctrl+C)

## Data Flow

### 1. Request Processing Flow

```
User Input → CLI Parser → Handler Selection → Message Creation → API Call → Response Processing → Output
```

**Detailed Steps:**
1. **CLI Parsing**: Typer parses command-line arguments and options
2. **Handler Selection**: Based on mode (default, chat, repl)
3. **Persona Loading**: Load appropriate AI persona
4. **Message Creation**: Format messages for API call
5. **API Communication**: Send request to DeepSeek via LiteLLM
6. **Response Processing**: Handle streaming/non-streaming responses
7. **Output Formatting**: Apply markdown/syntax highlighting
8. **Display**: Present results to user

### 2. Configuration Loading Flow

```
Environment Variables → Configuration File → Default Values → Merged Configuration
```

### 3. Caching Flow

```
Request → Cache Key Generation → Cache Lookup → [Hit: Return Cached] / [Miss: API Call → Cache Store] → Response
```

## API Integration

### LiteLLM Integration

DeepShell uses LiteLLM for unified API access:

```python
import litellm
from litellm import completion

# Configure LiteLLM
litellm.suppress_debug_info = True
litellm.drop_params = True

# API call
response = completion(
    model="deepseek/deepseek-chat",
    messages=messages,
    stream=True,
    **kwargs
)
```

**Benefits of LiteLLM:**
- Unified API across providers
- Automatic parameter handling
- Built-in retry logic
- Streaming support
- Error normalization

### DeepSeek Models

| Model | Use Case | Context | Max Output |
|-------|----------|---------|------------|
| `deepseek-chat` | General conversation | 64K | 8K |
| `deepseek-reasoner` | Complex reasoning | 64K | 64K |
| `deepseek-coder` | Code generation | 64K | 8K |

### Error Handling Strategy

```python
def _retry_with_backoff(self, func, *args, **kwargs):
    """Exponential backoff retry logic"""
    for attempt in range(self.max_retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == self.max_retries:
                raise e
            delay = self.retry_delay * (2 ** attempt)
            time.sleep(delay)
```

## Storage and Persistence

### Configuration Storage

- **Location**: `~/.config/deepshell/.deepshellrc`
- **Format**: Key-value pairs (INI-style)
- **Encoding**: UTF-8

### Persona Storage

- **Location**: `~/.config/deepshell/personas/`
- **Format**: JSON files
- **Naming**: `{persona_name}.json`

### Chat Session Storage

- **Location**: `/tmp/deepshell_chat_cache/`
- **Format**: JSON files with message arrays
- **Naming**: `{session_id}.json`

### Cache Storage

- **Location**: `/tmp/deepshell_cache/`
- **Format**: Plain text files
- **Naming**: `{md5_hash}.cache`

## Security Considerations

### API Key Management

- Environment variables preferred over config files
- Config file permissions: 600 (user read/write only)
- No API key logging or display
- Secure prompt for initial setup

### Input Validation

- Command injection prevention in shell execution
- Parameter validation and sanitization
- Safe file path handling
- Timeout limits for external commands

### Data Privacy

- Local storage of conversations (user control)
- No telemetry or usage tracking
- Temporary session support
- Cache cleanup mechanisms

## Performance Optimizations

### Caching Strategy

- Response caching with configurable TTL
- LRU eviction policy
- Cache size limits
- Selective caching (skip function calls, streaming)

### Streaming Implementation

- Real-time response display
- Chunked processing
- Interrupt handling
- Progress indicators

### Memory Management

- Message history truncation
- Lazy loading of personas
- Efficient JSON serialization
- Resource cleanup

## Extension Points

### Custom Personas

Users can create custom personas:
```bash
deepshell --create-persona myexpert
```

### Function Calling

Extensible function system (future enhancement):
```python
class CustomFunction(BaseModel):
    def execute(self, **kwargs) -> str:
        # Custom function implementation
        pass
```

### Shell Integration

Hotkey integration for shell environments:
```bash
deepshell --install-integration
```

## Testing Strategy

### Unit Tests

- Handler functionality
- Configuration management
- Persona system
- Cache operations
- Utility functions

### Integration Tests

- API communication
- End-to-end workflows
- Error handling
- Configuration loading

### Performance Tests

- Response time benchmarks
- Memory usage profiling
- Cache effectiveness
- Concurrent request handling

## Deployment and Distribution

### Package Structure

- PyPI distribution via setuptools
- Entry points for CLI commands
- Dependency management
- Version pinning

### Installation Methods

1. **PyPI**: `pip install deepshell`
2. **Source**: `pip install -e .`
3. **Development**: `pip install -e ".[dev]"`

### Platform Support

- Linux (primary)
- macOS (supported)
- Windows (basic support)
- Python 3.8+ requirement

## Future Enhancements

### Planned Features

1. **Function Calling**: Extensible tool integration
2. **Plugin System**: Third-party extensions
3. **Web Interface**: Browser-based UI
4. **Team Features**: Shared personas and sessions
5. **Advanced Caching**: Semantic similarity caching
6. **Multi-model Support**: Provider switching
7. **Voice Interface**: Speech-to-text integration

### Architecture Evolution

- Microservice decomposition for web features
- Database backend for enterprise features
- API server mode for team collaboration
- Plugin architecture for extensibility

## Conclusion

DeepShell's architecture emphasizes:

- **Modularity**: Clear separation of concerns
- **Extensibility**: Easy to add new features
- **Performance**: Efficient caching and streaming
- **Usability**: Rich CLI experience
- **Reliability**: Robust error handling and retry logic

The design enables both simple one-shot queries and complex interactive workflows while maintaining excellent performance and user experience.
