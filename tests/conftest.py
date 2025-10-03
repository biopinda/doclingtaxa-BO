"""
Pytest fixtures for doclingtaxaBO tests.

Provides MongoDB test fixtures, sample PDF directories, and test data.
"""
import os
from pathlib import Path
from typing import Generator

import pytest
from pymongo import MongoClient
from pymongo.database import Database


@pytest.fixture(scope="session")
def mongodb_test_client() -> Generator[MongoClient, None, None]:
    """
    Provide test MongoDB client (session scope).

    Uses MONGODB_TEST_URI environment variable if set, otherwise defaults to localhost.
    Database is cleaned up after all tests complete.

    Yields:
        MongoClient: Connected MongoDB client for testing
    """
    # Get MongoDB URI from environment or use default
    mongodb_uri = os.getenv("MONGODB_TEST_URI", "mongodb://localhost:27017")

    client = MongoClient(mongodb_uri)

    # Verify connection
    try:
        client.admin.command("ping")
    except Exception as e:
        pytest.skip(f"MongoDB not available: {e}")

    yield client

    # Cleanup: Drop test database after all tests
    client.drop_database("doclingtaxa_test")
    client.close()


@pytest.fixture(scope="function")
def clean_test_db(mongodb_test_client: MongoClient) -> Database:
    """
    Provide clean test database for each test (function scope).

    Deletes all documents from test collection before each test.

    Args:
        mongodb_test_client: MongoDB client fixture

    Returns:
        Database: Clean test database instance
    """
    db = mongodb_test_client["doclingtaxa_test"]

    # Clean all collections before test
    for collection_name in db.list_collection_names():
        db[collection_name].delete_many({})

    return db


@pytest.fixture(scope="session")
def sample_pdf_dir() -> Path:
    """
    Path to sample PDF test fixtures.

    Returns:
        Path: Absolute path to tests/fixtures/sample_pdfs directory
    """
    fixtures_dir = Path(__file__).parent / "fixtures" / "sample_pdfs"

    # Create directory if it doesn't exist
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    return fixtures_dir


@pytest.fixture(scope="session")
def monografias_dir() -> Path:
    """
    Path to monografias directory with real test PDFs.

    Returns:
        Path: Absolute path to monografias directory
    """
    repo_root = Path(__file__).parent.parent
    monografias = repo_root / "monografias"

    # Create directory if it doesn't exist
    monografias.mkdir(parents=True, exist_ok=True)

    return monografias


@pytest.fixture(scope="function")
def temp_pdf_dir(tmp_path: Path) -> Path:
    """
    Provide temporary directory for PDF test files (function scope).

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path: Temporary directory for test PDFs
    """
    pdf_dir = tmp_path / "test_pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return pdf_dir


# Pytest markers
def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line("markers", "contract: Contract tests for API/schema validation")
    config.addinivalue_line("markers", "integration: Integration tests for end-to-end scenarios")
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "slow: Tests that take significant time to run")
