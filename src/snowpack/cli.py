"""CLI router, argument parser, and interactive status dashboard for Snowpack."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

from snowpack import __version__
from snowpack.assembler import assemble_documents, natural_sort_key
from snowpack.compiler import (
    _linux_set_pdeathsig,
    build_pdf,
    compile_markdown_latex,
    compile_markdown_typst,
    compile_tectonic,
    compile_typst_direct,
)
from snowpack.config import check_toolchain, load_user_config
from snowpack.discovery import (
    discover_workspace_documents,
    find_target_file,
    print_status_dashboard,
    resolve_typst_template,
)
from snowpack.frontmatter import build_typst_kwargs, normalize_mode, parse_frontmatter
from snowpack.templates_latex import tex_safe
from snowpack.ui import handle_agent_args, handle_color_args, ui
from snowpack.watcher import watch_pdf

__all__ = [
    "main",
    "build_pdf",
    "assemble_documents",
    "watch_pdf",
    "find_target_file",
    "resolve_typst_template",
    "parse_frontmatter",
    "build_typst_kwargs",
    "normalize_mode",
    "compile_tectonic",
    "compile_typst_direct",
    "compile_markdown_latex",
    "compile_markdown_typst",
    "print_status_dashboard",
    "load_user_config",
    "tex_safe",
    "natural_sort_key",
    "check_toolchain",
    "discover_workspace_documents",
    "_linux_set_pdeathsig",
]


def get_usage() -> str:
    """Returns the Prism-styled help and usage guide matching Basecamp & Borealis, or compact agent guide."""
    return ui.render_help(
        tagline="Polyglot Document & Presentation Compiler (Typst + LaTeX)",
        version=__version__,
        usage=[
            "snowpack [file] [options]",
            "snowpack build [file] [options]",
            "snowpack new [target] [options]",
            "snowpack init [preset] [options]",
            "snowpack assemble [dir] [options]",
            "snowpack mcp",
        ],
        commands=[
            ("build [file]", "Build PDF from Markdown, Typst, or LaTeX"),
            ("new [target]", "Scaffold a new document: report, slides, paper (.typ, .md, .tex)"),
            ("init [preset]", "Initialize complete Snowpack workspace with packages and starter doc"),
            ("assemble [dir]", "Assemble modular chapters into master Markdown"),
            ("mcp", "Run Model Context Protocol (MCP) stdio server"),
        ],
        sections=[
            (
                "Operating Modes",
                [
                    ("-m report", "Minimal sans-serif document (default, A4/Letter)"),
                    ("-m slides", "16:9 widescreen presentation (1920x1080)"),
                    ("-m paper", "Academic paper (IEEE 2-column layout)"),
                ],
            )
        ],
        options=[
            ("-A, --agent", "Compact machine/agent friendly output mode"),
            ("--json", "Structured JSON output mode"),
            ("-m, --mode MODE", "Document operating mode: report, slides, paper"),
            ("-p, --preset PRESET", "Layout preset (e.g. 'ieee', 'default')"),
            ("-f, --format FMT", "Document format: typ (default), md, tex"),
            ("-o, --output PATH", "Specify output PDF filename"),
            ("-t, --template PATH", "Use custom Typst template file"),
            ("-w, --watch", "Watch mode: recompile automatically on file changes"),
            ("--title TITLE", "Document title for 'new' / 'init'"),
            ("--author AUTHOR", "Document author for 'new' / 'init'"),
            ("--theme THEME", "Presentation theme ('dark' or 'light')"),
            ("--engine ENGINE", "Compiler engine: 'typst' (default) or 'tectonic'"),
            ("--root PATH", "Typst compilation root directory"),
            ("--font-path PATH", "Additional directory containing fonts for Typst"),
            ("--open", "Open generated PDF in system viewer after build"),
            ("--color MODE", "Color output mode: auto, always, never"),
            ("--no-color", "Disable colored output"),
            ("-h, --help", "Show this help message and exit"),
            ("-V, -v, --version", "Show version information and exit"),
        ],
        examples=[
            ("snowpack", "Interactive telemetry & documents dashboard"),
            ("snowpack new slides", "Scaffold modern 16:9 Typst presentation (slides.typ)"),
            ("snowpack new paper --format md", "Scaffold IEEE 2-column Markdown paper (paper.md)"),
            ("snowpack init", "Initialize workspace (packages.typ + report.typ + bib)"),
            ("snowpack report.md", "Compile report.md -> report.pdf"),
            ("snowpack assemble chapters", "Assemble chapters/*.md -> report.md"),
            ("snowpack deck.md -m slides -w", "Live watch 16:9 presentation"),
            ("snowpack main.typ -w", "Direct Typst compilation with live reload"),
        ],
    )


USAGE = get_usage()


def _handle_init_cmd(rest: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="snowpack init", add_help=False)
    parser.add_argument("mode", nargs="?", default="report")
    parser.add_argument("-f", "--format", dest="format_hint", default="typ")
    parser.add_argument("--title", dest="title", default=None)
    parser.add_argument("--author", dest="author", default=None)
    parser.add_argument("--theme", dest="theme", default="dark")
    parser.add_argument(
        "-F", "--force", dest="force", action="store_true", default=False
    )
    parser.add_argument("-d", "--dir", dest="directory", default=".")
    args, _ = parser.parse_known_args(rest)
    try:
        from snowpack.scaffold import init_workspace

        res = init_workspace(
            directory=args.directory,
            mode=args.mode,
            format_hint=args.format_hint,
            title=args.title,
            author=args.author,
            theme=args.theme,
            force=args.force,
        )
        if ui.is_json:
            ui.json(res)
        return 0
    except Exception as exc:
        ui.error(str(exc))
        return 1


def _handle_new_cmd(rest: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="snowpack new", add_help=False)
    parser.add_argument("target", nargs="?", default="report")
    parser.add_argument("-m", "--mode", dest="mode", default=None)
    parser.add_argument("-f", "--format", dest="format_hint", default=None)
    parser.add_argument("--title", dest="title", default=None)
    parser.add_argument("--subtitle", dest="subtitle", default=None)
    parser.add_argument("--author", dest="author", default=None)
    parser.add_argument("--theme", dest="theme", default="dark")
    parser.add_argument("--engine", dest="engine", default="typst")
    parser.add_argument(
        "-F", "--force", dest="force", action="store_true", default=False
    )
    parser.add_argument("-d", "--dir", dest="directory", default=".")
    args, _ = parser.parse_known_args(rest)
    try:
        from snowpack.scaffold import new_document

        target = args.mode or args.target
        path = new_document(
            target_or_mode=target,
            directory=args.directory,
            format_hint=args.format_hint,
            title=args.title,
            subtitle=args.subtitle,
            author=args.author,
            theme=args.theme,
            engine=args.engine,
            force=args.force,
        )
        if ui.is_json:
            ui.json({"status": "ok", "file": str(path)})
        return 0
    except Exception as exc:
        ui.error(str(exc))
        return 1


def run_interactive_hub(docs: list[Path], user_cfg: dict[str, Any]) -> int:
    """Provides interactive quick actions when Snowpack is run without arguments."""
    actions: list[tuple[str, str, str]] = []

    if docs:
        first_doc = docs[0]
        actions.append(
            (
                "build",
                f"Compile '{first_doc.name}' to PDF",
                "Immediate Typst/LaTeX compilation",
            )
        )
        actions.append(
            (
                "watch",
                f"Watch & live compile '{first_doc.name}'",
                "Recompiles instantly on file save",
            )
        )
        if len(docs) > 1:
            actions.append(
                (
                    "select_build",
                    "Pick from discovered documents...",
                    f"{len(docs)} document targets found",
                )
            )
    else:
        actions.append(
            (
                "build_custom",
                "Compile a document to PDF...",
                "Specify a document file path to compile",
            )
        )
        actions.append(
            (
                "watch_custom",
                "Watch & live compile a document...",
                "Live reload a specific document file path",
            )
        )

    # Check for chapters / modules directory or offer assemble
    ch_dirs = (
        [
            d.name
            for d in Path(".").iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        if Path(".").exists()
        else []
    )
    detected_ch = [
        d for d in ("chapters", "modules", "sections", "parts") if d in ch_dirs
    ]
    if detected_ch:
        desc = f"Join markdown files from ./{detected_ch[0]}/ into a master document"
    else:
        desc = "Join modular chapter markdown files into a master document"
    actions.append(
        ("assemble", "Assemble modular chapters (join multiple .md files)", desc)
    )

    actions.append(
        (
            "new_doc",
            "Scaffold a new document (report, slides, paper)",
            "Generate Typst, Markdown, or LaTeX starter templates",
        )
    )
    actions.append(
        (
            "init_ws",
            "Initialize Snowpack workspace",
            "Bootstrap workspace with packages.typ and starter files",
        )
    )
    actions.append(("exit", "Exit", "Close Snowpack"))

    choice = ui.select("Snowpack Quick Actions:", actions)

    if choice == "exit":
        return 0
    elif choice == "new_doc":
        mode_choice = ui.select(
            "Select document type to scaffold:",
            [
                ("report", "Technical Report / Standard Document (A4/Letter)"),
                ("slides", "16:9 Widescreen Presentation (1080p Keynote style)"),
                ("paper", "Academic Paper (IEEE 2-column layout)"),
            ],
        )
        fmt_choice = ui.select(
            "Select format:",
            [
                ("typ", "Typst (.typ) - fast, native typesetting"),
                ("md", "Markdown (.md) - portable frontmatter document"),
                ("tex", "LaTeX (.tex) - academic TeX document"),
            ],
        )
        from snowpack.scaffold import new_document

        new_document(target_or_mode=mode_choice, format_hint=fmt_choice)
        return 0
    elif choice == "init_ws":
        from snowpack.scaffold import init_workspace

        init_workspace()
        return 0
    elif choice == "assemble":
        default_dir = detected_ch[0] if detected_ch else "chapters"
        ch_dir = ui.prompt(
            "Directory containing chapter markdown files", default=default_dir
        )
        ok = assemble_documents(chapters_dir=ch_dir)
        if ok and ui.confirm("Compile assembled document to PDF now?", default=True):
            build_pdf(
                target_file=None,
                open_after=bool(user_cfg.get("open", False)),
            )
        return 0 if ok else 1
    elif choice == "build" and docs:
        ok = build_pdf(
            target_file=str(docs[0]),
            open_after=bool(user_cfg.get("open", False)),
        )
        return 0 if ok else 1
    elif choice == "watch" and docs:
        watch_pdf(
            target_file=str(docs[0]),
            open_after=bool(user_cfg.get("open", False)),
        )
        return 0
    elif choice == "select_build" and docs:
        options = [
            (
                str(d),
                f"{'📄' if d.suffix == '.md' else ('📓' if d.suffix == '.typ' else '📜')} {d.name}",
                f"{d.stat().st_size:,} bytes",
            )
            for d in docs
        ]
        chosen = ui.select("Select document to compile:", options)
        ok = build_pdf(
            target_file=chosen,
            open_after=bool(user_cfg.get("open", False)),
        )
        return 0 if ok else 1
    elif choice == "build_custom":
        target = ui.prompt(
            "Document path to compile (.md, .typ, .tex)", default="report.md"
        )
        if not Path(target).exists():
            ui.error(f"File not found: '{target}'")
            return 1
        ok = build_pdf(
            target_file=target,
            open_after=bool(user_cfg.get("open", False)),
        )
        return 0 if ok else 1
    elif choice == "watch_custom":
        target = ui.prompt("Document path to watch & live compile", default="report.md")
        if not Path(target).exists():
            ui.error(f"File not found: '{target}'")
            return 1
        watch_pdf(
            target_file=target,
            open_after=bool(user_cfg.get("open", False)),
        )
        return 0

    return 0


def _parse_assemble_args(rest: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(prog="snowpack assemble", add_help=False)
    parser.add_argument("chapters_dir", nargs="?", default="chapters")
    parser.add_argument("-o", "--output", dest="output_filename", default=None)
    parser.add_argument("-m", "--mode", dest="mode", default=None)
    parser.add_argument("--title", dest="title", default=None)
    parser.add_argument("--subtitle", dest="subtitle", default=None)
    parser.add_argument("--author", dest="author", default=None)
    parser.add_argument("--dependency", dest="dependency", default=None)
    parser.add_argument("--date", dest="date", default=None)
    parser.add_argument("--engine", dest="engine", default=None)
    parser.add_argument("--theme", dest="theme", default=None)
    parser.add_argument("--aspect-ratio", dest="aspect_ratio", default=None)
    parser.add_argument("--pattern", dest="pattern", default="*.md")
    parser.add_argument(
        "--no-pagebreaks",
        dest="add_pagebreaks",
        action="store_false",
        default=True,
    )
    args, _ = parser.parse_known_args(rest)
    return vars(args)


def _parse_build_args(rest: list[str], user_cfg: dict[str, Any]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(prog="snowpack", add_help=False)
    parser.add_argument("target_file", nargs="?", default=None)
    parser.add_argument("-o", "--output", dest="output_filename", default=None)
    parser.add_argument("-m", "--mode", dest="mode", default=None)
    parser.add_argument("-p", "--preset", dest="preset", default=None)
    parser.add_argument(
        "-t", "--template", dest="custom_template", default=user_cfg.get("template")
    )
    parser.add_argument(
        "-w", "--watch", dest="is_watch", action="store_true", default=False
    )
    parser.add_argument("--engine", dest="engine", default=user_cfg.get("engine"))
    parser.add_argument("--root", dest="root_path", default=user_cfg.get("root"))
    parser.add_argument(
        "--font-path", dest="font_path", default=user_cfg.get("font_path")
    )
    parser.add_argument(
        "--open",
        dest="open_after",
        action="store_true",
        default=bool(user_cfg.get("open", False)),
    )
    args, _ = parser.parse_known_args(rest)
    return vars(args)


def main(argv: Sequence[str] | None = None) -> int:
    raw_args = list(argv) if argv is not None else sys.argv[1:]
    if (
        (raw_args and raw_args[0] == "mcp")
        or ("mcp" in raw_args)
        or (argv is None and "mcp" in sys.argv)
    ):
        from snowpack.mcp import main as mcp_main

        return mcp_main()
    user_cfg = load_user_config()
    if "color" in user_cfg:
        ui.set_color_mode(str(user_cfg["color"]))
    handle_agent_args(raw_args)
    handle_color_args(raw_args)

    if any(a in ("-h", "--help", "help") for a in raw_args):
        print(get_usage())
        return 0

    if ui.handle_version_arg(raw_args, __version__):
        return 0

    # No arguments provided: display dashboard panel!
    if not raw_args:
        docs = print_status_dashboard()
        if ui.is_interactive:
            return run_interactive_hub(docs, user_cfg)
        else:
            if docs:
                ok = build_pdf(
                    target_file=str(docs[0]),
                    open_after=bool(user_cfg.get("open", False)),
                )
                return 0 if ok else 1
            return 0

    cmd = raw_args[0]
    rest = raw_args[1:]

    if cmd == "init":
        return _handle_init_cmd(rest)

    if cmd == "new":
        return _handle_new_cmd(rest)

    if cmd == "mcp":
        from snowpack.mcp import main as mcp_main

        return mcp_main()

    if cmd == "assemble":
        asm_kwargs = _parse_assemble_args(rest)
        ok = assemble_documents(**asm_kwargs)
        return 0 if ok else 1

    # Build command or direct file/options
    build_args = rest if cmd == "build" else raw_args
    opts = _parse_build_args(build_args, user_cfg)
    is_watch = opts.pop("is_watch", False)

    if is_watch:
        watch_pdf(**opts)
        return 0
    else:
        ok = build_pdf(**opts)
        if ui.is_json:
            target_val = opts.get("target_file")
            out_pdf = opts.get("output_filename")
            ui.json(
                {
                    "status": "ok" if ok else "error",
                    "target": str(target_val) if target_val else None,
                    "output": str(out_pdf) if out_pdf else None,
                    "mode": opts.get("mode", "report"),
                }
            )
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
