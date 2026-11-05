"""Model Context Protocol (MCP) server for Snowpack."""

from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path
from typing import Any

from snowpack import __version__
from snowpack.assembler import assemble_documents, resolve_ordered_chapter_files
from snowpack.compiler import build_pdf
from snowpack.frontmatter import normalize_mode

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "snowpack_build",
        "description": "Compiles Markdown, Typst, or LaTeX into publication-grade PDFs, IEEE academic papers, or 16:9 presentation slide decks via Snowpack.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to source document (.md, .typ, or .tex; defaults to auto-discovery or 'input.md').",
                    "default": "input.md",
                },
                "output_pdf": {
                    "type": "string",
                    "description": "Optional custom output PDF destination path (-o).",
                    "default": "",
                },
                "mode": {
                    "type": "string",
                    "description": "Operating mode: 'report' (default A4/Letter), 'slides' (16:9 widescreen presentation), or 'paper' (IEEE 2-column layout).",
                    "default": "report",
                },
                "preset": {
                    "type": "string",
                    "description": "Layout preset, e.g. 'ieee', 'default' (-p).",
                    "default": "",
                },
                "engine": {
                    "type": "string",
                    "description": "Compiler engine override: 'typst' (default) or 'tectonic' (--engine).",
                    "default": "typst",
                },
                "template": {
                    "type": "string",
                    "description": "Optional custom Typst template path (-t).",
                    "default": "",
                },
                "root_dir": {
                    "type": "string",
                    "description": "Optional compilation root directory for Typst (--root).",
                    "default": "",
                },
                "font_path": {
                    "type": "string",
                    "description": "Additional directory containing custom fonts for Typst (--font-path).",
                    "default": "",
                },
            },
        },
    },
    {
        "name": "snowpack_assemble",
        "description": "Assembles modular chapter Markdown files into a unified master document with consolidated frontmatter for Snowpack compilation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chapters_dir": {
                    "type": "string",
                    "description": "Directory containing individual chapter Markdown files (default 'chapters').",
                    "default": "chapters",
                },
                "output_file": {
                    "type": "string",
                    "description": "Target assembled Markdown file path (default 'report.md' or 'slides.md').",
                    "default": "",
                },
                "title": {
                    "type": "string",
                    "description": "Document title override. If omitted, derives from existing frontmatter or directory name.",
                    "default": "",
                },
                "subtitle": {
                    "type": "string",
                    "description": "Optional subtitle or course descriptor.",
                    "default": "",
                },
                "author": {
                    "type": "string",
                    "description": "Document author name. If omitted, derives from frontmatter or 'Author'.",
                    "default": "",
                },
                "dependency": {
                    "type": "string",
                    "description": "Institutional affiliation / department.",
                    "default": "",
                },
                "date": {
                    "type": "string",
                    "description": "Document date string (e.g. 'November 2026').",
                    "default": "",
                },
                "mode": {
                    "type": "string",
                    "description": "Snowpack operating mode: 'report' (default A4/Letter), 'slides' (16:9 presentation), or 'paper'.",
                    "default": "report",
                },
                "theme": {
                    "type": "string",
                    "description": "Presentation theme if mode is 'slides': 'dark' (default) or 'light'.",
                    "default": "dark",
                },
                "aspect_ratio": {
                    "type": "string",
                    "description": "Presentation aspect ratio: '16-9' (default).",
                    "default": "16-9",
                },
                "engine": {
                    "type": "string",
                    "description": "Compiler engine: 'typst' (default) or 'tectonic' / 'latex'.",
                    "default": "typst",
                },
                "pattern": {
                    "type": "string",
                    "description": "Filename glob pattern to match chapter files (default '*.md').",
                    "default": "*.md",
                },
                "add_pagebreaks": {
                    "type": "boolean",
                    "description": "Insert pagebreaks between chapters in report mode (default True).",
                    "default": True,
                },
                "workspace_dir": {
                    "type": "string",
                    "description": "Workspace root directory where chapters and output reside (default '.').",
                    "default": ".",
                },
            },
        },
    },
]


