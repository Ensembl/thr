"""
.. See the NOTICE file distributed with this work for additional information
   regarding copyright ownership.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import pytest

import trackhubs.hub_check as hub_check_module
from trackhubs.hub_check import hub_check


@pytest.fixture(autouse=True)
def local_hubcheck_binary(tmp_path, monkeypatch):
    hubcheck = tmp_path / "tools" / "hubCheck"
    hubcheck.parent.mkdir()
    hubcheck.touch()
    monkeypatch.setattr(hub_check_module, "HUBCHECK_PATH", hubcheck)


@pytest.mark.parametrize(
    'returncode, stdout, expected_key_in_result',
    [
        (0, "No problems detected\n", 'success'),
        (1, "hub.txt:\nwarning: missing optional description\n", 'warning'),
        (1, "hub.txt:\nerror: cannot open genomes.txt\n", 'error'),
    ]
)
def test_hub_check_all_cases(monkeypatch, returncode, stdout, expected_key_in_result):
    """
    Test hubCheck utility in the three different scenarios
    """
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return type("CompletedProcess", (), {"returncode": returncode, "stdout": stdout})

    monkeypatch.setattr(hub_check_module.subprocess, "run", fake_run)

    actual_result = hub_check("https://example.org/hub.txt")

    assert expected_key_in_result in actual_result
    assert calls[0][0] == [str(hub_check_module.HUBCHECK_PATH), "-noTracks", "https://example.org/hub.txt"]


def test_hub_check_downloads_binary_when_missing(tmp_path, monkeypatch):
    """
    Test hubCheck is downloaded locally if it is missing.
    """
    hubcheck = tmp_path / "tools" / "hubCheck"
    hubcheck.unlink()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        if command[0] == "curl":
            hubcheck.touch()
            return type("CompletedProcess", (), {"returncode": 0, "stdout": ""})
        return type("CompletedProcess", (), {"returncode": 0, "stdout": "No problems detected\n"})

    monkeypatch.setattr(hub_check_module, "HUBCHECK_PATH", hubcheck)
    monkeypatch.setattr(hub_check_module.subprocess, "run", fake_run)

    actual_result = hub_check("https://example.org/hub.txt")

    assert "success" in actual_result
    assert calls[0][0][0] == "curl"
    assert calls[1][0] == [str(hubcheck), "-noTracks", "https://example.org/hub.txt"]


def test_hub_check_makes_existing_binary_executable(monkeypatch):
    """
    Test hubCheck permissions are fixed when the binary already exists.
    """
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return type("CompletedProcess", (), {"returncode": 0, "stdout": "No problems detected\n"})

    hub_check_module.HUBCHECK_PATH.chmod(0o600)
    monkeypatch.setattr(hub_check_module.subprocess, "run", fake_run)

    actual_result = hub_check("https://example.org/hub.txt")

    assert "success" in actual_result
    assert hub_check_module.HUBCHECK_PATH.stat().st_mode & 0o700 == 0o700
