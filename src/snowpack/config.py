"""Configuration loader and toolchain discovery for Snowpack."""

from __future__ import annotations

import os
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any


def find_project_config(start_dir: Path | str | None = None) -> tuple[dict[str, Any], Path | None]:
    """Scans start_dir and parent directories upward for snowpack.toml or pyproject.toml."""
    try:
        cur = Path(start_dir or Path.cwd()).resolve()
    except Exception:
        cur = Path.cwd().resolve()

    while True:
        # 1. Check snowpack.toml or .snowpack.toml
        for candidate_name in ("snowpack.toml", ".snowpack.toml"):
            candidate = cur / candidate_name
            if candidate.is_file():
                try:
                    with candidate.open("rb") as f:
                        data = tomllib.load(f)
                    cfg: dict[str, Any] = {}
                    if isinstance(data, dict):
                        # Merge [project], [general], [tool.snowpack], or flat dict
                        if "project" in data and isinstance(data["project"], dict):
                            cfg.update(data["project"])
                        if "general" in data and isinstance(data["general"], dict):
                            cfg.update(data["general"])
                        if (
                            "tool" in data
                            and isinstance(data["tool"], dict)
                            and "snowpack" in data["tool"]
                            and isinstance(data["tool"]["snowpack"], dict)
                        ):
                            cfg.update(data["tool"]["snowpack"])
                        for k, v in data.items():
                            if k not in ("project", "general", "tool") and not isinstance(v, dict):
                                cfg[k] = v
                    return cfg, candidate
                except Exception:
                    pass

        # 2. Check pyproject.toml
        pyproject = cur / "pyproject.toml"
        if pyproject.is_file():
            try:
                with pyproject.open("rb") as f:
                    data = tomllib.load(f)
                if (
                    isinstance(data, dict)
                    and "tool" in data
                    and isinstance(data["tool"], dict)
                    and "snowpack" in data["tool"]
                    and isinstance(data["tool"]["snowpack"], dict)
                ):
                    return dict(data["tool"]["snowpack"]), pyproject
            except Exception:
                pass

        # Stop if at git boundary or filesystem root
        if (cur / ".git").exists() or cur.parent == cur:
            break
        cur = cur.parent

    return {}, None


def load_resolved_config(start_dir: Path | str | None = None) -> dict[str, Any]:
    """Loads configuration by layered precedence:
    Built-in defaults < User config (~/.config/snowpack/snowpack.toml) < Project config (snowpack.toml / pyproject.toml) < Environment variables.
    """
    cfg: dict[str, Any] = {
        "format": "typ",
        "engine": "typst",
        "preset": "default",
        "theme": "dark",
    }

    # 1. User config (~/.config/snowpack/snowpack.toml)
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg_config) if xdg_config else Path.home() / ".config"
    user_cfg_path = base / "snowpack" / "snowpack.toml"
    if user_cfg_path.is_file():
        try:
            with user_cfg_path.open("rb") as f:
                data = tomllib.load(f)
            user_data = data.get("general", data) if isinstance(data, dict) else {}
            if isinstance(user_data, dict):
                cfg.update(user_data)
                cfg["_user_config"] = str(user_cfg_path)
        except Exception:
            pass

    # 2. Project config (snowpack.toml / pyproject.toml)
    proj_cfg, proj_path = find_project_config(start_dir)
    if proj_path:
        cfg.update(proj_cfg)
        cfg["_project_config"] = str(proj_path)

    # 3. Environment variables take precedence over config file defaults
    env_format = os.environ.get("SNOWPACK_FORMAT") or os.environ.get("SNOWPACK_DEFAULT_FORMAT")
    if env_format:
        cfg["format"] = env_format.strip().lower()

    env_engine = os.environ.get("SNOWPACK_ENGINE") or os.environ.get("SNOWPACK_DEFAULT_ENGINE")
    if env_engine:
        cfg["engine"] = env_engine.strip().lower()

    env_preset = os.environ.get("SNOWPACK_PRESET")
    if env_preset:
        cfg["preset"] = env_preset.strip().lower()

    env_theme = os.environ.get("SNOWPACK_THEME")
    if env_theme:
        cfg["theme"] = env_theme.strip().lower()

    return cfg


def load_user_config(start_dir: Path | str | None = None) -> dict[str, Any]:
    """Loads resolved Snowpack configuration across user, project, and environment levels."""
    return load_resolved_config(start_dir)


def get_tool_version(cmd: str) -> str | None:
    """Returns the first version string from a CLI tool, or None if unavailable."""
    path = shutil.which(cmd)
    if not path:
        return None
    try:
        res = subprocess.run(
            [cmd, "--version"],
            capture_output=True,
            text=True,
            timeout=2.0,
            check=False,
        )
        first_line = (res.stdout or res.stderr).splitlines()
        return first_line[0].strip() if first_line else "available"
    except Exception:
        return "available"


def check_toolchain() -> dict[str, dict[str, Any]]:
    """Checks the availability and version of document compilation backends."""
    tools = ["typst", "tectonic", "pandoc"]
    status: dict[str, dict[str, Any]] = {}
    for tool in tools:
        path = shutil.which(tool)
        version = get_tool_version(tool) if path else None
        status[tool] = {
            "installed": path is not None,
            "path": path,
            "version": version,
        }
    return status
