import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.middleware.beta_access import BetaAccessMiddleware


@pytest.fixture
def app_with_middleware():
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"status": "ok"}

    @app.get("/api/v1/test")
    async def api_endpoint():
        return {"data": "test"}

    @app.get("/docs")
    async def docs():
        return {"docs": True}

    @app.get("/health")
    async def health():
        return {"healthy": True}

    return app


class TestBetaAccessMiddlewareDisabled:
    @pytest.mark.unit
    def test_no_beta_code_configured_allows_all_requests(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code=None)
        client = TestClient(app_with_middleware)

        response = client.get("/api/v1/test")

        assert response.status_code == 200
        assert response.json() == {"data": "test"}

    @pytest.mark.unit
    def test_empty_beta_code_allows_all_requests(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="")
        client = TestClient(app_with_middleware)

        response = client.get("/api/v1/test")

        assert response.status_code == 200


class TestBetaAccessMiddlewareEnabled:
    @pytest.mark.unit
    def test_missing_header_returns_403(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/api/v1/test")

        assert response.status_code == 403
        assert response.json()["error"] == "BETA_CODE_REQUIRED"

    @pytest.mark.unit
    def test_invalid_code_returns_403(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/api/v1/test", headers={"X-Beta-Code": "wrong-code"})

        assert response.status_code == 403
        assert response.json()["error"] == "BETA_CODE_INVALID"

    @pytest.mark.unit
    def test_valid_code_allows_request(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/api/v1/test", headers={"X-Beta-Code": "secret-beta-code"})

        assert response.status_code == 200
        assert response.json() == {"data": "test"}


class TestBetaAccessMiddlewareExcludedPaths:
    @pytest.mark.unit
    def test_root_path_excluded(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_docs_path_excluded(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/docs")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_health_path_excluded(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/health")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_openapi_json_excluded(self, app_with_middleware):
        app_with_middleware.add_middleware(BetaAccessMiddleware, beta_code="secret-beta-code")
        client = TestClient(app_with_middleware)

        response = client.get("/openapi.json")

        assert response.status_code in [200, 404]


class TestBetaAccessMiddlewareFromEnv:
    @pytest.mark.unit
    def test_reads_beta_code_from_environment(self, app_with_middleware):
        with patch.dict("os.environ", {"BETA_ACCESS_CODE": "env-beta-code"}):
            app_with_middleware.add_middleware(BetaAccessMiddleware)
            client = TestClient(app_with_middleware)

            response = client.get("/api/v1/test", headers={"X-Beta-Code": "env-beta-code"})

            assert response.status_code == 200
