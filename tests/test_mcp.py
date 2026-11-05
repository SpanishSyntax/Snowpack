"""Unit tests for Snowpack Model Context Protocol (MCP) stdio server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snowpack.mcp import StdioMCPServer, execute_tool


def test_mcp_initialize() -> None:
    server = StdioMCPServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-agent", "version": "1.0"},
        },
    }
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "snowpack"
    assert resp["result"]["protocolVersion"] == "2024-11-05"


def test_mcp_tools_list() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_map = {t["name"]: t for t in tools}

    assert "snowpack_build" in tool_map
    assert "snowpack_assemble" in tool_map

    build_props = tool_map["snowpack_build"]["inputSchema"]["properties"]
    for expected_prop in [
        "input_file",
        "output_pdf",
        "mode",
        "preset",
        "engine",
        "template",
        "root_dir",
        "font_path",
    ]:
        assert expected_prop in build_props

    asm_props = tool_map["snowpack_assemble"]["inputSchema"]["properties"]
    for expected_prop in [
        "chapters_dir",
        "output_file",
        "title",
        "subtitle",
        "author",
        "dependency",
        "date",
        "mode",
        "theme",
        "aspect_ratio",
    ]:
        assert expected_prop in asm_props


def test_mcp_assemble(tmp_path: Path) -> None:
    server = StdioMCPServer()
    ch_dir = tmp_path / "chapters"
    ch_dir.mkdir()

    (ch_dir / "01_intro.md").write_text(
        "# Chapter 1: Foundations\nIntro content.\n", encoding="utf-8"
    )
    (ch_dir / "02_methods.md").write_text(
        "# Chapter 2: Methods\nMethods content.\n", encoding="utf-8"
    )

    out_file = tmp_path / "unified.md"
    req = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "snowpack_assemble",
            "arguments": {
                "chapters_dir": str(ch_dir),
                "output_file": str(out_file),
                "title": "Quantum Control Companion",
                "subtitle": "Lecture Notes",
                "author": "Antigravity Swarm",
                "mode": "report",
                "workspace_dir": str(tmp_path),
            },
        },
    }

    resp = server.handle_request(req)
    assert resp is not None
    assert resp["id"] == 10
    assert resp["result"]["isError"] is False

    content_data = json.loads(resp["result"]["content"][0]["text"])
    assert content_data["status"] == "ok"
    assert content_data["chapters_count"] == 2
    assert "01_intro.md" in content_data["chapter_files"]
    assert "02_methods.md" in content_data["chapter_files"]
    assert out_file.is_file()

    assembled_text = out_file.read_text(encoding="utf-8")
    assert 'title: "Quantum Control Companion"' in assembled_text
    assert 'author: "Antigravity Swarm"' in assembled_text
    assert "# Chapter 1: Foundations" in assembled_text
    assert "# Chapter 2: Methods" in assembled_text


def test_mcp_assemble_missing_dir(tmp_path: Path) -> None:
    res = execute_tool(
        "snowpack_assemble",
        {"chapters_dir": "nonexistent_dir", "workspace_dir": str(tmp_path)},
    )
    assert res["status"] == "error"
    assert "Chapters directory not found" in res["error"]


def test_mcp_execute_unknown() -> None:
    res = execute_tool("unknown_tool", {})
    assert res["status"] == "error"
    assert "Unknown tool" in res["error"]


def test_mcp_build_missing_file() -> None:
    res = execute_tool("snowpack_build", {"input_file": "nonexistent_file.md"})
    assert res["status"] == "error"
    assert "Source document not found" in res["error"]


def test_mcp_run_loop(monkeypatch: Any) -> None:
    import io

    input_stream = io.StringIO('{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n')
    output_stream = io.StringIO()
    monkeypatch.setattr("sys.stdin", input_stream)
    monkeypatch.setattr("sys.stdout", output_stream)
    server = StdioMCPServer()
    server.run()
    resp = json.loads(output_stream.getvalue())
    assert resp["id"] == 1
    assert resp["result"] == {}


def test_mcp_notifications_and_errors() -> None:
    server = StdioMCPServer()
    # Notification returns None
    assert (
        server.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"})
        is None
    )

    # Unknown method returns code -32601
    resp = server.handle_request(
        {"jsonrpc": "2.0", "id": 5, "method": "unknown/method"}
    )
    assert resp is not None
    assert resp["error"]["code"] == -32601


def test_mcp_ping() -> None:
    server = StdioMCPServer()
    req = {"jsonrpc": "2.0", "id": 99, "method": "ping"}
    resp = server.handle_request(req)
    assert resp == {"jsonrpc": "2.0", "id": 99, "result": {}}


def test_cli_mcp_dispatch(monkeypatch: Any) -> None:
    from snowpack.cli import main

    called = False

    def dummy_mcp_main() -> int:
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr("snowpack.mcp.main", dummy_mcp_main)
    ret = main(["mcp"])
    assert ret == 0
    assert called is True
