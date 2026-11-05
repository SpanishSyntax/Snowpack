"""Multi-chapter modular Markdown assembler for Snowpack."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from snowpack.frontmatter import normalize_mode, parse_frontmatter
from snowpack.ui import ui


def natural_sort_key(p: Path) -> list[Any]:
    """Sort key that orders numerical filenames naturally (e.g. 1, 2, 10)."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", p.name)]


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Lightweight zero-dependency YAML parser for book and chapter manifests."""
    result: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" in stripped:
            k, v = stripped.split(":", 1)
            k = k.strip().lower()
            v = v.strip().strip("\"'")
            if not v:
                sub_items: list[Any] = []
                i += 1
                while i < len(lines):
                    s_line = lines[i]
                    s_stripped = s_line.strip()
                    if not s_stripped or s_stripped.startswith("#"):
                        i += 1
                        continue
                    indent = len(s_line) - len(s_line.lstrip(" "))
                    if indent == 0 and not s_stripped.startswith("-"):
                        break
                    if s_stripped.startswith("- "):
                        sub_items.append(s_stripped[2:].strip().strip("\"'"))
                    i += 1
                result[k] = sub_items
                continue
            else:
                result[k] = v
        i += 1
    return result


def resolve_ordered_chapter_files(
    work_path: Path,
    ch_path: Path,
    pattern: str = "*.md",
) -> list[Path]:
    """Resolves chapter files using a multi-tier strategy:
    1. Manifest file (book.yaml, book.toml, snowpack.yaml, manifest.yaml).
    2. Order list file (order.txt).
    3. Natural alphanumeric sort across matching files in chapters_dir.
    """
    manifest_names = (
        "book.yaml",
        "book.yml",
        "book.toml",
        "snowpack.yaml",
        "snowpack.yml",
        "snowpack.toml",
        "manifest.yaml",
    )
    for search_dir in (work_path, ch_path):
        for m_name in manifest_names:
            m_file = search_dir / m_name
            if m_file.is_file():
                try:
                    content = m_file.read_text(encoding="utf-8")
                    if m_file.suffix.lower() == ".toml":
                        import tomllib

                        data = tomllib.loads(content)
                    else:
                        data = _parse_simple_yaml(content)
                    raw_chaps = data.get("chapters", data.get("pages", []))
                    resolved: list[Path] = []
                    for item in raw_chaps:
                        rel_p = item if isinstance(item, str) else item.get("path", "")
                        if rel_p:
                            for base in (search_dir, ch_path, work_path):
                                cand = (base / rel_p).resolve()
                                if cand.is_file() and cand not in resolved:
                                    resolved.append(cand)
                                    break
                    if resolved:
                        return resolved
                except Exception:
                    pass

    # Tier 2: Check order.txt in ch_path
    order_file = ch_path / "order.txt"
    if order_file.is_file():
        try:
            lines = [
                ln.strip() for ln in order_file.read_text(encoding="utf-8").splitlines()
            ]
            resolved = []
            for ln in lines:
                if ln and not ln.startswith("#"):
                    cand = (ch_path / ln).resolve()
                    if cand.is_file():
                        resolved.append(cand)
            if resolved:
                return resolved
        except Exception:
            pass

    # Tier 3: Natural sort fallback
    return sorted(
        [f for f in ch_path.glob(pattern) if f.is_file()],
        key=natural_sort_key,
    )


def assemble_documents(
    chapters_dir: str = "chapters",
    output_filename: str | None = None,
    mode: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    author: str | None = None,
    dependency: str | None = None,
    date: str | None = None,
    engine: str | None = None,
    theme: str | None = None,
    aspect_ratio: str | None = None,
    pattern: str = "*.md",
    add_pagebreaks: bool = True,
    base_dir: Path | str = ".",
) -> bool:
    """Assembles modular chapter Markdown files into a unified document with consolidated frontmatter."""
    work_path = Path(base_dir).resolve()
    ch_path = (
        work_path / chapters_dir
        if not Path(chapters_dir).is_absolute()
        else Path(chapters_dir)
    )
    if not ch_path.is_dir():
        ui.error(f"Chapters directory not found: '{chapters_dir}'.")
        return False

    matched_files = resolve_ordered_chapter_files(work_path, ch_path, pattern=pattern)
    if not matched_files:
        ui.error(f"No chapter files matching '{pattern}' found in '{chapters_dir}'.")
        return False

    final_mode = normalize_mode(mode)
    if output_filename:
        out_path = (
            work_path / output_filename
            if not Path(output_filename).is_absolute()
            else Path(output_filename)
        )
    else:
        out_path = work_path / ("slides.md" if final_mode == "slides" else "report.md")

    existing_meta: dict[str, str] = {}
    if out_path.is_file():
        existing_meta = parse_frontmatter(out_path)

    default_title = work_path.name.replace("-", " ").replace("_", " ").title()
    final_title = (title or existing_meta.get("title") or default_title).strip()
    final_subtitle = (subtitle or existing_meta.get("subtitle") or "").strip()
    final_author = (author or existing_meta.get("author") or "Author").strip()
    final_dependency = (dependency or existing_meta.get("dependency") or "").strip()
    final_date = (date or existing_meta.get("date") or "").strip()
    final_engine = (engine or existing_meta.get("engine") or "typst").strip().lower()

    fm_lines = ["---", f'title: "{final_title}"']
    if final_subtitle:
        fm_lines.append(f'subtitle: "{final_subtitle}"')
    if final_author:
        fm_lines.append(f'author: "{final_author}"')
    if final_dependency:
        fm_lines.append(f'dependency: "{final_dependency}"')
    if final_date:
        fm_lines.append(f'date: "{final_date}"')
    fm_lines.append(f'mode: "{final_mode}"')
    fm_lines.append(f'engine: "{final_engine}"')

    if final_mode == "slides":
        final_theme = (theme or existing_meta.get("theme") or "dark").strip().lower()
        final_aspect = (
            aspect_ratio or existing_meta.get("aspect_ratio") or "16-9"
        ).strip()
        fm_lines.append(f'theme: "{final_theme}"')
        fm_lines.append(f'aspect-ratio: "{final_aspect}"')

    fm_lines.append("---")
    header_block = "\n".join(fm_lines)

    processed_names: list[str] = []
    chapter_bodies: list[str] = []

    for cf in matched_files:
        try:
            content = cf.read_text(encoding="utf-8")
        except Exception as exc:
            ui.error(f"Failed to read chapter file '{cf.name}': {exc}")
            return False

        clean_body = re.sub(
            r"^---\s*\n.*?\n---\s*\n?", "", content, flags=re.DOTALL
        ).strip()
        if clean_body:
            processed_names.append(cf.name)
            chapter_bodies.append(clean_body)

    if not chapter_bodies:
        ui.error(f"All matched chapter files in '{chapters_dir}' were empty.")
        return False

    if final_mode == "slides":
        separator = "\n\n---\n\n"
    elif add_pagebreaks:
        separator = "\n\n```{=typst}\n#pagebreak()\n```\n\n"
    else:
        separator = "\n\n"

    assembled_content = f"{header_block}\n\n" + separator.join(chapter_bodies) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(assembled_content, encoding="utf-8")

    ui.success(
        f"Assembled {ui.bold(str(len(processed_names)))} chapters into {ui.bold(str(out_path))} ({final_mode} mode)"
    )
    return True
