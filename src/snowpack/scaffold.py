"""Scaffolding engine, document generator, and workspace bootstrap for Snowpack."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from snowpack.ui import ui

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
STARTER_TEMPLATES_DIR = TEMPLATES_DIR / "starter"
PROJECT_TEMPLATES_DIR = TEMPLATES_DIR / "project"


def get_git_author() -> str | None:
    """Detects Git user name and email from environment or git config."""
    name = os.environ.get("GIT_AUTHOR_NAME")
    email = os.environ.get("GIT_AUTHOR_EMAIL")
    if name and email:
        return f"{name} <{email}>"
    if name:
        return name

    try:
        res_name = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=1.0,
        )
        if res_name.returncode == 0 and res_name.stdout.strip():
            u_name = res_name.stdout.strip()
            res_mail = subprocess.run(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=1.0,
            )
            if res_mail.returncode == 0 and res_mail.stdout.strip():
                return f"{u_name} <{res_mail.stdout.strip()}>"
            return u_name
    except Exception:
        pass
    return None


def list_available_templates(
    format_filter: str | None = None,
    mode_filter: str | None = None,
) -> list[dict[str, Any]]:
    """Discovers all available templates, presets, and formats across starter directories."""
    templates: list[dict[str, Any]] = []
    clean_fmt = format_filter.strip().lower() if format_filter else None
    if clean_fmt in ("typst", "typ"):
        clean_fmt = "typ"
    elif clean_fmt in ("markdown", "md"):
        clean_fmt = "md"
    elif clean_fmt in ("latex", "tex"):
        clean_fmt = "tex"

    clean_mode = mode_filter.strip().lower() if mode_filter else None

    descriptions = {
        ("report", "reader"): "Long-format technical textbook & course companion (7-stage pedagogy, David Lay cards, Q2 colored equations)",
        ("report", "report"): "Minimal clean sans-serif engineering report (A4/Letter)",
        ("report", "default"): "Minimal clean sans-serif engineering report (A4/Letter)",
        ("report", "executive"): "Executive decision memo, KPI scorecards & strategic brief",
        ("report", "memo"): "Executive decision memo & technical brief powered by Floe",
        ("report", "cheatsheet"): "Multi-column high-density closed-book exam formula reference sheet powered by Floe",
        ("slides", "slides"): "16:9 widescreen presentation (Apple Keynote-style split-hero cards)",
        ("slides", "default"): "16:9 widescreen presentation (Apple Keynote-style split-hero cards)",
        ("slides", "lecture"): "Academic chalkboard / lecture presentation theme",
        ("paper", "paper"): "IEEE standard 2-column academic paper layout",
        ("paper", "default"): "IEEE standard 2-column academic paper layout",
        ("paper", "ieee"): "IEEE Transactions 2-column academic paper",
        ("paper", "springer"): "Springer LNCS single-column academic paper",
    }

    seen_keys: set[tuple[str, str, str]] = set()

    # 1. Type-first subdirectories (typ/reader.typ, typ/report.typ, md/report.md, tex/report.tex, etc.)
    for fmt_dir_name in ("typ", "md", "tex"):
        fmt_dir = STARTER_TEMPLATES_DIR / fmt_dir_name
        if fmt_dir.is_dir():
            for p in sorted(fmt_dir.iterdir()):
                if p.is_file() and p.suffix.lstrip(".") == fmt_dir_name:
                    preset = p.stem
                    fmt = fmt_dir_name
                    # Map preset to conceptual mode
                    if preset in ("slides", "lecture"):
                        mode = "slides"
                    elif preset in ("paper", "ieee", "springer"):
                        mode = "paper"
                    else:
                        mode = "report"

                    key = (fmt, mode, preset)
                    if key not in seen_keys:
                        seen_keys.add(key)
                        desc = descriptions.get(
                            (mode, preset),
                            f"{mode.title()} preset '{preset}' in {fmt.upper()}",
                        )
                        templates.append(
                            {
                                "mode": mode,
                                "preset": preset,
                                "format": fmt,
                                "file": f"{fmt}/{p.name}",
                                "path": str(p),
                                "description": desc,
                            }
                        )

    # Filter by format and mode if requested
    if clean_fmt:
        templates = [t for t in templates if t["format"] == clean_fmt]
    if clean_mode:
        templates = [t for t in templates if t["mode"] == clean_mode]

    return templates


def resolve_document_specs(
    target_or_mode: str,
    preset: str | None = None,
    format_hint: str | None = None,
) -> tuple[str, str, str, Path]:
    """Resolves (mode, format, filename, template_file_path) from user arguments and presets.

    Examples:
      'slides' -> ('slides', 'typ', 'slides.typ', <path to typ/slides.typ>)
      'reader' -> ('report', 'typ', 'report.typ', <path to typ/reader.typ>)
      'report', preset='reader' -> ('report', 'typ', 'report.typ', <path to typ/reader.typ>)
      'paper.tex' -> ('paper', 'tex', 'paper.tex', <path to tex/paper.tex>)
    """
    clean = target_or_mode.strip().lower()

    # Check if target is an explicit preset alias
    resolved_preset = preset
    if clean in ("reader", "deep-reader", "textbook"):
        mode_hint = "report"
        resolved_preset = "reader"
    elif clean in ("lecture", "chalkboard"):
        mode_hint = "slides"
        resolved_preset = "lecture"
    elif clean in ("ieee", "springer"):
        mode_hint = "paper"
        resolved_preset = clean
    elif clean in ("executive", "memo"):
        mode_hint = "report"
        resolved_preset = "memo"
    elif clean in ("cheatsheet", "cheat-sheet", "cheat"):
        mode_hint = "report"
        resolved_preset = "cheatsheet"
    else:
        mode_hint = clean

    # Check if user specified a file extension
    ext = None
    if "." in mode_hint:
        parts = mode_hint.rsplit(".", 1)
        base_name, ext = parts[0], parts[1]
    else:
        base_name = mode_hint

    # Determine format
    if ext in ("typ", "typst"):
        fmt = "typ"
    elif ext in ("md", "markdown"):
        fmt = "md"
    elif ext in ("tex", "latex"):
        fmt = "tex"
    elif format_hint:
        f_clean = format_hint.strip().lower()
        if f_clean in ("typ", "typst"):
            fmt = "typ"
        elif f_clean in ("md", "markdown"):
            fmt = "md"
        elif f_clean in ("tex", "latex"):
            fmt = "tex"
        else:
            fmt = "typ"
    else:
        fmt = "typ"

    # Determine mode
    if "slide" in base_name or "presentation" in base_name or "deck" in base_name:
        mode = "slides"
    elif "paper" in base_name or "ieee" in base_name or "article" in base_name:
        mode = "paper"
    else:
        mode = "report"

    # Locate matching template file from type-first directory (starter/<fmt>/)
    template_file = None
    candidates: list[Path] = []

    if resolved_preset:
        candidates.append(STARTER_TEMPLATES_DIR / fmt / f"{resolved_preset}.{fmt}")
    candidates.append(STARTER_TEMPLATES_DIR / fmt / f"{mode}.{fmt}")
    candidates.append(STARTER_TEMPLATES_DIR / fmt / f"default.{fmt}")
    if mode == "report":
        candidates.append(STARTER_TEMPLATES_DIR / fmt / f"report.{fmt}")

    for cand in candidates:
        if cand.is_file():
            template_file = cand
            break

    if not template_file:
        raise FileNotFoundError(
            f"Starter template not found for mode='{mode}', preset='{resolved_preset}', format='{fmt}' "
            f"(searched: {[str(c) for c in candidates]})"
        )

    # Determine default destination filename
    if "." in mode_hint:
        filename = mode_hint
    elif clean in ("memo", "cheatsheet", "reader", "executive"):
        filename = f"{clean}.{fmt}"
    else:
        filename = f"{mode}.{fmt}"

    return mode, fmt, filename, template_file


def render_template_content(
    template_text: str,
    title: str,
    subtitle: str = "",
    author: str = "Author",
    dependency: str = "Department of Systems & Control",
    date: str | None = None,
    theme: str = "dark",
    engine: str = "typst",
) -> str:
    """Replaces standard Snowpack template placeholders with provided metadata."""
    final_date = date or time.strftime("%B %Y")

    replacements = {
        "__TITLE__": title,
        "__SUBTITLE__": subtitle,
        "__AUTHOR__": author,
        "__DEPENDENCY__": dependency,
        "__DATE__": final_date,
        "__THEME__": theme,
        "__ENGINE__": engine,
    }

    content = template_text
    for key, val in replacements.items():
        content = content.replace(key, val)
    return content


def new_document(
    target_or_mode: str = "report",
    directory: Path | str = ".",
    preset: str | None = None,
    format_hint: str | None = None,
    title: str | None = None,
    subtitle: str | None = None,
    author: str | None = None,
    theme: str = "dark",
    engine: str = "typst",
    force: bool = False,
    with_companions: bool = True,
) -> Path:
    """Generates a new starter Snowpack document and companion files.

    Args:
        target_or_mode: Mode name ('report', 'slides', 'paper') or target filename.
        directory: Destination workspace directory.
        preset: Layout preset ('reader', 'default', 'lecture', 'ieee').
        format_hint: Format override ('typ', 'md', 'tex').
        title: Document title.
        subtitle: Document subtitle.
        author: Author string.
        theme: Presentation theme ('dark' or 'light').
        engine: Markdown engine ('typst' or 'latex').
        force: Overwrite existing files without confirmation.
        with_companions: Also ensure packages.typ/tex and library.bib exist.

    Returns:
        Path of the generated document.
    """
    dest_dir = Path(directory).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    mode, fmt, filename, template_file = resolve_document_specs(
        target_or_mode, preset=preset, format_hint=format_hint
    )
    dest_file = dest_dir / filename

    if dest_file.exists() and not force:
        if sys.stdin.isatty():
            ans = (
                input(
                    f"{ui.badge()} {ui.yellow(f'⚠️  {dest_file.name} already exists. Overwrite? [y/N]: ')}"
                )
                .strip()
                .lower()
            )
            if ans not in ("y", "yes"):
                ui.warn(f"Skipped {dest_file.name} (preserved existing file)")
                return dest_file
        else:
            raise FileExistsError(
                f"File '{dest_file.name}' already exists. Use --force to overwrite."
            )

    # Resolve metadata
    folder_title = dest_dir.name.replace("-", " ").replace("_", " ").title()
    final_title = title or folder_title
    git_author = get_git_author()
    final_author = author or (git_author if git_author else "Author")

    raw_text = template_file.read_text(encoding="utf-8")
    rendered_text = render_template_content(
        raw_text,
        title=final_title,
        subtitle=subtitle or "",
        author=final_author,
        theme=theme,
        engine=engine,
    )

    dest_file.write_text(rendered_text, encoding="utf-8")
    ui.success(f"Created {ui.bold(dest_file.name)} from preset '{template_file.stem}' in {dest_dir}")

    # Scaffold companion files (packages.typ / packages.tex, library.bib)
    if with_companions:
        scaffold_companion_files(dest_dir, fmt, force=False)

    return dest_file


def scaffold_companion_files(
    dest_dir: Path,
    fmt: str = "typ",
    force: bool = False,
) -> list[Path]:
    """Ensures packages.typ/packages.tex and library.bib exist in the workspace."""
    created: list[Path] = []

    # 1. BibTeX file
    bib_target = dest_dir / "library.bib"
    if not bib_target.exists():
        bib_source = PROJECT_TEMPLATES_DIR / "library.bib"
        if bib_source.exists():
            shutil.copy2(bib_source, bib_target)
            created.append(bib_target)
            ui.info(f"Scaffolded companion {ui.bold('library.bib')}")

    # 2. Package manifest
    if fmt == "tex":
        pkg_file = dest_dir / "packages.tex"
        if not pkg_file.exists():
            pkg_source = PROJECT_TEMPLATES_DIR / "packages.tex"
            if pkg_source.exists():
                shutil.copy2(pkg_source, pkg_file)
                created.append(pkg_file)
                ui.info(f"Scaffolded companion {ui.bold('packages.tex')}")
    else:
        pkg_file = dest_dir / "packages.typ"
        if not pkg_file.exists():
            pkg_source = PROJECT_TEMPLATES_DIR / "packages.typ"
            if pkg_source.exists():
                shutil.copy2(pkg_source, pkg_file)
                created.append(pkg_file)
                ui.info(f"Scaffolded companion {ui.bold('packages.typ')}")

    return created


def init_workspace(
    directory: Path | str = ".",
    mode: str = "report",
    preset: str | None = None,
    format_hint: str = "typ",
    title: str | None = None,
    author: str | None = None,
    theme: str = "dark",
    force: bool = False,
) -> dict[str, Any]:
    """Initializes a complete Snowpack publishing workspace."""
    dest_dir = Path(directory).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate starter document and companions
    doc_file = new_document(
        target_or_mode=mode,
        directory=dest_dir,
        preset=preset,
        format_hint=format_hint,
        title=title,
        author=author,
        theme=theme,
        force=force,
        with_companions=True,
    )

    # 2. Add document-aware .gitignore if none exists
    gitignore_file = dest_dir / ".gitignore"
    if not gitignore_file.exists():
        ignores = (
            "*.aux\n"
            "*.log\n"
            "*.out\n"
            "*.toc\n"
            "*.synctex.gz\n"
            "*.fdb_latexmk\n"
            "*.fls\n"
            "_snowpack_*\n"
        )
        gitignore_file.write_text(ignores, encoding="utf-8")
        ui.info(f"Created {ui.bold('.gitignore')}")

    # 3. Add project snowpack.toml configuration
    toml_file = dest_dir / "snowpack.toml"
    if not toml_file.exists():
        clean_title = title or dest_dir.name.replace("-", " ").replace("_", " ").title()
        clean_author = author or get_git_author() or "Author"
        default_engine = "tectonic" if format_hint == "tex" else "typst"
        snowpack_config = (
            "# Snowpack Workspace Configuration\n"
            "[project]\n"
            f'title = "{clean_title}"\n'
            f'author = "{clean_author}"\n'
            f'format = "{format_hint}"\n'
            f'preset = "{preset or "default"}"\n'
            f'engine = "{default_engine}"\n'
            f'theme = "{theme}"\n'
        )
        toml_file.write_text(snowpack_config, encoding="utf-8")
        ui.info(f"Created {ui.bold('snowpack.toml')}")

    files = [p.name for p in dest_dir.iterdir() if p.is_file()]
    return {
        "status": "ok",
        "directory": str(dest_dir),
        "target_file": str(doc_file),
        "mode": mode,
        "format": format_hint,
        "files": files,
    }
