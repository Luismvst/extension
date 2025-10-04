# src/core/utils/utils.py

from typing import Optional, Iterable

def _csv(value: Optional[Iterable[str] | str]) -> Optional[str]:
    """Convierte listas a CSV; pasa-through si ya es str o None."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return ",".join(map(str, value))

def _bool_to_str(value: Optional[bool]) -> Optional[str]:
    """Convierte bool a 'true'/'false' para query params; None -> None."""
    if value is None:
        return None
    return "true" if value else "false"