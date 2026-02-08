import hashlib
import re

MAX_FILENAME_LENGTH = 255
EXTENSION = ".pdf"
HASH_LENGTH = 8
SEPARATOR = "__"


def slugify_title(title: str) -> str:
    """Convert a paper title into a lowercase underscore-separated slug."""
    title = title.lower()
    title = re.sub(r"\s+", "_", title)
    title = re.sub(r"[^\w_]", "", title)
    return title


def generate_deterministic_hash(
    conference: str, year: str, title: str, hash_len: int = HASH_LENGTH
) -> str:
    """Generate a deterministic short hash from conference, year, and title."""
    key = f"{conference.lower()}_{year}_{title.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:hash_len]


def generate_safe_filename(
    conference: str, year: str, title: str, extension: str = EXTENSION
) -> str:
    """Generate a safe and deterministic filename within length limits."""
    safe_hash = generate_deterministic_hash(conference, year, title)
    base_slug = slugify_title(title)

    reserved = len(SEPARATOR) + len(safe_hash) + len(extension)
    max_slug_len = MAX_FILENAME_LENGTH - reserved
    truncated_slug = base_slug[:max_slug_len]

    return f"{truncated_slug}{SEPARATOR}{safe_hash}{extension}"
