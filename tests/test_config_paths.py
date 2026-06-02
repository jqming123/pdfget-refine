"""Tests for cache and output path defaults."""

from pathlib import Path

from pdfget.config import DEFAULT_OUTPUT_DIR, get_cache_dir


def test_get_cache_dir_env_override(monkeypatch, tmp_path):
    """PDFGET_CACHE_DIR should override the default cache directory."""
    monkeypatch.setenv("PDFGET_CACHE_DIR", str(tmp_path))
    assert get_cache_dir() == tmp_path


def test_get_cache_dir_defaults_to_home(monkeypatch, tmp_path):
    """Default cache directory should follow ~/.cache/pdfget."""
    monkeypatch.delenv("PDFGET_CACHE_DIR", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert get_cache_dir() == Path(tmp_path) / ".cache" / "pdfget"


def test_default_output_dir_is_relative():
    """Default output dir should be a relative path."""
    assert DEFAULT_OUTPUT_DIR == "pdfs"
    assert not Path(DEFAULT_OUTPUT_DIR).is_absolute()
