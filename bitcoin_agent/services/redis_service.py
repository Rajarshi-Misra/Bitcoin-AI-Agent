import redis
import json
from bitcoin_agent.config import settings
from datetime import timedelta
from typing import Optional, Any

class RedisService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    def get(self, key: str) -> Optional[Any]:
        value = self.redis_client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        try:
            self.redis_client.setex(key, timedelta(seconds=expire_seconds), json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        return bool(self.redis_client.delete(key))
    
redis_service = RedisService()