import redis.asyncio as redis
import os
import json
from app.utils import left_to_right_match, try_decode
import asyncio
from dotenv import load_dotenv

from contextlib import asynccontextmanager
load_dotenv()


def get_redis():
    # Create a new Redis connection for the current event loop
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True,
        username="default",
        password=os.getenv("REDIS_PASSWORD")
    )


@asynccontextmanager
async def redis_client():
    r = get_redis()
    try:
        yield r
    finally:
        await r.aclose()

async def run_with_client(redis_func, *args, **kwargs):
    async with redis_client() as r:
        return await redis_func(r, *args, **kwargs)

async def map_names(r, names: list[tuple], prefix: str = "alias"):
    try:
        async with r.pipeline(transaction=True) as pipe:
            for name1, name2 in names:
                name1, name2 = name1.lower(), name2.lower()
                pipe.set(f"{prefix}:{name1}", name2)
                pipe.set(f"{prefix}:{name2}", name1)
            await pipe.execute()
    except Exception as e:
        print(f"Error during mapping: {e}")

async def cache_titles(r, key: str, values: set[str], content_type: str, ttl: int = 60 * 60 * 24 * 7):
    if not values:
        return
    key = f"{content_type}:{key.lower()}"
    try:
        await r.sadd(key, *values)
        if ttl:
            await r.expire(key, ttl)
    except Exception as e:
        print(f"Error caching titles for key {key}: {e}")


async def get_titles(r, key: str, content_type: str) -> set[str]:
    key = f"{content_type}:{key.lower()}"
    try:
        return await r.smembers(key)
    except Exception as e:
        print(f"Error retrieving titles for key {key}: {e}")


async def cache_results(r, results: list[dict], content_type: str, prefix: str = "cache", ttl: int = None):
    if content_type != 'anime' or not results:
        return 
    try:
        async with r.pipeline(transaction=True) as pipeline:
            for result in results:
                redis_key = f"{prefix}:{content_type}_{result['title'].lower()}"
                if result['genres'] and not await r.exists(redis_key):
                    serialized_result = {
                        k: json.dumps(v) if isinstance(v, (list, dict)) else v
                        for k, v in result.items()
                    }
                    await pipeline.hset(redis_key, mapping=serialized_result)
                    if ttl:
                        await pipeline.expire(redis_key, ttl)
                    
            await pipeline.execute()
    except Exception as e:
        print(f"Error during caching: {e}")

async def pipeline_caching(r, keys: list[str], mode: str = 'hash'):
    if not keys:
        return []
    async with r.pipeline(transaction=True) as pipeline:
        for key in keys:
            if mode == "hash":
                await pipeline.hgetall(key)
            else:
                await pipeline.get(key)
        results = await pipeline.execute()
        return results
        
# 0, None, None, None, None
# 0, None, 2, 3
# 0, None, 2

# 1, 2, 3, 4 
# 1, 3, 4 
# 1, 4
    
async def get_cached_results_with_fallback(r, titles: list[str], content_type: str, prefix: str = "cache", alias_prefix: str = "alias"):
    if content_type != 'anime' or not titles:
        return {}
    # Pipeline to get original keys
    redis_keys = [f"{prefix}:{content_type}_{title.lower()}" for title in titles]
    original_results = await pipeline_caching(r, redis_keys)
    missing_indices = [i for i in range(len(original_results)) if not original_results[i]]

    # Get aliases for missing titles
    mapping_keys = [f"{alias_prefix}:{titles[idx].lower()}" for idx in missing_indices]
    mapped_titles = await pipeline_caching(r, mapping_keys, 'string')
    mapped_indices = [missing_indices[i] for i in range(len(mapped_titles)) if mapped_titles[i]]


    # Pipeline to fetch fallback (mapped) keys
    fallback_keys = [f"{prefix}:{content_type}_{title.lower()}" for title in mapped_titles if title]
    fallback_results = await pipeline_caching(r, fallback_keys)
    fallback_map = {mapped_indices[i]: fallback_results[i] for i in range(len(fallback_results)) if fallback_results[i]}
    
    # we could also compute the mapping once at the end, but i like this approach of intermediate mappings between indices
    
    # Merge original and fallback results
    final_results = {}
    for i, title in enumerate(titles):
        if original_results[i]:
            final_results[title] = original_results[i]
        elif i in fallback_map:
            final_results[title] = fallback_map[i]
    
    return final_results



async def clear_cache(r, prefixes: tuple[str] = ("cache", "alias", "series", "anime", "movie")):
    for prefix in prefixes:
        keys = await r.keys(f"{prefix}:*")
        if keys:
            await r.delete(*keys)


async def auto_cleanup(r, prefix: str = "cache", threshold_percent: float = 80, cleanup_percent: float = 20, max_memory: float = 3e7):

    info = await r.info("memory")
    used_memory = info['used_memory']
    usage_ratio = (used_memory / max_memory) * 100
    print(f"Redis Memory Usage: {usage_ratio:.2f}%")

    if usage_ratio >= threshold_percent:
        keys = []
        async for key in r.scan_iter(match=f"{prefix}:*"):
            keys.append(key)

        total_keys = len(keys)
        if total_keys == 0:
            print("No keys found to delete.")
            return

        async with r.pipeline(transaction=True) as pipeline:
            for key in keys:
                await pipeline.object('idletime', key)
            idletimes = await pipeline.execute()

        keys_with_idle = sorted(zip(keys, idletimes), key=lambda x: x[1], reverse=True)
        num_to_delete = int(total_keys * (cleanup_percent / 100))
        keys_to_delete = [k for k, _ in keys_with_idle[:num_to_delete]]

        async with r.pipeline(transaction=True) as pipeline:
            for key in keys_to_delete:
                await pipeline.delete(key)
            await pipeline.execute()

        print(f"🚨 Cleanup triggered: Deleted {num_to_delete}/{total_keys} least-accessed keys in '{prefix}:*'")
    else:
        print("✅ Memory usage under control. No cleanup needed.")

async def get_keys(r, prefix: str):
    keys = []
    async for key in r.scan_iter(match=f"{prefix}:*"):
        keys.append(key)
    return keys
    
if __name__ == '__main__':
    async def main():
        anime_shows = {
            "Attack on Titan",
            "Fullmetal Alchemist: Brotherhood",
            "Death Note",
            "One Piece",
            "Jujutsu Kaisen",
            "My Hero Academia",
            "Demon Slayer",
            "Cowboy Bebop",
            "Hunter x Hunter",
            "Steins;Gate",
            "Naruto",
            "Naruto Shippuden",
        }
        async with redis_client() as r:
            # await clear_cache(r)
            keys = await get_keys(r, "cache")
            print(keys)
            # data = [
            #     {"title": str(i), "genres": ['g1', 'g2'], "age": 30} for i in range(10)
            # ]
            # await cache_results(data, 'anime', prefix="cache")
            # cached = await get_cached_results(r, anime_shows, 'anime')


    asyncio.run(main())
