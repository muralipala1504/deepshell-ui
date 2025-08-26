
"""
Caching system for DeepShell responses.

Provides decorator-based caching with configurable size limits and
automatic cleanup for improved performance and reduced API costs.
"""

import hashlib
import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from rich.console import Console

from .config import config

console = Console()

F = TypeVar('F', bound=Callable[..., Any])


class Cache:
    """
    File-based cache with LRU eviction and size management.
    
    Stores cached responses as individual files with MD5 hash keys
    and maintains access times for LRU cleanup.
    """
    
    def __init__(self, max_size: int, cache_dir: Union[str, Path]) -> None:
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of cached items
            cache_dir: Directory to store cache files
        """
        self.max_size = max_size
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Metadata file to track access times
        self.metadata_file = self.cache_dir / ".cache_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, float]:
        """Load cache metadata (access times)."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f)
        except IOError as e:
            console.print(f"[yellow]Warning: Could not save cache metadata: {e}[/yellow]")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        # Create a stable string representation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode('utf-8')).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for key."""
        return self.cache_dir / f"{key}.cache"
    
    def _cleanup_old_entries(self) -> None:
        """Remove oldest entries if cache exceeds max size."""
        if len(self.metadata) <= self.max_size:
            return
        
        # Sort by access time (oldest first)
        sorted_items = sorted(self.metadata.items(), key=lambda x: x[1])
        items_to_remove = len(sorted_items) - self.max_size
        
        for key, _ in sorted_items[:items_to_remove]:
            cache_file = self._get_cache_file(key)
            try:
                if cache_file.exists():
                    cache_file.unlink()
                del self.metadata[key]
            except (OSError, KeyError) as e:
                console.print(f"[yellow]Warning: Could not remove cache entry {key}: {e}[/yellow]")
        
        self._save_metadata()
    
    def get(self, key: str) -> Optional[str]:
        """Get cached value by key."""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update access time
            self.metadata[key] = time.time()
            self._save_metadata()
            
            return content
        
        except (IOError, UnicodeDecodeError) as e:
            console.print(f"[yellow]Warning: Could not read cache file {key}: {e}[/yellow]")
            return None
    
    def set(self, key: str, value: str) -> None:
        """Set cached value for key."""
        cache_file = self._get_cache_file(key)
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(value)
            
            # Update metadata
            self.metadata[key] = time.time()
            self._cleanup_old_entries()
            self._save_metadata()
        
        except IOError as e:
            console.print(f"[yellow]Warning: Could not write cache file {key}: {e}[/yellow]")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        try:
            for cache_file in self.cache_dir.glob("*.cache"):
                cache_file.unlink()
            
            self.metadata.clear()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
        
        except OSError as e:
            console.print(f"[yellow]Warning: Could not clear cache: {e}[/yellow]")
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.metadata)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        return {
            "entries": len(self.metadata),
            "max_entries": self.max_size,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir),
        }


# Global cache instance
_cache: Optional[Cache] = None


def get_cache() -> Cache:
    """Get or create global cache instance."""
    global _cache
    
    if _cache is None:
        _cache = Cache(
            max_size=config.get("CACHE_LENGTH"),
            cache_dir=config.get("CACHE_PATH")
        )
    
    return _cache


def cache_response(func: F) -> F:
    """
    Decorator to cache function responses.
    
    Only caches if caching is enabled in configuration.
    Skips caching for functions that use function calling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Skip caching if disabled
        if config.get("ENABLE_CACHE") != "true":
            return func(*args, **kwargs)
        
        # Skip caching if function calling is involved
        if kwargs.get("functions") or kwargs.get("tools"):
            return func(*args, **kwargs)
        
        # Skip caching for streaming responses
        if kwargs.get("stream", False):
            return func(*args, **kwargs)
        
        cache = get_cache()
        
        # Generate cache key (skip 'self' parameter if present)
        cache_args = args[1:] if args and hasattr(args[0], '__dict__') else args
        cache_key = cache._generate_key(*cache_args, **kwargs)
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            try:
                # Deserialize cached result
                return json.loads(cached_result)
            except json.JSONDecodeError:
                # If deserialization fails, treat as cache miss
                pass
        
        # Execute function and cache result
        result = func(*args, **kwargs)
        
        # Cache the result
        try:
            serialized_result = json.dumps(result, default=str)
            cache.set(cache_key, serialized_result)
        except (TypeError, ValueError) as e:
            console.print(f"[yellow]Warning: Could not cache result: {e}[/yellow]")
        
        return result
    
    return wrapper


def clear_cache() -> None:
    """Clear all cached responses."""
    cache = get_cache()
    cache.clear()
    console.print("[green]✓ Cache cleared successfully[/green]")


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    cache = get_cache()
    return cache.stats()


def print_cache_stats() -> None:
    """Print cache statistics in a readable format."""
    stats = cache_stats()
    
    console.print("\n[bold cyan]Cache Statistics[/bold cyan]")
    console.print(f"Entries: {stats['entries']}/{stats['max_entries']}")
    console.print(f"Total Size: {stats['total_size_mb']} MB")
    console.print(f"Cache Directory: {stats['cache_dir']}")
