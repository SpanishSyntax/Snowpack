<p align="center">
  <img src="assets/banner.png" alt="Deep snowpack fracture line and winter alpine crown" width="100%" />
</p>

# Snowpack 📝

> Hermetic Multi-Mode Document & Presentation Compiler (Typst + LaTeX)

Snowpack is an opinionated, hermetic document compiler that transforms GitHub Flavored Markdown (GFM), Typst, and LaTeX into publication-grade PDFs, IEEE academic papers, and 16:9 widescreen presentation slide decks.

---

## Why "Snowpack"? (The Lore)

> **snowpack** (`/ˈsnəʊ.pæk/`) — *noun:* The perennial mass of dense snow that accumulates in polar latitudes, compressed layer upon layer over seasons into an impenetrable, stratified geological formation.

Each winter season adds fresh snowfall atop the glacier. Over time, immense pressure compresses loose crystals into dense, stratified layers of permanent blue ice.

Snowpack compresses multi-layered technical manuscripts into definitive publications:
- **Stratified Compilation**: Blends GitHub Flavored Markdown, Typst, and LaTeX into cohesive academic papers, course readers, and presentation slide decks.
- **Hermetic Build Engine**: Guarantees reproducible PDF output with automated asset resolution, syntax styling, and typographic polish across diverse host environments.

---

## Core Features

- **Hermetic Toolchain Packaging**: Bundles `pandoc`, `typst`, and `tectonic` within its Nix closure, guaranteeing identical PDF compilation regardless of host dependencies.
- **Three Core Operating Modes**:
  - `report` (Default): Minimal sans-serif layout with Inter typography, running headers, footers, and callouts (A4/Letter).
  - `slides`: 16:9 widescreen presentation deck (1920×1080) with dark/light themes and automated slide pagination.
  - `paper`: IEEE two-column camera-ready layout with formal Roman section numbering, full-width abstract banners, and serif typography.
- **Polyglot Format Engine**:
  - Compiles standard Markdown documents via Typst or Tectonic LaTeX based on frontmatter or CLI flags.
  - Compiles native `.typ` source files directly via Typst.
  - Compiles native `.tex` source files directly via Tectonic.
- **YAML Frontmatter Integration**: Control title, authors, affiliations, operating mode, layout preset, engine backend, theme, and geometry directly from Markdown headers.
- **Live Watch Daemon**: Inotify-backed continuous compilation daemon that rebuilds PDFs upon filesystem changes in milliseconds.
- **Chapter Assembly**: Collates multi-chapter manuscript directories with natural sorting, manifest validation, and asset linking.
- **Model Context Protocol (MCP)**: Native stdio server exposing compilation, chapter discovery, and document inspection tools to AI agents.

---

## Operating Modes

| Mode | Target Layout | Primary Use Cases | Default Engine |
| :--- | :--- | :--- | :--- |
| `report` | Single-column A4/Letter | Engineering reports, course companions, project handbooks, whitepapers | Typst |
| `slides` | 16:9 Widescreen (1920×1080) | Lecture slides, conference presentations, technical defense decks | Typst |
| `paper` | Two-column IEEE | Academic submissions, conference proceedings, camera-ready papers | Typst / Tectonic |

---

## Quick Navigation

- [Getting Started](getting-started.md): Installation methods via Nix Flakes or pip, prerequisites, and starter workflows.
- [Architecture & Pipeline](architecture.md): Deep-dive into the compiler pipeline, AST conversion, and execution guarantees.
- [CLI & Compilation Recipes](usage.md): Comprehensive command options, mode configurations, and assembly pipelines.
- [Configuration & API Reference](api.md): YAML frontmatter schema, Python library methods, and Nix module integration.
