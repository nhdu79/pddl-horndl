"""Locate the external tools used by the pipeline.

Each tool is resolved in this order of priority:

1. an explicit path given on the command line,
2. the ``[tools]`` table of a TOML config file (``tools.toml`` at the repo
   root by default; see ``tools.example.toml``),
3. a lookup of the tool's usual executable names on ``PATH``.

An explicit path (1 or 2) that does not exist is an error rather than a silent
fall-through, so a typo in the config does not quietly pick up another binary.
"""

import shutil
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "tools.toml"

# Config key -> (human-readable name, executable names tried on PATH)
TOOLS = {
    "clipper": ("Clipper", ["clipper.sh", "clipper"]),
    "nmo": ("Nemo", ["nmo"]),
    "val": ("VAL Parser", ["Parser"]),
}


def load_config(path=None) -> dict:
    """Return the [tools] table of the config file, or {} if there is none.

    A missing default config is fine; a missing explicitly given one is not.
    """
    config_path = Path(path) if path else DEFAULT_CONFIG
    if not config_path.exists():
        if path:
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return {}
    with open(config_path, "rb") as f:
        tools = tomllib.load(f).get("tools", {})
    unknown = set(tools) - set(TOOLS)
    if unknown:
        raise ValueError(
            f"Unknown tool(s) {sorted(unknown)} in {config_path}; "
            f"expected any of {sorted(TOOLS)}"
        )
    return tools


def find_tool(key, cli_value=None, config=None):
    """Return the path of tool *key*, or None if it cannot be found.

    *config* is the dict returned by load_config(); it is loaded from the
    default location when omitted.
    """
    name, executables = TOOLS[key]
    if config is None:
        config = load_config()
    for source, value in (("command line", cli_value), ("config", config.get(key))):
        if value:
            path = Path(value).expanduser()
            if not path.exists():
                raise FileNotFoundError(f"{name} path from {source} does not exist: {path}")
            return str(path)
    for exe in executables:
        found = shutil.which(exe)
        if found:
            return found
    return None


def require_tool(key, cli_value=None, config=None):
    """Like find_tool(), but raise with a helpful message if nothing is found."""
    path = find_tool(key, cli_value, config)
    if path is None:
        name, executables = TOOLS[key]
        raise FileNotFoundError(
            f"{name} not found. Pass its path on the command line, set "
            f"'{key} = \"...\"' under [tools] in {DEFAULT_CONFIG.name}, or put "
            f"{' / '.join(executables)} on PATH."
        )
    return path
