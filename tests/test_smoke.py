from pathlib import Path

import yaml

import fedlens
from fedlens.config import REPO_ROOT, get_settings


def test_package_imports():
    assert fedlens.__version__


def test_default_model_is_configurable(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("FEDLENS_MODEL", "some-other-model")
    assert get_settings().fedlens_model == "some-other-model"
    get_settings.cache_clear()


def test_scope_file_is_valid():
    scope = yaml.safe_load(Path(REPO_ROOT / "config" / "scope.yaml").read_text())
    assert scope["fiscal_years"]
    assert scope["agencies"]
    assert set(scope["award_type_codes"]) <= {"A", "B", "C", "D"}
