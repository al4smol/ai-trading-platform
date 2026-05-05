"""Compatibility package shim for config modules."""

from pathlib import Path

# Allow importing submodules via `app.config.*` while keeping this file.
__path__ = [str(Path(__file__).with_name("config"))]
