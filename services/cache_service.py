from functools import lru_cache
from typing import Optional, Dict, Any
import hashlib
from datetime import datetime, timedelta
import threading

class CacheService:
    def __init__(self):
        """Initialize the cache service with in-memory cache"""
        # In-memory cache with thread safety
        self._cache = {}
        self._lock = threading.Lock()
        
        # Default expiry time (1 hour)
        self.default_expiry = 3600  # seconds
        
    def _generate_key(self, prefix: str, data: str) -> str:
        """Generate a unique cache key"""
        # Create a hash of the data to ensure consistent keys
        data_hash = hashlib.md5(data.encode()).hexdigest()
        return f"{prefix}:{data_hash}"
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a cache entry is expired"""
        return datetime.now() > timestamp + timedelta(seconds=self.default_expiry)
    
    @lru_cache(maxsize=1000)
    def get_cached_analysis(self, text: str) -> Optional[Dict]:
        """Get cached analysis results"""
        cache_key = self._generate_key("analysis", text)
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if not self._is_expired(entry['timestamp']):
                    return entry['data']
                else:
                    del self._cache[cache_key]
            
        return None
    
    def cache_analysis(self, text: str, analysis: Dict):
        """Cache analysis results"""
        cache_key = self._generate_key("analysis", text)
        
        with self._lock:
            self._cache[cache_key] = {
                'data': analysis,
                'timestamp': datetime.now()
            }
        
        # Update LRU cache
        self.get_cached_analysis.cache_clear()  # Clear old cache
        self.get_cached_analysis(text)  # Add to cache
    
    @lru_cache(maxsize=1000)
    def get_cached_evaluation(self, eval_key: str) -> Optional[Dict]:
        """Get cached evaluation results"""
        cache_key = self._generate_key("evaluation", eval_key)
        
        with self._lock:
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if not self._is_expired(entry['timestamp']):
                    return entry['data']
                else:
                    del self._cache[cache_key]
            
        return None
    
    def cache_evaluation(self, eval_key: str, evaluation: Dict):
        """Cache evaluation results"""
        cache_key = self._generate_key("evaluation", eval_key)
        
        with self._lock:
            self._cache[cache_key] = {
                'data': evaluation,
                'timestamp': datetime.now()
            }
        
        # Update LRU cache
        self.get_cached_evaluation.cache_clear()  # Clear old cache
        self.get_cached_evaluation(eval_key)  # Add to cache
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            current_time = datetime.now()
            expired_count = sum(
                1 for entry in self._cache.values()
                if self._is_expired(entry['timestamp'])
            )
            
            return {
                "cache_size": len(self._cache),
                "expired_entries": expired_count,
                "lru_cache_size": self.get_cached_analysis.cache_info().currsize,
                "lru_cache_hits": self.get_cached_analysis.cache_info().hits,
                "lru_cache_misses": self.get_cached_analysis.cache_info().misses
            }
    
    def clear_cache(self, prefix: Optional[str] = None):
        """Clear cache entries"""
        with self._lock:
            if prefix:
                # Clear specific prefix
                keys_to_delete = [
                    key for key in self._cache.keys()
                    if key.startswith(f"{prefix}:")
                ]
                for key in keys_to_delete:
                    del self._cache[key]
            else:
                # Clear all cache
                self._cache.clear()
        
        # Clear LRU cache
        self.get_cached_analysis.cache_clear()
        self.get_cached_evaluation.cache_clear() 