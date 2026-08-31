"""Functional tests for scripts/domino-tsh.

The script has no .py extension (it's a standalone executable), so it's
loaded via importlib rather than a normal import statement — see the `dtsh`
fixture below.
"""

import importlib.machinery
import importlib.util
import json
import subprocess
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "domino-tsh"


@pytest.fixture
def dtsh():
    """Fresh module object per test — avoids any state leaking between
    tests beyond what monkeypatch/os.environ already isolate.

    `spec_from_file_location` can't infer a loader for an extensionless
    file, so it's given one explicitly (SourceFileLoader) rather than
    relying on suffix-based detection.
    """
    loader = importlib.machinery.SourceFileLoader("domino_tsh", str(SCRIPT_PATH))
    spec = importlib.util.spec_from_loader("domino_tsh", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class TestEnvKey:
    def test_simple_alias(self, dtsh):
        assert dtsh._env_key("marcdo126967") == "MARCDO126967"

    def test_hyphens_and_dots_become_underscores(self, dtsh):
        assert dtsh._env_key("my-cluster.prod") == "MY_CLUSTER_PROD"


class TestClusterConfig:
    def test_proxy_and_explicit_cluster_name(self, dtsh, monkeypatch):
        monkeypatch.setenv("TELEPORT_PROXY_FOO", "dominodatalab.teleport.sh:443")
        monkeypatch.setenv("TELEPORT_CLUSTER_NAME_FOO", "actual-kube-name")
        proxy, kube_name = dtsh._cluster_config("foo")
        assert proxy == "dominodatalab.teleport.sh:443"
        assert kube_name == "actual-kube-name"

    def test_cluster_name_defaults_to_alias(self, dtsh, monkeypatch):
        monkeypatch.setenv("TELEPORT_PROXY_FOO", "dominodatalab.teleport.sh:443")
        monkeypatch.delenv("TELEPORT_CLUSTER_NAME_FOO", raising=False)
        _, kube_name = dtsh._cluster_config("foo")
        assert kube_name == "foo"

    def test_missing_proxy_exits(self, dtsh, monkeypatch):
        monkeypatch.delenv("TELEPORT_PROXY_MISSING", raising=False)
        with pytest.raises(SystemExit, match="TELEPORT_PROXY_MISSING"):
            dtsh._cluster_config("missing")


class TestCandidateBinaries:
    def test_override_env_var(self, dtsh, monkeypatch):
        monkeypatch.setenv("DOMINO_TSH_CANDIDATES", "tsh, tsh7 , custom-bin")
        assert dtsh._candidate_binaries() == ["tsh", "tsh7", "custom-bin"]

    def test_path_scan_finds_tsh_like_executables(self, dtsh, monkeypatch, tmp_path):
        monkeypatch.delenv("DOMINO_TSH_CANDIDATES", raising=False)
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        for name in ("tsh", "tsh7", "not-relevant", "tsh-dir"):
            f = bin_dir / name
            f.write_text("#!/bin/sh\n")
            f.chmod(0o755)
        (bin_dir / "tsh-dir").unlink()
        (bin_dir / "tsh-dir").mkdir()  # directories should be excluded even if named like a match
        monkeypatch.setenv("PATH", str(bin_dir))

        found = set(dtsh._candidate_binaries())
        assert found == {"tsh", "tsh7"}

    def test_path_scan_excludes_non_executable(self, dtsh, monkeypatch, tmp_path):
        monkeypatch.delenv("DOMINO_TSH_CANDIDATES", raising=False)
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        f = bin_dir / "tsh-noexec"
        f.write_text("not executable")
        f.chmod(0o644)
        monkeypatch.setenv("PATH", str(bin_dir))

        assert dtsh._candidate_binaries() == []


class TestClientMajorVersion:
    def test_parses_version_from_output(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh.shutil, "which", lambda b: f"/usr/local/bin/{b}")
        fake = MagicMock(stdout="Teleport v7.3.26 git:v7.3.26-0-g7a8ba8822 go1.18.4\n", stderr="")
        with patch.object(dtsh.subprocess, "run", return_value=fake):
            assert dtsh._client_major_version("tsh7") == 7

    def test_parses_version_from_stderr(self, dtsh, monkeypatch):
        """tsh sometimes emits a compatibility WARNING before the version
        line — seen for real on this machine — and it isn't guaranteed to
        be on stdout, so the parser checks both streams."""
        monkeypatch.setattr(dtsh.shutil, "which", lambda b: f"/usr/local/bin/{b}")
        fake = MagicMock(
            stdout="WARNING\nDetected potentially incompatible client and server versions.\n",
            stderr="Teleport v18.1.2 git:v18.1.2-0 go1.22.0\n",
        )
        with patch.object(dtsh.subprocess, "run", return_value=fake):
            assert dtsh._client_major_version("tsh") == 18

    def test_binary_not_found(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh.shutil, "which", lambda b: None)
        assert dtsh._client_major_version("nonexistent") is None

    def test_unparseable_output_returns_none(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh.shutil, "which", lambda b: f"/usr/local/bin/{b}")
        fake = MagicMock(stdout="not a teleport binary at all\n", stderr="")
        with patch.object(dtsh.subprocess, "run", return_value=fake):
            assert dtsh._client_major_version("impostor") is None

    def test_subprocess_error_returns_none(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh.shutil, "which", lambda b: f"/usr/local/bin/{b}")
        with patch.object(dtsh.subprocess, "run", side_effect=subprocess.TimeoutExpired("tsh", 10)):
            assert dtsh._client_major_version("tsh") is None


class TestServerMajorVersion:
    def test_parses_server_version(self, dtsh):
        fake_resp = MagicMock()
        fake_resp.read.return_value = json.dumps({"server_version": "18.1.2"}).encode()
        fake_resp.__enter__.return_value = fake_resp
        with patch.object(dtsh.urllib.request, "urlopen", return_value=fake_resp):
            assert dtsh._server_major_version("dominodatalab.teleport.sh:443") == 18

    def test_missing_server_version_field_exits(self, dtsh):
        fake_resp = MagicMock()
        fake_resp.read.return_value = json.dumps({"no_version_here": True}).encode()
        fake_resp.__enter__.return_value = fake_resp
        with patch.object(dtsh.urllib.request, "urlopen", return_value=fake_resp):
            with pytest.raises(SystemExit, match="server_version"):
                dtsh._server_major_version("dominodatalab.teleport.sh:443")

    def test_unreachable_proxy_exits(self, dtsh):
        with patch.object(dtsh.urllib.request, "urlopen",
                          side_effect=urllib.error.URLError("no route to host")):
            with pytest.raises(SystemExit, match="Could not reach"):
                dtsh._server_major_version("unreachable.example.com:443")


class TestSelectBinary:
    def test_prefers_exact_major_match_over_one_behind(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh, "_server_major_version", lambda proxy: 18)
        monkeypatch.setattr(dtsh, "_candidate_binaries", lambda: ["tsh17", "tsh18"])
        versions = {"tsh17": 17, "tsh18": 18}
        monkeypatch.setattr(dtsh, "_client_major_version", lambda b: versions[b])

        binary, client_major, server_major = dtsh._select_binary("some-proxy:443")
        assert binary == "tsh18"
        assert client_major == 18
        assert server_major == 18

    def test_accepts_one_major_behind_when_no_exact_match(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh, "_server_major_version", lambda proxy: 18)
        monkeypatch.setattr(dtsh, "_candidate_binaries", lambda: ["tsh7", "tsh17"])
        versions = {"tsh7": 7, "tsh17": 17}
        monkeypatch.setattr(dtsh, "_client_major_version", lambda b: versions[b])

        binary, client_major, _ = dtsh._select_binary("some-proxy:443")
        assert binary == "tsh17"
        assert client_major == 17

    def test_real_world_dev_and_prod_split(self, dtsh, monkeypatch):
        """Mirrors this repo's actual setup: tsh (v18) and tsh7 (v7) installed,
        dev proxy needs v7."""
        monkeypatch.setattr(dtsh, "_server_major_version", lambda proxy: 7)
        monkeypatch.setattr(dtsh, "_candidate_binaries", lambda: ["tsh", "tsh7"])
        versions = {"tsh": 18, "tsh7": 7}
        monkeypatch.setattr(dtsh, "_client_major_version", lambda b: versions[b])

        binary, client_major, server_major = dtsh._select_binary("dev-teleport.domino.tech:443")
        assert binary == "tsh7"
        assert client_major == 7
        assert server_major == 7

    def test_no_compatible_binary_exits_with_actionable_message(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh, "_server_major_version", lambda proxy: 18)
        monkeypatch.setattr(dtsh, "_candidate_binaries", lambda: ["tsh7"])
        monkeypatch.setattr(dtsh, "_client_major_version", lambda b: 7)

        with pytest.raises(SystemExit, match="major version 18 or 17"):
            dtsh._select_binary("some-proxy:443")

    def test_no_candidates_found_exits(self, dtsh, monkeypatch):
        monkeypatch.setattr(dtsh, "_server_major_version", lambda proxy: 18)
        monkeypatch.setattr(dtsh, "_candidate_binaries", lambda: [])

        with pytest.raises(SystemExit, match="No tsh-like binaries found"):
            dtsh._select_binary("some-proxy:443")