def execute_tool(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a Snowpack MCP tool call and return JSON-serializable results."""
    args = arguments or {}
    try:
        if name == "snowpack_build":
            input_file = args.get("input_file") or "input.md"
            target_path = Path(input_file).expanduser().resolve()
            if not target_path.is_file():
                if input_file == "input.md":
                    for cand in (
                        "report.md",
                        "slides.md",
                        "paper.md",
                        "report.typ",
                        "slides.typ",
                        "main.typ",
                        "main.tex",
                    ):
                        cand_path = Path(cand).resolve()
                        if cand_path.is_file():
                            target_path = cand_path
                            break
                if not target_path.is_file():
                    return {"status": "error", "error": f"Source document not found: {input_file}"}

            output_pdf = str(args.get("output_pdf", "")).strip() or None
            mode = str(args.get("mode", "")).strip() or None
            preset = str(args.get("preset", "")).strip() or None
            engine = str(args.get("engine", "")).strip() or None
            template = str(args.get("template", "")).strip() or None
            root_dir = str(args.get("root_dir", "")).strip() or None
            font_path = str(args.get("font_path", "")).strip() or None

            expected_pdf = (
                Path(output_pdf).resolve()
                if output_pdf
                else target_path.with_suffix(".pdf")
            )

            # Redirect stdout to stderr during execution so UI/print messages do not break JSON-RPC stream
            with contextlib.redirect_stdout(sys.stderr):
                ok = build_pdf(
                    target_file=str(target_path),
                    output_filename=str(expected_pdf) if output_pdf else None,
                    mode=mode,
                    preset=preset,
                    custom_template=template,
                    engine=engine,
                    root_path=root_dir,
                    font_path=font_path,
                    quiet=True,
                )

            pdf_exists = expected_pdf.is_file()
            pdf_size = expected_pdf.stat().st_size if pdf_exists else 0

            if ok and pdf_exists:
                return {
                    "status": "ok",
                    "input_file": str(target_path),
                    "output_pdf": str(expected_pdf),
                    "mode": mode or "report",
                    "engine": engine or ("tectonic" if target_path.suffix == ".tex" else "typst"),
                    "pdf_created": True,
                    "size_bytes": pdf_size,
                }
            else:
                return {
                    "status": "error",
                    "error": f"Failed to compile PDF for {target_path}",
                    "input_file": str(target_path),
                    "output_pdf": str(expected_pdf) if pdf_exists else None,
                    "pdf_created": pdf_exists,
                }

        elif name == "snowpack_assemble":
            chapters_dir = args.get("chapters_dir") or "chapters"
            output_file = str(args.get("output_file", "")).strip() or None
            title = str(args.get("title", "")).strip() or None
            subtitle = str(args.get("subtitle", "")).strip() or None
            author = str(args.get("author", "")).strip() or None
            dependency = str(args.get("dependency", "")).strip() or None
            date = str(args.get("date", "")).strip() or None
            mode = str(args.get("mode", "")).strip() or None
            engine = str(args.get("engine", "")).strip() or None
            theme = str(args.get("theme", "")).strip() or None
            aspect_ratio = str(args.get("aspect_ratio", "")).strip() or None
            pattern = str(args.get("pattern", "")).strip() or "*.md"
            add_pagebreaks = args.get("add_pagebreaks", True)
            workspace_dir = args.get("workspace_dir") or "."

            work_path = Path(workspace_dir).resolve()
            ch_path = work_path / chapters_dir if not Path(chapters_dir).is_absolute() else Path(chapters_dir)
            if not ch_path.is_dir():
                return {"status": "error", "error": f"Chapters directory not found: {ch_path}"}

            with contextlib.redirect_stdout(sys.stderr):
                ok = assemble_documents(
                    chapters_dir=str(ch_path),
                    output_filename=output_file,
                    mode=mode,
                    title=title,
                    subtitle=subtitle,
                    author=author,
                    dependency=dependency,
                    date=date,
                    engine=engine,
                    theme=theme,
                    aspect_ratio=aspect_ratio,
                    pattern=pattern,
                    add_pagebreaks=bool(add_pagebreaks),
                    base_dir=work_path,
                )

            if not ok:
                return {"status": "error", "error": f"Failed to assemble chapters from {ch_path}"}

            final_mode = normalize_mode(mode)
            if output_file:
                out_path = work_path / output_file if not Path(output_file).is_absolute() else Path(output_file)
            else:
                out_path = work_path / ("slides.md" if final_mode == "slides" else "report.md")

            chapter_files = [f.name for f in resolve_ordered_chapter_files(work_path, ch_path, pattern=pattern)]

            return {
                "status": "ok",
                "output_file": str(out_path),
                "mode": final_mode,
                "chapters_count": len(chapter_files),
                "chapter_files": chapter_files,
                "size_bytes": out_path.stat().st_size if out_path.is_file() else 0,
            }

        else:
            return {"status": "error", "error": f"Unknown tool: {name}"}

    except Exception as e:
        return {"status": "error", "error": str(e)}


class StdioMCPServer:
    """JSON-RPC 2.0 stdio server implementing the Model Context Protocol."""

    def __init__(self) -> None:
        self.server_info = {"name": "snowpack", "version": __version__}

    def handle_request(self, req: dict[str, Any]) -> dict[str, Any] | None:
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": self.server_info,
                    "capabilities": {"tools": {}},
                },
            }

        elif method == "notifications/initialized":
            return None

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOL_DEFINITIONS},
            }

        elif method == "tools/call":
            params = req.get("params", {})
            name = params.get("name", "")
            args = params.get("arguments", {})
            res = execute_tool(name, args)
            is_error = res.get("status") == "error"

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": is_error,
                },
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

    def run(self) -> int:
        """Run JSON-RPC event loop reading lines from sys.stdin."""
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                req = json.loads(line_str)
                resp = self.handle_request(req)
                if resp is not None:
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                err_resp = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {e}"},
                }
                sys.stdout.write(json.dumps(err_resp) + "\n")
                sys.stdout.flush()
        return 0


def main() -> int:
    """Entry point for `snowpack mcp`."""
    return StdioMCPServer().run()
