# CLI & Compilation Recipes

Snowpack exposes a comprehensive command-line interface supporting direct compilation, project scaffolding, multi-chapter assembly, and watch daemons.

---

## Command Reference

The primary entry point is the `snowpack` binary:

```text
Usage:
  snowpack [file] [options]             Build PDF from Markdown, Typst, or LaTeX
  snowpack build [file] [options]       Explicit build command
  snowpack new [target] [options]       Scaffold a new document (report, slides, paper)
  snowpack init [preset] [options]      Initialize complete Snowpack workspace
  snowpack assemble [dir] [options]     Assemble modular chapters into master document
  snowpack mcp                          Run Model Context Protocol stdio server

Operating Modes:
  -m, --mode MODE        Document operating mode:
                         • report: Minimal sans-serif document (default, A4/Letter)
                         • slides: 16:9 widescreen presentation (1920x1080)
                         • paper:  Academic paper (IEEE 2-column layout)
  -p, --preset PRESET    Layout preset (e.g. 'ieee', 'default')

Compilation Options:
  -o, --output PATH      Specify output PDF filename
  -t, --template PATH    Use custom Typst template file
  -w, --watch            Watch mode: recompile automatically on file changes
  --engine ENGINE        Compiler engine: 'typst' (default) or 'tectonic'
  --root PATH            Typst compilation root directory (default: current directory)
  --font-path PATH       Additional directory containing fonts for Typst
  --open                 Open generated PDF in system viewer after build
  -f, --format FMT       Document format for scaffolding: typ (default), md, tex
  --force                Overwrite existing files during init without prompting

Metadata Options:
  --title TITLE          Document title for 'new' / 'init'
  --author AUTHOR        Document author for 'new' / 'init'
  --theme THEME          Presentation theme ('dark' or 'light')

Agent & Telemetry Options:
  -A, --agent            Compact machine/agent friendly output mode
  --json                 Structured JSON output mode
  --toon                 Token-Oriented Object Notation (TOON) output mode
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored output
  -h, --help             Show help message and exit
  -V, -v, --version      Show version information and exit
```

---

## Document Modes and Layouts

### 1. Report Mode (Default)

Designed for single-column technical reports, specifications, and whitepapers. Uses crisp Inter typography, proportional line heights, subtle borders, and automatic headers.

```bash
# Build report with explicit output path
snowpack report.md -m report -o dist/report.pdf
```

### 2. Presentation Slides Mode

Compiles 16:9 widescreen slide decks (1920×1080). Markdown sections or horizontal rules (`---`) delimit individual slides.

```bash
# Build presentation with dark theme and live watch mode
snowpack slides.md -m slides --theme dark -w
```

### 3. Academic Paper Mode

Formats camera-ready papers in the standard IEEE two-column format. It processes abstract, keywords, and Roman numeral headings (`I. INTRODUCTION`, `II. RELATED WORK`).

```bash
# Compile IEEE paper
snowpack paper.md -m paper -p ieee
```

---

## Compilation Recipes

### Compile Native Typst Document

Snowpack passes native `.typ` source files directly to the Typst compiler with root path anchoring:

```bash
snowpack main.typ --root . -w
```

### Compile Native LaTeX with Tectonic

Directly build complex LaTeX documents without managing TeX Live trees:

```bash
snowpack manuscript.tex --engine tectonic
```

### Overriding the Markdown Engine

By default, Markdown files are converted and rendered via Typst. You can route Markdown through Tectonic LaTeX instead:

```bash
snowpack paper.md --engine tectonic
```

Or declare it in the file's YAML frontmatter:

```markdown
---
title: "Distributed Factor Graphs for Multi-Robot Localization"
author: "Alex Rivera"
engine: "tectonic"
mode: "paper"
---
```

---

## Chapter Assembly

When working on large manuscripts, split content into separate files within a directory:

```text
book/
├── 01_introduction.md
├── 02_problem_formulation.md
├── 03_convex_relaxations.md
├── 04_experimental_results.md
└── manifest.yaml (optional)
```

Assemble all chapters into a unified master document ready for compilation:

```bash
# Assemble directory into master Markdown document
snowpack assemble ./book -o master.md

# Compile the assembled master document to PDF
snowpack master.md -m report -o dist/book.pdf
```

---

## Machine Output and MCP

Snowpack is designed to integrate cleanly with automated agent loops and CI pipelines:

### JSON and Agent Modes

To receive structured compilation metadata rather than terminal UI decorations:

```bash
# JSON output
snowpack report.md --json

# Compact Agent mode (plain text with zero ANSI noise)
snowpack report.md --agent
```

### Model Context Protocol (MCP)

Snowpack includes a built-in MCP stdio server that enables LLM agents to inspect, scaffold, and compile documents without raw shell execution:

```bash
snowpack mcp
```

The MCP server exposes tools:
- `build_pdf`: Compiles target files with mode, preset, and engine options.
- `assemble`: Aggregates multi-chapter directories.
- `discover_documents`: Scans current workspace for compile targets.
