#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "build" / "writebook"
TARGET_DIR = ROOT / "src"

BOOK_TITLE = "Notes on Shaping Life"
BOOK_DESCRIPTION = "A short book assembled from a PDF draft and published as an mdBook."

CHAPTERS = [
    ("04-opening.md", "opening.md", "Opening"),
    ("05-on-awareness.md", "on-awareness.md", "On Awareness"),
    ("06-awareness-awareness-awareness.md", "awareness-awareness-awareness.md", '"Awareness. Awareness. Awareness."'),
    ("07-on-attention.md", "on-attention.md", "On Attention"),
    ("08-on-suffering.md", "on-suffering.md", "On Suffering"),
    ("09-on-joy.md", "on-joy.md", "On Joy"),
    ("10-on-perspective.md", "on-perspective.md", "On Perspective"),
    ("11-on-truth.md", "on-truth.md", "On Truth"),
    ("12-on-opinions.md", "on-opinions.md", "On Opinions"),
    ("13-on-simplicity.md", "on-simplicity.md", "On Simplicity"),
    ("14-on-action.md", "on-action.md", "On Action"),
    ("15-on-ownership.md", "on-ownership.md", "On Ownership"),
    ("16-on-identity.md", "on-identity.md", "On Identity"),
    ("17-on-tradeoffs.md", "on-tradeoffs.md", "On Tradeoffs"),
    ("18-on-commitment.md", "on-commitment.md", "On Commitment"),
    ("19-on-time.md", "on-time.md", "On Time"),
    ("20-on-creating.md", "on-creating.md", "On Creating"),
    ("21-on-inversion.md", "on-inversion.md", "On Inversion"),
    ("22-on-winning.md", "on-winning.md", "On Winning"),
    ("23-the-question.md", "the-question.md", "The Question"),
]


def clean_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()
    cleaned: list[str] = []

    for line in lines:
        stripped = line.strip()
        if re.fullmatch(r"final-\s+notes on shaping life\s+\d+", stripped, re.IGNORECASE):
            continue
        if re.fullmatch(r"final-\s+notes on shaping life", stripped, re.IGNORECASE):
            continue
        if stripped.startswith("Created    @") and "Updated @" in stripped:
            continue
        cleaned.append(line.rstrip())

    output = "\n".join(cleaned)
    output = re.sub(r"\n{3,}", "\n\n", output).strip()
    return output + "\n"


def write_intro() -> None:
    intro = f"""# {BOOK_TITLE}

{BOOK_DESCRIPTION}

This edition was reconstructed from a PDF draft and adapted into Markdown for web publication with `mdBook`.
"""
    (TARGET_DIR / "README.md").write_text(intro, encoding="utf-8")


def write_summary() -> None:
    lines = ["# Summary", "", f"[{BOOK_TITLE}](README.md)", ""]
    for _, target_name, title in CHAPTERS:
        lines.append(f"- [{title}]({target_name})")
    lines.append("")
    (TARGET_DIR / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_DIR.exists():
        raise SystemExit(f"Missing source directory: {SOURCE_DIR}")

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    TARGET_DIR.mkdir(parents=True)

    write_intro()
    write_summary()

    for source_name, target_name, _title in CHAPTERS:
        source_path = SOURCE_DIR / source_name
        target_path = TARGET_DIR / target_name
        content = source_path.read_text(encoding="utf-8")
        target_path.write_text(clean_markdown(content), encoding="utf-8")

    print(f"Wrote mdBook source files to {TARGET_DIR}")


if __name__ == "__main__":
    main()
