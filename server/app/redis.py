import redis
import os
import json
from dotenv import load_dotenv
load_dotenv()

# Redis connection
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
    username="default",
    password=os.getenv("REDIS_PASSWORD")
)

def try_decode(value):
    """Attempt to decode a JSON string; return original value if decoding fails."""
    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value

def cache_results(results: list[dict], content_type: str, prefix: str = "cache", ttl: int = None):
    """
    Caches a list of dictionaries in Redis using a pipeline.
    Automatically serializes lists/dicts to JSON strings using dict comprehension.
    """
    pipeline = r.pipeline()

    for result in results:
        redis_key = f"{prefix}:{content_type}_{result['title']}"
        if result['genres'] and not r.exists(redis_key):
            # Serialize with dict comprehension
            serialized_result = {
                k: json.dumps(v) if isinstance(v, (list, dict)) else v
                for k, v in result.items()
            }
            pipeline.hset(redis_key, mapping=serialized_result)
            if ttl:
                pipeline.expire(redis_key, ttl)
    
    pipeline.execute()
    

def get_cached_results(titles: set[str], content_type: str, prefix: str = "cache"):
    """
    Retrieves multiple cached dictionaries from Redis using a pipeline and automatically
    unserializes JSON strings back into Python objects using a dict comprehension.
    
    :param titles: List of titles (unique identifiers) to fetch.
    :param prefix: Prefix for Redis keys.
    :return: A list of retrieved dictionaries (empty dicts are filtered out).
    """
    redis_keys = [f"{prefix}:{content_type}_{title}" for title in titles]
    pipeline = r.pipeline()

    # Queue hgetall for each key
    for key in redis_keys:
        pipeline.hgetall(key)
    
    # Execute all batched hgetall commands
    results = pipeline.execute()
    
    # Use dict comprehension to unserialize each field if possible
    final_results = [
        {k: try_decode(v) for k, v in res.items()}
        for res in results if res
    ]
    
    return final_results

def clear_cache(prefix: str = "cache"):
    """
    Clears all cached entries from Redis with the specified prefix.
    
    :param prefix: The prefix used for keys to delete (e.g., 'user').
    """
    pattern = f"{prefix}:*"
    keys = r.keys(pattern)
    
    if keys:
        r.delete(*keys)
        
        
        
def auto_cleanup(prefix: str = "cache", threshold_percent: float = 80, cleanup_percent: float = 20, max_memory: float = 3e7):
    """
    Deletes least-accessed keys (by IDLETIME) when Redis memory exceeds threshold.

    :param prefix: The prefix/namespace for keys to delete (e.g., "cache:*").
    :param threshold_percent: Trigger cleanup if Redis usage exceeds this %.
    :param cleanup_percent: The % of keys to delete (based on least accessed).
    """
    info = r.info("memory")
    used_memory = info['used_memory']


    
    usage_ratio = (used_memory / max_memory) * 100
    print(f"Redis Memory Usage: {usage_ratio:.2f}%")

    if usage_ratio >= threshold_percent:
        keys = list(r.scan_iter(match=f"{prefix}:*"))
        total_keys = len(keys)

        if total_keys == 0:
            print("No keys found to delete.")
            return

        # Pipeline to get IDLETIME for each key
        pipeline = r.pipeline()
        for key in keys:
            pipeline.object('idletime', key)
        idletimes = pipeline.execute()

        # Pair keys with their idletime and sort by idletime descending (least used = longest idle)
        keys_with_idle = sorted(zip(keys, idletimes), key=lambda x: x[1], reverse=True)

        # Select the least accessed keys
        num_to_delete = int(total_keys * (cleanup_percent / 100))
        keys_to_delete = [k for k, idle in keys_with_idle[:num_to_delete]]

        # Bulk delete using pipeline
        pipeline = r.pipeline()
        for key in keys_to_delete:
            pipeline.delete(key)
        pipeline.execute()

        print(f"🚨 Cleanup triggered: Deleted {num_to_delete}/{total_keys} least-accessed keys in '{prefix}:*'")
    else:
        print("✅ Memory usage under control. No cleanup needed.")
# check size of one result
# let evictions happen, if slow then we can dleete oruselves using above func
# if redis storage not sufficient, we will keep it, but add postgres anyways as step 2 its not either or


if __name__ == '__main__':
    clear_cache()
    auto_cleanup()
    data = [
        {"title": str(i), "genres": ['g1', 'g2'], "age": 30} for i in range(1000)
    ] 


    cache_results(data, 'anime', prefix="cache")  
    auto_cleanup()

    print(get_cached_results([str(i) for i in range(0, 50, 2)], 'anime'))
