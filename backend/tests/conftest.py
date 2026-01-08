import pytest
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.engine import Base, get_db
from backend.main import app


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, Any, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator[TestClient, Any, None]:
    def override_get_db() -> Generator[Session, Any, None]:
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_llm_client() -> MagicMock:
    mock = MagicMock()
    mock.complete.return_value = "This is a mock LLM response."
    mock.classify.return_value = "linear_equation_1var"
    return mock


@pytest.fixture
def sample_problem_text() -> str:
    return "3x + 5 = 14"


@pytest.fixture
def sample_quadratic_text() -> str:
    return "x² + 2x - 3 = 0"


@pytest.fixture
def sample_geometry_text() -> str:
    return "Find the area of a triangle with base 6 and height 4"
