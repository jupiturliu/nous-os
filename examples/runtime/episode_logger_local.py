#!/usr/bin/env python3
"""Local episode logger adapter for the NOUS OS workspace demo."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
NOUS_OS_ROOT = HERE.parent.parent
WORKSPACE = NOUS_OS_ROOT.parent
EPISODES_DIR = NOUS_OS_ROOT / "examples" / "runtime" / "data" / "episodes"
EPISODES_FILE = EPISODES_DIR / "episodes.jsonl"
SQLITE_FILE = EPISODES_DIR / "episodes.sqlite"


def load_episode_module():
    module_path = WORKSPACE / "trustmem" / "tools" / "episode_logger.py"
    tools_dir = str(module_path.parent)
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    spec = importlib.util.spec_from_file_location("workspace_episode_logger", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.EPISODES_DIR = EPISODES_DIR
    module.EPISODES_FILE = EPISODES_FILE
    module._DEFAULT_SQLITE_PATH = str(SQLITE_FILE)
    return module


def main() -> None:
    module = load_episode_module()
    if len(sys.argv) < 2:
        module.main()
        return

    action = sys.argv[1]
    args = {}
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg.startswith("--") and i + 1 < len(sys.argv):
            args[arg[2:]] = sys.argv[i + 1]

    if action == "recall":
        results = module.recall_similar(
            task=args.get("task", ""),
            agent=args.get("agent"),
            top_k=int(args.get("top", 5)),
        )
        payload = [{"episode": episode, "similarity": similarity} for episode, similarity in results]
        print(module.json.dumps(payload, ensure_ascii=False))
        return

    if action == "stats":
        print(module.json.dumps(module.get_stats(agent=args.get("agent")), ensure_ascii=False))
        return

    module.main()


if __name__ == "__main__":
    main()
