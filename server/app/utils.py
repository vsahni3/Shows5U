import unicodedata
import re
import hashlib

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
