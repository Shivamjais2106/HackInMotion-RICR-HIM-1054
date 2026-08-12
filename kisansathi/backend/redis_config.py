"""
Redis Configuration and Utilities
"""

import redis
import json
import logging
from datetime import timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisManager:
    """Manage Redis connections and caching"""
    
    def __init__(self, host='localhost', port=6379, db=0, decode_responses=True):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis connected: {host}:{port}")
            self.connected = True
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Using fallback mode.")
            self.redis_client = None
            self.connected = False
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in Redis with expiration"""
        if not self.connected:
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.redis_client.setex(key, expire, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        if not self.connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                try:
                    return json.loads(value)
                except:
                    return value
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.connected:
            return False
        
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Redis CLEAR_PATTERN error: {e}")
            return 0
    
    def flush_all(self) -> bool:
        """Clear all Redis data"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.flushall()
            logger.info("Redis cache cleared")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSH error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get Redis statistics"""
        if not self.connected:
            return {'status': 'disconnected'}
        
        try:
            info = self.redis_client.info()
            return {
                'status': 'connected',
                'used_memory': info.get('used_memory_human', 'N/A'),
                'connected_clients': info.get('connected_clients', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace': info.get('db0', {})
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {'status': 'error', 'error': str(e)}

# Global Redis instance
redis_manager = None

def init_redis(host='localhost', port=6379, db=0):
    """Initialize global Redis manager"""
    global redis_manager
    redis_manager = RedisManager(host=host, port=port, db=db)
    return redis_manager

def get_redis() -> Optional[RedisManager]:
    """Get Redis manager instance"""
    return redis_manager
