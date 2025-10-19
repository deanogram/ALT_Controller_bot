"""Bot package public interface."""

from typing import TYPE_CHECKING

__all__ = ["main"]

if TYPE_CHECKING:  # pragma: no cover - for type checkers only
    from .main import main as main


def main(*args, **kwargs):
    """Lazy import for the :mod:`alt_controller_bot.bot.main` entrypoint."""
    from .main import main as _main

    return _main(*args, **kwargs)
