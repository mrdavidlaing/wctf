"""Tests for YAML handler with safe read/write operations."""

import pytest
from pathlib import Path
import tempfile
import os

from wctf_core.utils.yaml_handler import (
    read_yaml,
    write_yaml,
    YAMLHandlerError,
)


class TestReadYAML:
    """Test YAML reading functionality."""

    def test_read_valid_yaml(self, tmp_path):
        """Test reading a valid YAML file."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\nlist:\n  - item1\n  - item2\n")

        data = read_yaml(yaml_file)
        assert data["key"] == "value"
        assert data["list"] == ["item1", "item2"]

    def test_read_empty_yaml(self, tmp_path):
        """Test reading an empty YAML file returns empty dict."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        data = read_yaml(yaml_file)
        assert data == {}

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading nonexistent file raises YAMLHandlerError."""
        yaml_file = tmp_path / "nonexistent.yaml"

        with pytest.raises(YAMLHandlerError) as exc_info:
            read_yaml(yaml_file)
        assert "does not exist" in str(exc_info.value).lower()

    def test_read_malformed_yaml(self, tmp_path):
        """Test reading malformed YAML raises YAMLHandlerError."""
        yaml_file = tmp_path / "malformed.yaml"
        yaml_file.write_text("key: value\n  invalid indentation\n: no key")

        with pytest.raises(YAMLHandlerError) as exc_info:
            read_yaml(yaml_file)
        assert "parse" in str(exc_info.value).lower() or "yaml" in str(exc_info.value).lower()

    def test_read_yaml_with_dates(self, tmp_path):
        """Test reading YAML with date values."""
        yaml_file = tmp_path / "dates.yaml"
        yaml_file.write_text("date: 2025-09-27\nstring_date: '2025-09-27'\n")

        data = read_yaml(yaml_file)
        # Should parse ISO date format
        assert "date" in data
        assert "string_date" in data

    def test_read_yaml_with_complex_structure(self, tmp_path):
        """Test reading YAML with nested structures."""
        yaml_content = """
company: TestCo
details:
  nested:
    level: 3
    items:
      - name: item1
        value: 100
      - name: item2
        value: 200
"""
        yaml_file = tmp_path / "complex.yaml"
        yaml_file.write_text(yaml_content)

        data = read_yaml(yaml_file)
        assert data["company"] == "TestCo"
        assert data["details"]["nested"]["level"] == 3
        assert len(data["details"]["nested"]["items"]) == 2

    def test_read_yaml_accepts_string_path(self, tmp_path):
        """Test that read_yaml accepts string paths."""
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("key: value\n")

        data = read_yaml(str(yaml_file))
        assert data["key"] == "value"


class TestWriteYAML:
    """Test YAML writing functionality."""

    def test_write_valid_yaml(self, tmp_path):
        """Test writing valid data to YAML file."""
        yaml_file = tmp_path / "output.yaml"
        data = {"key": "value", "list": ["item1", "item2"]}

        write_yaml(yaml_file, data)

        assert yaml_file.exists()
        content = yaml_file.read_text()
        assert "key: value" in content
        assert "item1" in content

    def test_write_creates_parent_directories(self, tmp_path):
        """Test that write_yaml creates parent directories."""
        yaml_file = tmp_path / "subdir" / "nested" / "output.yaml"
        data = {"test": "data"}

        write_yaml(yaml_file, data)

        assert yaml_file.exists()
        assert yaml_file.parent.exists()

    def test_write_overwrites_existing_file(self, tmp_path):
        """Test that write_yaml overwrites existing files."""
        yaml_file = tmp_path / "overwrite.yaml"
        yaml_file.write_text("old: data\n")

        new_data = {"new": "content"}
        write_yaml(yaml_file, new_data)

        content = yaml_file.read_text()
        assert "new: content" in content
        assert "old: data" not in content

    def test_write_empty_dict(self, tmp_path):
        """Test writing an empty dictionary."""
        yaml_file = tmp_path / "empty.yaml"
        write_yaml(yaml_file, {})

        assert yaml_file.exists()
        content = yaml_file.read_text()
        assert content.strip() == "{}" or content.strip() == ""

    def test_write_complex_structure(self, tmp_path):
        """Test writing complex nested structures."""
        yaml_file = tmp_path / "complex.yaml"
        data = {
            "company": "TestCo",
            "details": {
                "nested": {
                    "level": 3,
                    "items": [
                        {"name": "item1", "value": 100},
                        {"name": "item2", "value": 200},
                    ],
                }
            },
        }

        write_yaml(yaml_file, data)

        # Read it back to verify
        read_data = read_yaml(yaml_file)
        assert read_data["company"] == "TestCo"
        assert read_data["details"]["nested"]["level"] == 3

    def test_write_preserves_date_objects(self, tmp_path):
        """Test writing preserves date objects."""
        from datetime import date

        yaml_file = tmp_path / "dates.yaml"
        data = {"date": date(2025, 9, 27)}

        write_yaml(yaml_file, data)

        content = yaml_file.read_text()
        assert "2025-09-27" in content

    def test_write_yaml_accepts_string_path(self, tmp_path):
        """Test that write_yaml accepts string paths."""
        yaml_file = tmp_path / "test.yaml"
        data = {"key": "value"}

        write_yaml(str(yaml_file), data)

        assert yaml_file.exists()

    def test_write_to_readonly_directory_raises_error(self, tmp_path):
        """Test writing to readonly directory raises YAMLHandlerError."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        os.chmod(readonly_dir, 0o444)

        yaml_file = readonly_dir / "test.yaml"

        try:
            with pytest.raises(YAMLHandlerError) as exc_info:
                write_yaml(yaml_file, {"test": "data"})
            assert "permission" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)


class TestRoundTrip:
    """Test reading and writing YAML maintains data integrity."""

    def test_roundtrip_preserves_data(self, tmp_path):
        """Test that write then read preserves data."""
        yaml_file = tmp_path / "roundtrip.yaml"
        original_data = {
            "company": "TestCo",
            "list": ["a", "b", "c"],
            "nested": {"key": "value"},
            "number": 42,
        }

        write_yaml(yaml_file, original_data)
        read_data = read_yaml(yaml_file)

        assert read_data == original_data

    def test_roundtrip_with_special_characters(self, tmp_path):
        """Test roundtrip with special characters."""
        yaml_file = tmp_path / "special.yaml"
        original_data = {
            "text": "Line with: colon and 'quotes'",
            "multiline": "Line 1\nLine 2",
        }

        write_yaml(yaml_file, original_data)
        read_data = read_yaml(yaml_file)

        assert read_data["text"] == original_data["text"]
        assert read_data["multiline"] == original_data["multiline"]
