# Configuration & API Reference

This reference covers the YAML frontmatter specification, Nix integration options, and the Python programmatic API.

---

## YAML Frontmatter Schema

Snowpack extracts metadata from standard YAML frontmatter blocks positioned at the top of Markdown files.

### Common Fields

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `string` | `"Untitled"` | Primary document title |
| `subtitle` | `string` | `""` | Secondary subtitle or context string |
| `author` | `string \| list` | `""` | Primary author name or list of author strings |
| `date` | `string` | Today's Date | Publication date formatted as string |
| `mode` | `string` | `"report"` | Operating layout: `report`, `slides`, or `paper` |
| `preset` | `string` | `"default"` | Sub-preset layout (e.g. `ieee` for academic papers) |
| `engine` | `string` | `"typst"` | Compilation backend: `typst` or `tectonic` |
| `lang` | `string` | `"en"` | BCP 47 language code for hyphenation rules |

### Report Mode Fields

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `affiliation` | `string` | `""` | Department, laboratory, or institutional affiliation |
| `version` | `string` | `""` | Document version or revision string (e.g., `v1.2.0`) |
| `paper` | `string` | `"a4"` | Paper size: `a4`, `us-letter`, etc. |
| `margin` | `string \| dict` | `"2.5cm"` | Page margins (scalar or `{ top, bottom, left, right }`) |

### Presentation Slides Mode Fields

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `theme` | `string` | `"dark"` | Slide deck visual theme: `dark` (slate) or `light` |
| `aspect-ratio` | `string` | `"16-9"` | Slide dimensions: `16-9` (1920×1080) or `4-3` |
| `footer` | `string` | `""` | Custom running slide deck footer string |

### Paper Mode Fields

| Key | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `abstract` | `string` | `""` | Formal academic abstract paragraph |
| `keywords` | `string \| list`| `""` | Indexed keywords or subject categories |
| `email` | `string` | `""` | Corresponding author email address |
| `doi` | `string` | `""` | Digital Object Identifier string |

---

## Nix Flake and Home Manager

### Flake Input Declaration

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    snowpack.url = "github:SpanishSyntax/Snowpack";
    snowpack.inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

### Home Manager Configuration

Enable Snowpack within your Home Manager configuration:

```nix
{
  programs.snowpack = {
    enable = true;
  };
}
```

When enabled, the `snowpack` binary is linked to your user profile along with its packaged dependencies (`typst`, `tectonic`, `pandoc`).

---

## Python API Reference

Snowpack exposes a Python library interface for invoking compiler actions in-process without invoking shell subshells:

```python
import pathlib
from snowpack.compiler import build_pdf, compile_markdown_typst
from snowpack.assembler import assemble_documents
from snowpack.frontmatter import parse_frontmatter
from snowpack.discovery import discover_workspace_documents
```

### `build_pdf`

Compiles a source file into a PDF artifact.

```python
def build_pdf(
    source_file: pathlib.Path,
    output_pdf: pathlib.Path | None = None,
    mode: str | None = None,
    preset: str | None = None,
    engine: str = "typst",
    template: pathlib.Path | None = None,
    root: pathlib.Path | None = None,
    font_path: pathlib.Path | None = None,
) -> pathlib.Path:
    """Compiles Markdown, Typst, or LaTeX source files into a target PDF.
    
    Returns:
        pathlib.Path: Absolute path to the generated PDF.
    Raises:
        FileNotFoundError: If source file is missing.
        RuntimeError: If underlying compiler backend fails.
    """
```

### `assemble_documents`

Combines a directory of modular chapter files into a unified document.

```python
def assemble_documents(
    source_dir: pathlib.Path,
    output_path: pathlib.Path,
    manifest_path: pathlib.Path | None = None,
) -> pathlib.Path:
    """Collates markdown or typst chapters in natural sort order.
    
    Returns:
        pathlib.Path: Path to the assembled master document.
    """
```

### `parse_frontmatter`

Extracts YAML frontmatter and document body from raw Markdown text.

```python
def parse_frontmatter(content: str) -> tuple[dict[str, any], str]:
    """Parses leading YAML frontmatter block from markdown text.
    
    Returns:
        tuple[dict, str]: Extracted metadata dictionary and remaining body content.
    """
```

---

## Template Customization

Snowpack allows overriding the default Typst templates by passing `--template PATH`:

```bash
snowpack report.md --template custom_template.typ
```

In your custom Typst template, bind the standard parameters:

```typst
#let report(
  title: "Untitled",
  authors: (),
  affiliation: "",
  date: none,
  body,
) = {
  set document(title: title, author: authors)
  set text(font: "Inter", size: 10.5pt, fill: rgb("#0F172A"))
  set page(paper: "a4", margin: (x: 2.5cm, y: 2.8cm))
  
  // Custom cover or title plaque
  v(1cm)
  text(size: 20pt, weight: "bold", title)
  v(0.5em)
  text(size: 11pt, fill: rgb("#475569"), affiliation)
  v(2em)
  
  body
}
```
