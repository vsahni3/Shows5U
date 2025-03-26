import unicodedata
import re
import hashlib
import asyncio


def left_to_right_match(str1: str, str2: str) -> float:
    str1, str2 = str1.lower(), str2.lower()
    min_len = min(len(str1), len(str2))
    matches = sum(1 for i in range(min_len) if str1[i] == str2[i])
    return matches / min_len if min_len > 0 else 0.0


def try_decode(value):
    if isinstance(value, str) and (value.startswith('{') or value.startswith('[')):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def to_ascii_safe_id(name: str) -> str:
    # Normalize Unicode
    normalized = unicodedata.normalize('NFKD', name)
    
    # Remove non-ASCII chars
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    
    # Slugify: replace non-alphanumerics with '_'
    slug = re.sub(r'[^a-zA-Z0-9]+', '_', ascii_only).strip('_').lower()
    
    # Fallback if slug is empty (all symbols or empty string)
    if not slug:
        slug = hashlib.md5(name.encode('utf-8')).hexdigest()[:8]
    
    return slug




def run_async_task(coro_func, *args, **kwargs):
    # Create a new event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro_func(*args, **kwargs))
    loop.close()