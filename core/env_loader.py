"""Load .env from project root (gitignored)."""

from __future__ import annotations

from pathlib import Path


def load_dotenv() -> None:
    try:
        from dotenv import load_dotenv as _load
    except ImportError:
        return
    root = Path(__file__).resolve().parents[1]
    _load(root / ".env")
