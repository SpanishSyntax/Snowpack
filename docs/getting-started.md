# Getting Started

Snowpack is designed to work out of the box with zero external configuration when packaged through Nix, while also providing standalone Python installation for standard environments.

---

## Installation

### Nix Flake (Recommended)

Snowpack is natively packaged with a hermetic Nix Flake bundling `typst`, `tectonic`, and `pandoc` into its runtime environment:

```bash
# Run directly without installation
nix run github:SpanishSyntax/Snowpack -- report.md

# Enter an interactive shell with snowpack available
nix shell github:SpanishSyntax/Snowpack
```

To add Snowpack to your system or Home Manager configuration, add it to your `flake.nix` inputs:

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
    homeConfigurations."usurper" = home-manager.lib.homeManagerConfiguration {
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

### Python Package (pip / uv)

If running outside Nix, Snowpack can be installed as a standard Python package:

```bash
# Using uv (fastest)
uv tool install git+https://github.com/SpanishSyntax/Snowpack.git

# Using pip
pip install git+https://github.com/SpanishSyntax/Snowpack.git
```

---

## Prerequisites and Toolchain

When installed via Nix, all required compiler backends are automatically linked. If installing via Python `pip` or running from source, ensure the following tools are available on your system `PATH`:

| Tool | Minimum Version | Required By | Purpose |
| :--- | :--- | :--- | :--- |
| `typst` | `>= 0.11.0` | Default Engine | Native compilation of `.typ` files and generated Typst ASTs |
| `pandoc` | `>= 3.1.0` | Markdown Parser | Markdown AST transformation and metadata extraction |
| `tectonic` | `>= 0.15.0` | LaTeX Engine | Self-contained modern XeTeX compiler engine |

To verify that your local environment has the necessary toolchains:

```bash
snowpack --version
```

If any compiler binary is missing, Snowpack displays a diagnostic alert indicating which tool is absent and how to provision it.

---

## Quick Start

### 1. Initialize a Starter Document

Create a minimal report document in your workspace:

```bash
snowpack new report --title "Optimal Trajectory Planning" --author "Dr. Alex Rivera"
```

This creates a starter `report.typ` (or `report.md` when using `--format md`) with preconfigured frontmatter and section hierarchy.

### 2. Compile to PDF

Compile the document in the current directory:

```bash
# Snowpack auto-discovers report.md, slides.md, or paper.md
snowpack

# Or specify the file explicitly
snowpack report.md
```

The output PDF is written to the same directory as the source file (e.g., `report.pdf`).

### 3. Live Watch Mode

To continuously recompile on every document save:

```bash
snowpack report.md -w
```

Snowpack starts a background watcher that detects disk writes, rebuilds the target document within milliseconds, and reports compilation status directly to the terminal.

---

## Basecamp Scaffolding

For complex multi-document repositories, project scaffolding can also be delegated to [Basecamp](https://github.com/SpanishSyntax/Basecamp):

```bash
# Initialize a complete Snowpack workspace with standard templates
basecamp init snowpack

# Drop starter document leaves into an existing workspace
basecamp new snowpack
```
