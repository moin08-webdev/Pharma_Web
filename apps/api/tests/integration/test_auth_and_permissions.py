import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_health_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health/live")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

        ready_res = await client.get("/api/health/ready")
        assert ready_res.status_code == 200
        assert ready_res.json()["status"] == "ready"


@pytest.mark.asyncio
async def test_auth_login_and_me():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Invalid password
        bad_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "pharmacist@pharmabridge.demo", "password": "WrongPassword!"},
        )
        assert bad_res.status_code == 401
        assert bad_res.json()["error"]["code"] == "UNAUTHORIZED"

        # Valid login
        res = await client.post(
            "/api/v1/auth/login",
            json={"email": "pharmacist@pharmabridge.demo", "password": "DemoPharmacistPass123!"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["user"]["role"] == "PHARMACIST"
        assert "approve:plans" in data["permissions"]

        # Call /me with session cookie
        me_res = await client.get("/api/v1/auth/me")
        assert me_res.status_code == 200
        assert me_res.json()["user"]["email"] == "pharmacist@pharmabridge.demo"


@pytest.mark.asyncio
async def test_role_enforcement_assistant_cannot_approve():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Login as assistant
        await client.post(
            "/api/v1/auth/login",
            json={"email": "assistant@pharmabridge.demo", "password": "DemoAssistantPass123!"},
        )

        # Assistant tries to finalize order -> must receive 403 Forbidden
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        res = await client.post(
            "/api/v1/orders",
            json={"quote_id": fake_uuid, "approval_id": fake_uuid},
        )
        assert res.status_code == 403
        assert res.json()["error"]["code"] == "FORBIDDEN"
