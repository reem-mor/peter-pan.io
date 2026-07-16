"""TDD tests for scripts/run_all_tests.py.

Tests the NEW behaviour: extending service-only discovery with ui/, n8n/,
and evaluation/ suites when a pytest.ini or tests/ directory is present.

Import strategy: use importlib to load the script without an __init__.py in
scripts/ (which is out of scope to create).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Load the module under test
# ---------------------------------------------------------------------------

_SCRIPT_PATH = Path(__file__).parent.parent.parent / "scripts" / "run_all_tests.py"


def _load_run_all_tests():
    spec = importlib.util.spec_from_file_location("run_all_tests", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


run_all_tests = _load_run_all_tests()


# ---------------------------------------------------------------------------
# Helper: build a fake service or suite directory
# ---------------------------------------------------------------------------

def _make_service(parent: Path, name: str, has_pytest_ini: bool = True) -> Path:
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    if has_pytest_ini:
        (d / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")
    return d


def _make_suite(parent: Path, name: str, *, has_pytest_ini: bool = False, has_tests_dir: bool = False) -> Path:
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    if has_pytest_ini:
        (d / "pytest.ini").write_text("[pytest]\ntestpaths = tests\n")
    if has_tests_dir:
        (d / "tests").mkdir(exist_ok=True)
    return d


# ---------------------------------------------------------------------------
# Tests for _has_pytest_suite helper
# ---------------------------------------------------------------------------


class TestHasPytestSuite:
    def test_returns_true_for_pytest_ini(self, tmp_path: Path) -> None:
        d = tmp_path / "suite"
        d.mkdir()
        (d / "pytest.ini").write_text("[pytest]\n")
        assert run_all_tests._has_pytest_suite(d) is True

    def test_returns_true_for_tests_dir(self, tmp_path: Path) -> None:
        d = tmp_path / "suite"
        d.mkdir()
        (d / "tests").mkdir()
        assert run_all_tests._has_pytest_suite(d) is True

    def test_returns_true_for_both(self, tmp_path: Path) -> None:
        d = tmp_path / "suite"
        d.mkdir()
        (d / "pytest.ini").write_text("[pytest]\n")
        (d / "tests").mkdir()
        assert run_all_tests._has_pytest_suite(d) is True

    def test_returns_false_for_neither(self, tmp_path: Path) -> None:
        d = tmp_path / "suite"
        d.mkdir()
        (d / "app.py").write_text("# app")
        assert run_all_tests._has_pytest_suite(d) is False

    def test_returns_false_for_nonexistent_dir(self, tmp_path: Path) -> None:
        d = tmp_path / "does_not_exist"
        assert run_all_tests._has_pytest_suite(d) is False


# ---------------------------------------------------------------------------
# Tests for _iter_suites
# ---------------------------------------------------------------------------


class TestResolvePython:
    def test_prefers_repo_venv_when_present(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        venv_dir = tmp_path / ".venv" / "Scripts"
        venv_dir.mkdir(parents=True)
        venv_python = venv_dir / "python.exe"
        venv_python.write_text("", encoding="utf-8")

        monkeypatch.setattr(run_all_tests, "_REPO_ROOT", tmp_path)
        monkeypatch.setattr(run_all_tests.sys, "executable", "C:/other/python.exe")

        assert run_all_tests._resolve_python() == str(venv_python)

    def test_falls_back_to_sys_executable_without_venv(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(run_all_tests, "_REPO_ROOT", tmp_path)
        monkeypatch.setattr(run_all_tests.sys, "executable", "C:/other/python.exe")

        assert run_all_tests._resolve_python() == "C:/other/python.exe"


class TestIterSuites:
    def test_discovers_services_with_pytest_ini(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        _make_service(services, "alpha")
        _make_service(services, "beta")
        _make_service(services, "no-ini", has_pytest_ini=False)

        result = run_all_tests._iter_suites(services, [])
        names = [p.name for p in result]
        assert "alpha" in names
        assert "beta" in names
        assert "no-ini" not in names

    def test_services_returned_in_sorted_order(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        for name in ("zz", "aa", "mm"):
            _make_service(services, name)

        result = run_all_tests._iter_suites(services, [])
        names = [p.name for p in result]
        assert names == sorted(names)

    def test_extra_suite_included_when_pytest_ini_present(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()
        ui = _make_suite(tmp_path, "ui", has_pytest_ini=True)

        result = run_all_tests._iter_suites(services, [ui])
        assert ui in result

    def test_extra_suite_included_when_tests_dir_present(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()
        n8n = _make_suite(tmp_path, "n8n", has_tests_dir=True)

        result = run_all_tests._iter_suites(services, [n8n])
        assert n8n in result

    def test_extra_suite_skipped_when_no_pytest_infrastructure(
        self, tmp_path: Path
    ) -> None:
        services = tmp_path / "services"
        services.mkdir()
        evaluation = _make_suite(tmp_path, "evaluation")  # no pytest.ini, no tests/

        result = run_all_tests._iter_suites(services, [evaluation])
        assert evaluation not in result

    def test_extra_suite_skipped_when_directory_absent(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()
        nonexistent = tmp_path / "ghost"  # not created

        result = run_all_tests._iter_suites(services, [nonexistent])
        assert nonexistent not in result

    def test_services_come_before_extras(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        _make_service(services, "myservice")
        ui = _make_suite(tmp_path, "ui", has_pytest_ini=True)

        result = run_all_tests._iter_suites(services, [ui])
        names = [p.name for p in result]
        svc_idx = names.index("myservice")
        ui_idx = names.index("ui")
        assert svc_idx < ui_idx, "Service suites must come before extra suites"

    def test_missing_services_dir_returns_only_extras(self, tmp_path: Path) -> None:
        services = tmp_path / "services"  # not created
        ui = _make_suite(tmp_path, "ui", has_pytest_ini=True)

        result = run_all_tests._iter_suites(services, [ui])
        assert ui in result


# ---------------------------------------------------------------------------
# Tests for main() — subprocess invocation and return codes
# ---------------------------------------------------------------------------


def _make_subprocess_result(returncode: int) -> MagicMock:
    r = MagicMock()
    r.returncode = returncode
    return r


class TestMain:
    def test_returns_zero_when_all_suites_pass(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        _make_service(services, "svc-a")

        with patch("subprocess.run", return_value=_make_subprocess_result(0)):
            rc = run_all_tests.main(
                services_dir=services,
                extra_suite_dirs=[],
            )
        assert rc == 0

    def test_returns_one_when_any_suite_fails(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        _make_service(services, "ok-svc")
        _make_service(services, "fail-svc")

        results = [
            _make_subprocess_result(0),
            _make_subprocess_result(1),
        ]
        with patch("subprocess.run", side_effect=results):
            rc = run_all_tests.main(
                services_dir=services,
                extra_suite_dirs=[],
            )
        assert rc == 1

    def test_extra_suite_failure_causes_nonzero_exit(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()
        ui = _make_suite(tmp_path, "ui", has_pytest_ini=True)

        with patch("subprocess.run", return_value=_make_subprocess_result(1)):
            rc = run_all_tests.main(
                services_dir=services,
                extra_suite_dirs=[ui],
            )
        assert rc == 1

    def test_subprocess_runs_with_suite_cwd(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        svc = _make_service(services, "my-service")

        captured: list[dict] = []

        def _fake_run(cmd, *, cwd, check):
            captured.append({"cmd": cmd, "cwd": cwd})
            return _make_subprocess_result(0)

        with patch("subprocess.run", side_effect=_fake_run):
            run_all_tests.main(services_dir=services, extra_suite_dirs=[])

        assert len(captured) == 1
        assert captured[0]["cwd"] == svc

    def test_subprocess_command_uses_python_m_pytest(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        _make_service(services, "svc")

        captured: list[list] = []

        def _fake_run(cmd, *, cwd, check):
            captured.append(cmd)
            return _make_subprocess_result(0)

        with patch("subprocess.run", side_effect=_fake_run):
            run_all_tests.main(services_dir=services, extra_suite_dirs=[])

        assert len(captured) == 1
        cmd = captured[0]
        assert cmd[0] == run_all_tests._resolve_python()
        assert "-m" in cmd
        assert "pytest" in cmd

    def test_extra_suite_cwd_is_suite_directory(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()
        n8n = _make_suite(tmp_path, "n8n", has_tests_dir=True)

        captured: list[Path] = []

        def _fake_run(cmd, *, cwd, check):
            captured.append(cwd)
            return _make_subprocess_result(0)

        with patch("subprocess.run", side_effect=_fake_run):
            run_all_tests.main(services_dir=services, extra_suite_dirs=[n8n])

        assert n8n in captured

    def test_no_suites_fails_closed_without_subprocess_calls(self, tmp_path: Path) -> None:
        services = tmp_path / "services"
        services.mkdir()

        with patch("subprocess.run") as mock_run:
            rc = run_all_tests.main(services_dir=services, extra_suite_dirs=[])

        mock_run.assert_not_called()
        assert rc == 1

    def test_reports_failed_suite_names(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        services = tmp_path / "services"
        _make_service(services, "broken-svc")

        with patch("subprocess.run", return_value=_make_subprocess_result(1)):
            run_all_tests.main(services_dir=services, extra_suite_dirs=[])

        out = capsys.readouterr().out
        assert "broken-svc" in out

    def test_all_green_prints_success_message(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        services = tmp_path / "services"
        _make_service(services, "green-svc")

        with patch("subprocess.run"):
            run_all_tests.main(services_dir=services, extra_suite_dirs=[])

        out = capsys.readouterr().out
        assert "green" in out.lower() or "pass" in out.lower() or "all" in out.lower()
