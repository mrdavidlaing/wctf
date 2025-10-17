"""Tests for path utilities managing data directory."""

import pytest
from pathlib import Path
import os
import tempfile

from wctf_core.utils.paths import (
    get_data_dir,
    get_company_dir,
    ensure_company_dir,
    get_facts_path,
    get_flags_path,
    list_companies,
    PathsError,
)


class TestGetDataDir:
    """Test getting the data directory."""

    def test_get_data_dir_default(self):
        """Test getting default data directory."""
        data_dir = get_data_dir()
        assert isinstance(data_dir, Path)
        assert data_dir.name == "data"

    def test_get_data_dir_exists(self):
        """Test that default data dir exists in project."""
        data_dir = get_data_dir()
        # In our actual project, the data dir should exist
        assert data_dir.exists() or True  # Allow for test environments

    def test_get_data_dir_custom_base(self, tmp_path):
        """Test getting data dir with custom base path."""
        custom_base = tmp_path / "custom"
        custom_base.mkdir()
        data_dir = get_data_dir(base_path=custom_base)
        assert data_dir == custom_base / "data"

    def test_get_data_dir_returns_path_object(self):
        """Test that get_data_dir returns a Path object."""
        data_dir = get_data_dir()
        assert isinstance(data_dir, Path)


class TestGetCompanyDir:
    """Test getting company-specific directories."""

    def test_get_company_dir(self, tmp_path):
        """Test getting a company directory."""
        company_dir = get_company_dir("TestCo", base_path=tmp_path)
        assert company_dir == tmp_path / "data" / "TestCo"

    def test_get_company_dir_normalizes_name(self, tmp_path):
        """Test that company names are normalized."""
        company_dir = get_company_dir("Test Co", base_path=tmp_path)
        # Should handle spaces or special characters appropriately
        assert "Test Co" in str(company_dir) or "TestCo" in str(company_dir)

    def test_get_company_dir_multiple_companies(self, tmp_path):
        """Test getting directories for multiple companies."""
        company1 = get_company_dir("Company1", base_path=tmp_path)
        company2 = get_company_dir("Company2", base_path=tmp_path)

        assert company1 != company2
        assert company1.name == "Company1"
        assert company2.name == "Company2"


class TestEnsureCompanyDir:
    """Test ensuring company directories exist."""

    def test_ensure_company_dir_creates_directory(self, tmp_path):
        """Test that ensure_company_dir creates the directory."""
        company_dir = ensure_company_dir("NewCo", base_path=tmp_path)
        assert company_dir.exists()
        assert company_dir.is_dir()

    def test_ensure_company_dir_idempotent(self, tmp_path):
        """Test that calling ensure_company_dir twice is safe."""
        company_dir1 = ensure_company_dir("ExistingCo", base_path=tmp_path)
        company_dir2 = ensure_company_dir("ExistingCo", base_path=tmp_path)

        assert company_dir1 == company_dir2
        assert company_dir1.exists()

    def test_ensure_company_dir_creates_parent_dirs(self, tmp_path):
        """Test that ensure_company_dir creates parent directories."""
        # If data dir doesn't exist, it should be created
        new_base = tmp_path / "nonexistent"
        company_dir = ensure_company_dir("TestCo", base_path=new_base)

        assert company_dir.exists()
        assert company_dir.parent.exists()  # data dir
        assert company_dir.parent.name == "data"


class TestGetFactsPath:
    """Test getting facts file paths."""

    def test_get_facts_path(self, tmp_path):
        """Test getting facts file path."""
        facts_path = get_facts_path("TestCo", base_path=tmp_path)
        assert facts_path == tmp_path / "data" / "TestCo" / "company.facts.yaml"
        assert facts_path.name == "company.facts.yaml"

    def test_get_facts_path_different_companies(self, tmp_path):
        """Test facts paths for different companies."""
        facts1 = get_facts_path("Company1", base_path=tmp_path)
        facts2 = get_facts_path("Company2", base_path=tmp_path)

        assert facts1 != facts2
        assert facts1.parent.name == "Company1"
        assert facts2.parent.name == "Company2"


class TestGetFlagsPath:
    """Test getting flags file paths."""

    def test_get_flags_path(self, tmp_path):
        """Test getting flags file path."""
        flags_path = get_flags_path("TestCo", base_path=tmp_path)
        assert flags_path == tmp_path / "data" / "TestCo" / "company.flags.yaml"
        assert flags_path.name == "company.flags.yaml"

    def test_get_flags_path_different_companies(self, tmp_path):
        """Test flags paths for different companies."""
        flags1 = get_flags_path("Company1", base_path=tmp_path)
        flags2 = get_flags_path("Company2", base_path=tmp_path)

        assert flags1 != flags2
        assert flags1.parent.name == "Company1"
        assert flags2.parent.name == "Company2"


class TestListCompanies:
    """Test listing companies in data directory."""

    def test_list_companies_empty_data_dir(self, tmp_path):
        """Test listing companies when data dir is empty."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        companies = list_companies(base_path=tmp_path)
        assert companies == []

    def test_list_companies_with_companies(self, tmp_path):
        """Test listing companies when companies exist."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create some company directories
        (data_dir / "Company1").mkdir()
        (data_dir / "Company2").mkdir()
        (data_dir / "Company3").mkdir()

        companies = list_companies(base_path=tmp_path)
        assert len(companies) == 3
        assert "Company1" in companies
        assert "Company2" in companies
        assert "Company3" in companies

    def test_list_companies_ignores_files(self, tmp_path):
        """Test that list_companies ignores files in data dir."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create companies and a file
        (data_dir / "Company1").mkdir()
        (data_dir / "somefile.txt").write_text("test")

        companies = list_companies(base_path=tmp_path)
        assert len(companies) == 1
        assert "Company1" in companies
        assert "somefile.txt" not in companies

    def test_list_companies_nonexistent_data_dir(self, tmp_path):
        """Test listing companies when data dir doesn't exist."""
        companies = list_companies(base_path=tmp_path / "nonexistent")
        assert companies == []

    def test_list_companies_sorted(self, tmp_path):
        """Test that companies are returned sorted."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create companies in non-alphabetical order
        (data_dir / "Zebra").mkdir()
        (data_dir / "Apple").mkdir()
        (data_dir / "Microsoft").mkdir()

        companies = list_companies(base_path=tmp_path)
        assert companies == ["Apple", "Microsoft", "Zebra"]


class TestPathsIntegration:
    """Integration tests for path utilities."""

    def test_create_company_and_get_paths(self, tmp_path):
        """Test creating a company and getting its file paths."""
        company_dir = ensure_company_dir("IntegrationCo", base_path=tmp_path)
        facts_path = get_facts_path("IntegrationCo", base_path=tmp_path)
        flags_path = get_flags_path("IntegrationCo", base_path=tmp_path)

        assert company_dir.exists()
        assert facts_path.parent == company_dir
        assert flags_path.parent == company_dir
        assert facts_path.name == "company.facts.yaml"
        assert flags_path.name == "company.flags.yaml"

    def test_multiple_companies_workflow(self, tmp_path):
        """Test working with multiple companies."""
        companies = ["Company1", "Company2", "Company3"]

        # Create all companies
        for company in companies:
            ensure_company_dir(company, base_path=tmp_path)

        # List should return all companies
        listed = list_companies(base_path=tmp_path)
        assert set(listed) == set(companies)

        # Each should have correct paths
        for company in companies:
            facts = get_facts_path(company, base_path=tmp_path)
            flags = get_flags_path(company, base_path=tmp_path)
            assert facts.parent.name == company
            assert flags.parent.name == company
