#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
from pathlib import Path


CHAPTER_PATTERNS = [
    re.compile(r"^(chapter\s+\d+[:.\- ]?.*)$", re.IGNORECASE),
    re.compile(r"^(part\s+\d+[:.\- ]?.*)$", re.IGNORECASE),
    re.compile(r"^([ivxlcdm]+\.\s+.+)$", re.IGNORECASE),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF draft into Markdown files that are easier to paste into Writebook."
    )
    parser.add_argument("pdf", type=Path, help="Path to the source PDF")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("build/writebook"),
        help="Directory for generated Markdown files",
    )
    parser.add_argument(
        "--no-split",
        action="store_true",
        help="Generate a single Markdown file instead of splitting by headings",
    )
    return parser.parse_args()


def require_tool(name: str) -> None:
    if shutil.which(name):
        return
    print(f"Missing required tool: {name}", file=sys.stderr)
    sys.exit(1)


def extract_text(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr.strip() or "pdftotext failed", file=sys.stderr)
        sys.exit(result.returncode)
    return result.stdout


def normalize_text(text: str) -> str:
    text = text.replace("\f", "\n")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]

    cleaned: list[str] = []
    for line in lines:
        stripped = line.strip()

        # Drop isolated page numbers and obvious running headers/footers.
        if re.fullmatch(r"\d+", stripped):
            continue

        cleaned.append(line)

    text = "\n".join(cleaned)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    for pattern in CHAPTER_PATTERNS:
        if pattern.match(stripped):
            return True
    if len(stripped) <= 80 and stripped == stripped.title() and len(stripped.split()) <= 8:
        return True
    return False


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "page"


def split_sections(text: str) -> list[tuple[str, str]]:
    lines = text.splitlines()
    sections: list[tuple[str, list[str]]] = []
    current_title = "Front Matter"
    current_lines: list[str] = []

    for line in lines:
        if looks_like_heading(line):
            if current_lines:
                sections.append((current_title, current_lines))
            current_title = line.strip()
            current_lines = [f"# {current_title}", ""]
            continue
        current_lines.append(line)

    if current_lines:
        sections.append((current_title, current_lines))

    rendered: list[tuple[str, str]] = []
    for title, content_lines in sections:
        body = "\n".join(content_lines).strip() + "\n"
        rendered.append((title, cleanup_markdown(body)))
    return rendered


def cleanup_markdown(text: str) -> str:
    lines = text.splitlines()
    rebuilt: list[str] = []

    paragraph: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if paragraph:
                rebuilt.append(join_paragraph(paragraph))
                paragraph = []
            rebuilt.append("")
            continue

        if stripped.startswith("#"):
            if paragraph:
                rebuilt.append(join_paragraph(paragraph))
                paragraph = []
            rebuilt.append(stripped)
            continue

        paragraph.append(stripped)

    if paragraph:
        rebuilt.append(join_paragraph(paragraph))

    output = "\n".join(rebuilt)
    output = re.sub(r"\n{3,}", "\n\n", output)
    return output.strip() + "\n"


def join_paragraph(lines: list[str]) -> str:
    text = " ".join(lines)
    text = re.sub(r"\s+([,.;:?!])", r"\1", text)
    text = re.sub(r"([(\[])\s+", r"\1", text)
    text = re.sub(r"\s+([)\]])", r"\1", text)
    return text


def write_outputs(output_dir: Path, sections: list[tuple[str, str]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.csv"

    with manifest_path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.writer(manifest_file)
        writer.writerow(["order", "title", "file"])

        for index, (title, content) in enumerate(sections, start=1):
            filename = f"{index:02d}-{slugify(title)}.md"
            path = output_dir / filename
            path.write_text(content, encoding="utf-8")
            writer.writerow([index, title, filename])


def main() -> None:
    args = parse_args()
    require_tool("pdftotext")

    pdf_path = args.pdf.expanduser().resolve()
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    raw_text = extract_text(pdf_path)
    text = normalize_text(raw_text)

    if not text.strip():
        print("No text was extracted from the PDF. It may need OCR first.", file=sys.stderr)
        sys.exit(1)

    if args.no_split:
        sections = [("Full Draft", cleanup_markdown(text))]
    else:
        sections = split_sections(text)

    write_outputs(args.output_dir, sections)
    print(f"Wrote {len(sections)} Markdown file(s) to {args.output_dir}")
    print(f"Manifest: {args.output_dir / 'manifest.csv'}")


if __name__ == "__main__":
    main()
