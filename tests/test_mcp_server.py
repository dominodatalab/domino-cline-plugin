"""Functional tests for the domino_mcp_server."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

MCP_DIR = Path(__file__).resolve().parent.parent / "mcp-servers" / "domino_mcp_server"
sys.path.insert(0, str(MCP_DIR))


class TestLoadClusters:
    """Credentials loader — verifies the .env resolution chain."""

    def test_loader_prefers_home_domino(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.setenv("DOMINO_CLUSTERS", "test123")
            mp.setenv("DOMINO_HOST_TEST123", "https://test123.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_TEST123", "fake-key-123")
            clusters = m._load_clusters()
        assert "test123" in clusters
        assert clusters["test123"]["host"] == "https://test123.cs.domino.tech"

    def test_loader_returns_empty_with_no_config(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.delenv("DOMINO_CLUSTERS", raising=False)
            mp.delenv("DOMINO_HOST", raising=False)
            mp.delenv("DOMINO_API_KEY", raising=False)
            clusters = m._load_clusters()
        assert clusters == {}

    def test_loader_single_cluster_legacy(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.delenv("DOMINO_CLUSTERS", raising=False)
            mp.setenv("DOMINO_HOST", "https://single.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY", "fakekey")
            clusters = m._load_clusters()
        assert "default" in clusters
        assert clusters["default"]["host"] == "https://single.cs.domino.tech"

    def test_default_cluster_first_alias(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.setenv("DOMINO_CLUSTERS", "a,b,c")
            mp.setenv("DOMINO_HOST_A", "https://a.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_A", "ka")
            mp.setenv("DOMINO_HOST_B", "https://b.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_B", "kb")
            mp.setenv("DOMINO_HOST_C", "https://c.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_C", "kc")
            clusters = m._load_clusters()
        assert m._default_cluster_alias(clusters) == "a"


class TestResolveCluster:
    def test_resolve_explicit_cluster(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.setenv("DOMINO_CLUSTERS", "x,y")
            mp.setenv("DOMINO_HOST_X", "https://x.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_X", "kx")
            mp.setenv("DOMINO_HOST_Y", "https://y.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_Y", "ky")
            resolved = m._resolve_cluster("y")
        assert resolved["host"] == "https://y.cs.domino.tech"

    def test_resolve_unknown_cluster_raises(self, monkeypatch):
        import domino_mcp_server as m

        with monkeypatch.context() as mp:
            mp.setenv("DOMINO_CLUSTERS", "x")
            mp.setenv("DOMINO_HOST_X", "https://x.cs.domino.tech")
            mp.setenv("DOMINO_API_KEY_X", "kx")
            with pytest.raises(ValueError, match="Unknown cluster"):
                m._resolve_cluster("nonexistent")


class TestCheckAccess:
    def test_check_access_returns_structure(self, monkeypatch):
        import domino_mcp_server as m

        with patch.object(m, "_get_domino_host", return_value="https://mock.domino.tech"), \
             patch.object(m, "_get_auth_headers", return_value={"Fake": "header"}), \
             patch("domino_mcp_server.requests.get") as mock_get:

            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = [{"id": "p1"}, {"id": "p2"}]

            result = m.check_domino_api_access()
        assert result["access"] is True
        assert result["host"] == "https://mock.domino.tech"
        assert result["status"] == 200
        assert result["project_count"] == 2

    def test_check_access_handles_401(self, monkeypatch):
        import domino_mcp_server as m

        with patch.object(m, "_get_domino_host", return_value="https://mock.domino.tech"), \
             patch.object(m, "_get_auth_headers", return_value={"Fake": "header"}), \
             patch("domino_mcp_server.requests.get") as mock_get:

            mock_get.return_value.status_code = 401
            mock_get.return_value.json.return_value = {}

            result = m.check_domino_api_access()
        assert result["access"] is False
        assert "expired or invalid" in result["error"].lower()
        assert "regenerate" in result["error"].lower()

    def test_check_access_handles_connection_error(self, monkeypatch):
        import domino_mcp_server as m
        import requests

        with patch.object(m, "_get_domino_host", return_value="https://mock.domino.tech"), \
             patch.object(m, "_get_auth_headers", return_value={"Fake": "header"}), \
             patch("domino_mcp_server.requests.get",
                   side_effect=requests.exceptions.ConnectionError("no route")):

            result = m.check_domino_api_access()
        assert result["access"] is False
        assert "cannot connect" in result["error"].lower()


class TestIsDominoWorkspace:
    def test_false_outside(self, monkeypatch):
        import domino_mcp_server as m
        with monkeypatch.context() as mp:
            mp.delenv("DOMINO_API_HOST", raising=False)
        assert not m._is_domino_workspace()

    def test_true_inside(self, monkeypatch):
        import domino_mcp_server as m
        with monkeypatch.context() as mp:
            mp.setenv("DOMINO_API_HOST", "https://prod.cs.domino.tech")
            assert m._is_domino_workspace()