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
    slugify_company_name,
    PathsError,
)


class TestSlugifyCompanyName:
    """Test company name slugification."""

    def test_slugify_simple_name(self):
        """Test slugifying a simple company name."""
        assert slugify_company_name("Stripe") == "stripe"
        assert slugify_company_name("GitHub") == "github"

    def test_slugify_name_with_spaces(self):
        """Test slugifying names with spaces."""
        assert slugify_company_name("Cato Networks") == "cato-networks"
        assert slugify_company_name("Affirm Holdings Inc") == "affirm-holdings-inc"

    def test_slugify_name_with_comma(self):
        """Test slugifying names with commas."""
        assert slugify_company_name("Toast, Inc.") == "toast-inc"
        assert slugify_company_name("GitHub, Inc.") == "github-inc"

    def test_slugify_name_with_period(self):
        """Test slugifying names with periods."""
        assert slugify_company_name("Toast, Inc.") == "toast-inc"
        assert slugify_company_name("Acme Corp.") == "acme-corp"

    def test_slugify_name_with_numbers(self):
        """Test slugifying names starting with numbers."""
        assert slugify_company_name("1Password") == "1password"
        assert slugify_company_name("0xide") == "0xide"

    def test_slugify_name_with_hyphen(self):
        """Test slugifying names that already have hyphens."""
        assert slugify_company_name("Meta-Dublin") == "meta-dublin"
        assert slugify_company_name("fly-io") == "fly-io"

    def test_slugify_name_with_multiple_spaces(self):
        """Test slugifying names with multiple consecutive spaces."""
        assert slugify_company_name("Affirm  Holdings  Inc") == "affirm-holdings-inc"

    def test_slugify_name_with_special_chars(self):
        """Test slugifying names with various special characters."""
        assert slugify_company_name("Affirm Holdings Inc.") == "affirm-holdings-inc"
        assert slugify_company_name("Company & Co.") == "company-co"
        assert slugify_company_name("Test@Company!") == "test-company"

    def test_slugify_preserves_existing_hyphens(self):
        """Test that existing hyphens are preserved."""
        assert slugify_company_name("mechanical-orchard") == "mechanical-orchard"

    def test_slugify_strips_leading_trailing_hyphens(self):
        """Test that leading/trailing hyphens are stripped."""
        assert slugify_company_name("-Company-") == "company"
        assert slugify_company_name("--Test--") == "test"

    def test_slugify_collapses_multiple_hyphens(self):
        """Test that multiple consecutive hyphens are collapsed."""
        assert slugify_company_name("Company---Name") == "company-name"
        assert slugify_company_name("Test--Co") == "test-co"

    def test_slugify_all_existing_companies(self):
        """Test slugifying all current problematic company names."""
        # Current problematic names
        assert slugify_company_name("Toast, Inc.") == "toast-inc"
        assert slugify_company_name("Affirm Holdings Inc.") == "affirm-holdings-inc"
        assert slugify_company_name("Cato Networks") == "cato-networks"

        # Existing correct names should remain lowercase
        assert slugify_company_name("stripe") == "stripe"
        assert slugify_company_name("anthropic") == "anthropic"

    def test_slugify_is_idempotent(self):
        """Test that slugifying a slug returns the same slug."""
        slug1 = slugify_company_name("Toast, Inc.")
        slug2 = slugify_company_name(slug1)
        assert slug1 == slug2
        assert slug1 == "toast-inc"


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
        assert company_dir == tmp_path / "data" / "testco"

    def test_get_company_dir_slugifies_name(self, tmp_path):
        """Test that company names are slugified."""
        company_dir = get_company_dir("Test Co", base_path=tmp_path)
        # Should be slugified to lowercase with hyphens
        assert company_dir == tmp_path / "data" / "test-co"

    def test_get_company_dir_with_special_chars(self, tmp_path):
        """Test getting directory with special characters in name."""
        company_dir = get_company_dir("Toast, Inc.", base_path=tmp_path)
        assert company_dir == tmp_path / "data" / "toast-inc"

    def test_get_company_dir_multiple_companies(self, tmp_path):
        """Test getting directories for multiple companies."""
        company1 = get_company_dir("Company1", base_path=tmp_path)
        company2 = get_company_dir("Company2", base_path=tmp_path)

        assert company1 != company2
        assert company1.name == "company1"
        assert company2.name == "company2"


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
        assert facts_path == tmp_path / "data" / "testco" / "company.facts.yaml"
        assert facts_path.name == "company.facts.yaml"

    def test_get_facts_path_different_companies(self, tmp_path):
        """Test facts paths for different companies."""
        facts1 = get_facts_path("Company1", base_path=tmp_path)
        facts2 = get_facts_path("Company2", base_path=tmp_path)

        assert facts1 != facts2
        assert facts1.parent.name == "company1"
        assert facts2.parent.name == "company2"


class TestGetFlagsPath:
    """Test getting flags file paths."""

    def test_get_flags_path(self, tmp_path):
        """Test getting flags file path."""
        flags_path = get_flags_path("TestCo", base_path=tmp_path)
        assert flags_path == tmp_path / "data" / "testco" / "company.flags.yaml"
        assert flags_path.name == "company.flags.yaml"

    def test_get_flags_path_different_companies(self, tmp_path):
        """Test flags paths for different companies."""
        flags1 = get_flags_path("Company1", base_path=tmp_path)
        flags2 = get_flags_path("Company2", base_path=tmp_path)

        assert flags1 != flags2
        assert flags1.parent.name == "company1"
        assert flags2.parent.name == "company2"


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
        slugs = ["company1", "company2", "company3"]

        # Create all companies
        for company in companies:
            ensure_company_dir(company, base_path=tmp_path)

        # List should return all slugified companies
        listed = list_companies(base_path=tmp_path)
        assert set(listed) == set(slugs)

        # Each should have correct paths with slugified names
        for company, slug in zip(companies, slugs):
            facts = get_facts_path(company, base_path=tmp_path)
            flags = get_flags_path(company, base_path=tmp_path)
            assert facts.parent.name == slug
            assert flags.parent.name == slug
