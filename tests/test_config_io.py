from pathlib import Path
from geoff.config_io import load_yaml, save_yaml, ensure_config_dir


def test_load_yaml_missing(tmp_path):
    path = tmp_path / "missing.yaml"
    assert load_yaml(path) is None


def test_save_and_load_yaml(tmp_path):
    path = tmp_path / "test.yaml"
    data = {"foo": "bar", "baz": [1, 2, 3]}

    save_yaml(path, data)
    assert path.exists()

    loaded = load_yaml(path)
    assert loaded == data


def test_ensure_config_dir(tmp_path):
    config_dir = tmp_path / ".geoff"
    assert not config_dir.exists()

    ensure_config_dir(config_dir)
    assert config_dir.exists()
    assert config_dir.is_dir()


def test_save_yaml_creates_parents(tmp_path):
    path = tmp_path / "nested" / "dir" / "config.yaml"
    data = {"a": 1}
    save_yaml(path, data)
    assert path.exists()
    assert load_yaml(path) == data
