from redis import Redis, ConnectionError


class DummyRedis:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, name, value, **kwargs):
        self.cache[name] = value

    def delete(self, key):
        self.cache.pop(key, None)


try:
    redis_client = Redis(host='localhost', port=6379, decode_responses=True)
    # Test connection
    redis_client.ping()
except (ConnectionError, ConnectionRefusedError):
    print("Redis not available, using in-memory cache instead")
    redis_client = DummyRedis()
