<p align="center">
  <img src="assets/banner.png" alt="Deep snowpack fracture line and winter alpine crown" width="100%" />
</p>

# Snowpack 📝

> Hermetic Multi-Mode Document & Presentation Compiler (Typst + LaTeX)

Snowpack is an opinionated, hermetic document compiler that turns standard GitHub Flavored Markdown (GFM), Typst, and LaTeX into publication-grade PDFs, IEEE academic papers, and 16:9 widescreen presentation slide decks.

[![Documentation](https://img.shields.io/badge/docs-GitHub_Pages-blue.svg)](https://spanishsyntax.github.io/Snowpack)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Why "Snowpack"? (The Lore)

> **snowpack** (`/ˈsnəʊ.pæk/`) — *noun:* The perennial mass of dense snow that accumulates in polar latitudes, compressed layer upon layer over seasons into an impenetrable, stratified geological formation.

Each winter season adds fresh snowfall atop the glacier. Over time, immense pressure compresses loose crystals into dense, stratified layers of permanent blue ice.

Snowpack compresses multi-layered technical manuscripts into definitive publications:
- **Stratified Compilation**: Blends GitHub Flavored Markdown, Typst, and LaTeX into cohesive academic papers, course readers, and presentation slide decks.
- **Hermetic Build Engine**: Guarantees reproducible PDF output with automated asset resolution, syntax styling, and typographic polish.

---

## Features

- **Hermetic Toolchain**: Packages `pandoc`, `typst`, and `tectonic` inside its Nix closure, guaranteeing identical PDF compilation across any host machine.
- **Three Core Operating Modes**:
  - `report` (Default): Clean minimal sans-serif report layout with Inter, dynamic margins, headers, footers, and callouts (A4/Letter).
  - `slides` (16:9 Presentation): High-contrast 16:9 widescreen presentation deck (1920×1080) with dark/light themes and automatic slide pagination.
  - `paper` (IEEE Academic Paper): Two-column camera-ready layout with IEEE Roman section numbering, full-width abstract banner, and serif typography.
- **Polyglot Format Engine**:
  - Compiles Markdown via Typst or LaTeX/Tectonic based on frontmatter `engine: typst | latex` (or `--engine`).
  - Compiles native `.typ` files directly with Typst (`typst:report`, `typst:slides`, `typst:paper`).
  - Compiles native `.tex` files directly with Tectonic (`latex:report`, `latex:slides`, `latex:paper`).
- **YAML Frontmatter Integration**: Control title, authors, affiliations, operating mode, layout presets, engine backends, themes, and geometry directly from Markdown headers.
- **Live Watch Mode**: Continuous inotify-backed background watcher that detects file saves and automatically recompiles the PDF in milliseconds.
- **Chapter Assembly**: Collates multi-chapter manuscript directories with natural numerical sorting, path rebasing, and manifest validation.
- **Basecamp Integration**: Scaffolding is integrated with [Basecamp](https://github.com/SpanishSyntax/Basecamp) (`basecamp init snowpack`).

---

## Documentation

Full documentation, architecture deep dives, CLI recipes, and API references are available on the **[Documentation Site](https://spanishsyntax.github.io/Snowpack)**:

- [Getting Started](https://spanishsyntax.github.io/Snowpack/#/getting-started)
- [Architecture & Compiler Pipeline](https://spanishsyntax.github.io/Snowpack/#/architecture)
- [CLI Reference & Recipes](https://spanishsyntax.github.io/Snowpack/#/usage)
- [YAML Frontmatter & API Reference](https://spanishsyntax.github.io/Snowpack/#/api)

---

## Quick Start

### 1. Scaffold Document

```bash
# Initialize a starter report document
snowpack new report --title "Autonomous Exploration Systems" --author "Dr. Alex Rivera"
```

### 2. Compile to PDF

```bash
# Auto-discover report.md, slides.md, or paper.md in current directory
snowpack

# Compile a report explicitly
snowpack report.md

# Compile 16:9 presentation slides with live watch mode
snowpack slides.md -m slides -w

# Compile an IEEE 2-column academic paper
snowpack paper.md -m paper

# Directly compile native Typst or LaTeX documents
snowpack report.typ -w
snowpack report.tex -w
```

---

## CLI Overview

```text
Usage:
  snowpack [file] [options]             Build PDF from Markdown, Typst, or LaTeX
  snowpack build [file] [options]       Explicit build command
  snowpack new [target] [options]       Scaffold starter document
  snowpack init [preset] [options]      Initialize complete Snowpack workspace
  snowpack assemble [dir] [options]     Assemble modular chapters into master Markdown
  snowpack mcp                          Run Model Context Protocol stdio server

Operating Modes:
  -m, --mode MODE        Document operating mode:
                         • report: Minimal sans-serif document (default, A4/Letter)
                         • slides: 16:9 widescreen presentation (1920x1080)
                         • paper:  Academic paper (IEEE 2-column layout)
  -p, --preset PRESET    Layout preset (e.g. 'ieee', 'default')

Options:
  -o, --output PATH      Specify output PDF filename
  -t, --template PATH    Use custom Typst template file
  -w, --watch            Watch mode: recompile automatically on file changes
  --engine ENGINE        Compiler engine: 'typst' (default) or 'tectonic'
  --root PATH            Typst compilation root directory (default: current directory)
  --font-path PATH       Additional directory containing fonts for Typst
  --open                 Open generated PDF in system viewer after build
  -f, --format FMT       Scaffolding document format: typ (default), md, tex
  --force                Overwrite existing files during init without prompting
  -A, --agent            Compact machine/agent friendly output mode
  --json                 Structured JSON output mode
  --color MODE           Color output mode: auto, always, never (default: auto)
  --no-color             Disable colored output
  -h, --help             Show help message and exit
  -V, -v, --version      Show version information and exit
```

---

## Frontmatter Formats

Snowpack configures layout and styling from standard Markdown YAML frontmatter:

### 1. Presentation Slides (16:9 / 1920×1080)

```markdown
---
title: "Distributed Swarm Intelligence"
subtitle: "Real-time Consensus in GPS-Denied Environments"
author: "Alex Rivera"
affiliation: "Robotics and Controls Laboratory"
date: "October 2026"
mode: "slides"
theme: "dark"
aspect-ratio: "16-9"
---

# Problem Formulation
- Sensor limitations: $O(t^2)$ dead-reckoning drift
- Intermittent peer-to-peer wireless links

---

# Mathematical Formulation
Each agent minimizes relative pose error:
$$
\min_{\mathbf{x}_i} \sum_{j \in \mathcal{N}_i} \|\mathbf{x}_i - \mathbf{x}_j - \mathbf{d}_{ij}\|^2
$$
```

### 2. Academic Paper (IEEE 2-Column)

```markdown
---
title: "Resilient Distributed State Estimation for Autonomous Swarms"
author: "Alex Rivera, Member, IEEE, and Jordan Vance"
affiliation: "Autonomous Systems Laboratory"
email: "a.rivera@laboratory.org"
abstract: "Autonomous micro-aerial vehicle swarms face rapid dead-reckoning drift under GPS denial..."
keywords: "Swarm robotics, distributed factor graphs, ADMM."
mode: "paper"
preset: "ieee"
---

# Introduction
Autonomous multi-agent systems require distributed awareness under degraded communications...

# System Architecture
Consider an undirected communication graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$...
```

### 3. Report Document (Default)

```markdown
---
title: "Autonomous Space Exploration Systems"
author: "Alex Rivera"
affiliation: "Space Systems Group"
date: "2026-10-15"
mode: "report"
---

# Introduction
Minimal Inter typography with automatic headers, footers, and page counters.
```

---

## Home Manager Configuration

Add Snowpack to your `flake.nix`:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    snowpack = {
      url = "github:SpanishSyntax/Snowpack";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, snowpack, ... }: {
    homeConfigurations.user = home-manager.lib.homeManagerConfiguration {
      modules = [
        snowpack.homeManagerModules.default
        {
          programs.snowpack.enable = true;
        }
      ];
    };
  };
}
```

---

## Repository Structure

```text
Snowpack/
├── .github/workflows/      # CI/CD and Docs deployment workflows
├── docs/                   # Docsify documentation site
│   ├── assets/             # Documentation visual assets & banners
│   ├── index.html          # Docsify single-page application
│   ├── _sidebar.md         # Documentation navigation tree
│   ├── getting-started.md  # Installation & quick start
│   ├── architecture.md     # Compiler pipeline & internals
│   ├── usage.md            # CLI recipes & assembly guides
│   └── api.md              # Frontmatter schema & Python API
├── flake.nix               # Nix packaging wrapping pandoc, typst, and tectonic
├── pyproject.toml          # PEP 517 / 621 Python packaging
├── LICENSE                 # MIT License
├── README.md               # Repository landing page
└── src/
    └── snowpack/
        ├── assembler.py    # Multi-chapter collation & natural sorting
        ├── cli.py          # Command line router & status dashboard
        ├── compiler.py     # Subprocess runner for Typst, Tectonic & Pandoc
        ├── discovery.py    # Document detection & template resolution
        ├── frontmatter.py  # YAML frontmatter normalization
        ├── mcp.py          # Model Context Protocol stdio server
        └── watcher.py      # File system watch daemon
```

---

## License

MIT © [SpanishSyntax](https://github.com/SpanishSyntax)
