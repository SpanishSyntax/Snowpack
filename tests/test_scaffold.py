"""Tests for Snowpack document scaffolding, templates, and workspace init."""

import tempfile
from pathlib import Path

from snowpack.manifests import generate_packages_manifest
from snowpack.scaffold import (
    init_workspace,
    new_document,
    render_template_content,
    resolve_document_specs,
)


def test_resolve_document_specs():
    assert resolve_document_specs("slides") == ("slides", "typ", "slides.typ")
    assert resolve_document_specs("slides.md") == ("slides", "md", "slides.md")
    assert resolve_document_specs("paper.tex") == ("paper", "tex", "paper.tex")
    assert resolve_document_specs("report", format_hint="md") == (
        "report",
        "md",
        "report.md",
    )
    assert resolve_document_specs("presentation") == ("slides", "typ", "slides.typ")
    assert resolve_document_specs("article.typ") == ("paper", "typ", "paper.typ")


def test_render_template_content():
    template = "Title: __TITLE__ | Author: __AUTHOR__ | Theme: __THEME__"
    rendered = render_template_content(
        template,
        title="Optimal Control",
        author="Alice",
        theme="light",
    )
    assert rendered == "Title: Optimal Control | Author: Alice | Theme: light"


def test_new_document_slides_typ():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        doc = new_document(
            target_or_mode="slides",
            directory=tmp_path,
            title="Quantum Stepper",
            author="Dr. Turing",
            theme="dark",
        )
        assert doc.exists()
        assert doc.name == "slides.typ"
        content = doc.read_text(encoding="utf-8")
        assert "Quantum Stepper" in content
        assert "Dr. Turing" in content
        assert "slides.with" in content
        # Companion files
        assert (tmp_path / "packages.typ").exists()
        assert (tmp_path / "library.bib").exists()


def test_new_document_paper_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        doc = new_document(
            target_or_mode="paper.md",
            directory=tmp_path,
            title="Consensus Graph",
        )
        assert doc.exists()
        assert doc.name == "paper.md"
        content = doc.read_text(encoding="utf-8")
        assert "Consensus Graph" in content
        assert 'mode: "paper"' in content


def test_init_workspace():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        res = init_workspace(
            directory=tmp_path,
            mode="report",
            format_hint="typ",
            title="Laboratory Report",
        )
        assert res["status"] == "ok"
        assert (tmp_path / "report.typ").exists()
        assert (tmp_path / "packages.typ").exists()
        assert (tmp_path / "library.bib").exists()
        assert (tmp_path / ".gitignore").exists()


def test_packages_manifest():
    typ_manifest = generate_packages_manifest("typst")
    assert "@preview/cetz" in typ_manifest
    assert "@preview/fletcher" in typ_manifest
    assert "@preview/physica" in typ_manifest

    tex_manifest = generate_packages_manifest("latex")
    assert "amsmath" in tex_manifest
    assert "booktabs" in tex_manifest
