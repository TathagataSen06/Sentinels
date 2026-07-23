"""Tests for configuration parsing and validation."""

from __future__ import annotations

import textwrap

import pytest

from honeytrace.config import Config, ConfigError, load_config


def _write(tmp_path, text: str):
    path = tmp_path / "honeytrace.yml"
    path.write_text(textwrap.dedent(text), encoding="utf-8")
    return path


def test_defaults_are_applied(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: ssh
            type: ssh
            port: 2222
        """,
    )
    config = load_config(path, apply_env=False)
    assert config.node_id == "honeytrace"
    assert config.metrics.port == 9101
    assert config.logging.level == "INFO"
    assert len(config.services) == 1
    assert config.services[0].type == "ssh"


def test_unknown_top_level_key_rejected(tmp_path):
    path = _write(tmp_path, "bogus: true\n")
    with pytest.raises(ConfigError, match="unknown option"):
        load_config(path, apply_env=False)


def test_missing_service_type_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: broken
            port: 1234
        """,
    )
    with pytest.raises(ConfigError, match="missing required option 'type'"):
        load_config(path, apply_env=False)


def test_duplicate_service_names_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: dup
            type: ssh
            port: 2222
          - name: dup
            type: telnet
            port: 2323
        """,
    )
    with pytest.raises(ConfigError, match="duplicate service name"):
        load_config(path, apply_env=False)


def test_conflicting_bindings_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: a
            type: ssh
            host: 0.0.0.0
            port: 5000
          - name: b
            type: telnet
            host: 0.0.0.0
            port: 5000
        """,
    )
    with pytest.raises(ConfigError, match="both bind"):
        load_config(path, apply_env=False)


def test_disabled_service_does_not_conflict(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: a
            type: ssh
            port: 5000
          - name: b
            type: telnet
            port: 5000
            enabled: false
        """,
    )
    config = load_config(path, apply_env=False)
    assert len(config.services) == 2


def test_invalid_log_level_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        logging:
          level: LOUD
        services: []
        """,
    )
    with pytest.raises(ConfigError, match="invalid level"):
        load_config(path, apply_env=False)


def test_negative_port_rejected(tmp_path):
    path = _write(
        tmp_path,
        """
        services:
          - name: a
            type: ssh
            port: -1
        """,
    )
    with pytest.raises(ConfigError, match="must be >= 1"):
        load_config(path, apply_env=False)


def test_missing_file_raises():
    with pytest.raises(ConfigError, match="not found"):
        load_config("/does/not/exist.yml", apply_env=False)


def test_env_overrides_applied():
    config = Config()
    config.apply_env_overrides(
        {
            "HONEYTRACE_NODE_ID": "edge-1",
            "HONEYTRACE_LOG_LEVEL": "debug",
            "HONEYTRACE_METRICS_PORT": "9200",
            "HONEYTRACE_EVENT_LOG": "/tmp/events.log",
        }
    )
    assert config.node_id == "edge-1"
    assert config.logging.level == "DEBUG"
    assert config.metrics.port == 9200
    assert config.logging.event_log == "/tmp/events.log"


def test_env_override_invalid_metrics_port():
    config = Config()
    with pytest.raises(ConfigError, match="must be an integer"):
        config.apply_env_overrides({"HONEYTRACE_METRICS_PORT": "not-a-number"})
