import re
from datetime import datetime
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def is_email(e: str) -> bool:
    if not e:
        return False
    return re.match(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", e.strip()) is not None


def parse_date(d: str):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(d, fmt)
        except Exception:
            pass
    return None
