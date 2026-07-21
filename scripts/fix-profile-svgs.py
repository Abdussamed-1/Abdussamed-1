#!/usr/bin/env python3
"""Make github-readme-stats SVGs visible on GitHub (Camo freezes CSS animations)."""

from __future__ import annotations

import re
from pathlib import Path


STATS_FILES = ("github-stats.svg", "top-langs.svg")


def fix_stats_svg(path: Path) -> None:
    """Fix cards that hide content behind opacity:0 + CSS animations."""
    text = path.read_text(encoding="utf-8")

    text = re.sub(
        r"\.stagger\s*\{[^}]*\}",
        ".stagger { opacity: 1; }",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"\.rank-text\s*\{[^}]*\}",
        ".rank-text { font: 800 24px 'Segoe UI', Ubuntu, Sans-Serif; fill: #e6edf3; }",
        text,
        flags=re.S,
    )

    match = re.search(
        r"@keyframes rankAnimation\s*\{.*?to\s*\{\s*stroke-dashoffset:\s*([0-9.]+);",
        text,
        re.S,
    )
    if match:
        final = match.group(1)

        def repl(mm: re.Match[str]) -> str:
            body = re.sub(r"animation:[^;]+;", "", mm.group(1))
            return f".rank-circle {{{body} stroke-dashoffset: {final}; }}"

        text = re.sub(r"\.rank-circle\s*\{([^}]*)\}", repl, text, count=1, flags=re.S)

    # Remove only CSS animation hooks; keep geometry intact
    text = re.sub(r"(?m)^\s*animation:[^;]+;\s*$", "", text)
    text = re.sub(r"\sanimation:[^;{]+;", "", text)
    text = re.sub(r"@keyframes\s+\w+\s*\{(?:[^{}]|\{[^{}]*\})*\}", "", text)

    path.write_text(text.lstrip(), encoding="utf-8", newline="\n")
    print(f"fixed {path.name} size={path.stat().st_size}")


def fix_streak_svg(path: Path) -> None:
    """Streak cards hide text behind delayed CSS animations."""
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    # Drop keyframes entirely
    text = re.sub(r"@keyframes\s+\w+\s*\{(?:[^{}]|\{[^{}]*\})*\}", "", text)
    # Inline styles: keep opacity visible, drop animation hooks
    text = re.sub(
        r"style='([^']*)'",
        lambda m: "style='"
        + re.sub(r"\s*animation:[^;']*;?", "", m.group(1)).strip()
        + (" opacity: 1" if "opacity" not in m.group(1) else "")
        + "'",
        text,
    )
    text = re.sub(r"opacity\s*:\s*0(?!\.\d)", "opacity: 1", text)
    text = re.sub(r"style='\s*'", "", text)
    text = re.sub(r"style='(\s*opacity:\s*1)\s*'", r"style='\1'", text)
    path.write_text(text.lstrip(), encoding="utf-8", newline="\n")
    print(f"fixed {path.name} size={path.stat().st_size}")


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "profile"
    for name in STATS_FILES:
        path = root / name
        if path.exists():
            fix_stats_svg(path)
    fix_streak_svg(root / "streak.svg")


if __name__ == "__main__":
    main()
