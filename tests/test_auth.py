valid_user_body = {"email": "test1@gmail.com", "password": "Test_pass_1", "name": "Test1"}


class TestRegister:
    async def test_success(self, client):
        response = await client.post("/auth/register", json=valid_user_body)
        assert response.status_code == 200
        user = response.json()["user"]
        assert user["email"] == "test1@gmail.com"
        assert user["name"] == "Test1"
        assert "password_hash" not in user

    async def test_duplicate_email(self, client):
        response1 = await client.post("/auth/register", json=valid_user_body)
        response2 = await client.post("/auth/register", json=valid_user_body)
        assert response1.status_code == 200
        assert response2.status_code == 409
        assert response2.json()["detail"] == "User with email 'test1@gmail.com' already exists"

    async def test_invalid_body(self, client):
        response1 = await client.post(
            "/auth/register", json={"email": "test1@gmail", "password": "Test_pass_1", "name": "Test1"}
        )
        response2 = await client.post(
            "/auth/register", json={"email": "test1@gmail.com", "password": "Test_pass", "name": "Test1"}
        )
        response3 = await client.post(
            "/auth/register", json={"email": "test1@gmail.com", "password": "test_pass_1", "name": "Test1"}
        )
        response4 = await client.post(
            "/auth/register", json={"email": "test1@gmail.com", "password": "Test_1", "name": "Test1"}
        )
        assert response1.status_code == 422
        assert response2.status_code == 422
        assert response3.status_code == 422
        assert response4.status_code == 422


class TestLogin:
    async def test_success(self, client):
        await client.post("/auth/register", json=valid_user_body)
        response = await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": valid_user_body["password"]}
        )
        assert response.status_code == 200
        assert "accessToken" in response.json()
        assert response.cookies.get("refresh_token") is not None

    async def test_bad_credentials(self, client):
        await client.post("/auth/register", json=valid_user_body)
        bad_pass_response = await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": "invalid_password"}
        )
        assert bad_pass_response.status_code == 401
        assert bad_pass_response.json()["detail"] == "Wrong email or password provided. Try again"
        assert bad_pass_response.cookies.get("refresh_token") is None

        bad_email_response = await client.post(
            "/auth/login", json={"email": "invalid@gmail.com", "password": valid_user_body["password"]}
        )
        assert bad_email_response.status_code == 401
        assert bad_email_response.json()["detail"] == "Wrong email or password provided. Try again"
        assert bad_email_response.cookies.get("refresh_token") is None


class TestRefresh:
    async def test_success(self, client):
        await client.post("/auth/register", json=valid_user_body)
        await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": valid_user_body["password"]}
        )
        refresh_response = await client.post("/auth/refresh")
        assert refresh_response.status_code == 200
        assert "accessToken" in refresh_response.json()

    async def test_without_cookies(self, client):
        await client.post("/auth/register", json=valid_user_body)
        refresh_response = await client.post("/auth/refresh")
        assert refresh_response.status_code == 401
        assert "accessToken" not in refresh_response.json()
        assert refresh_response.json()["detail"] == "Not authenticated"

    async def test_invalid_token(self, client):
        await client.post("/auth/register", json=valid_user_body)
        login_response = await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": valid_user_body["password"]}
        )
        client.cookies.set("refresh_token", "invalid_token")
        refresh_response1 = await client.post("/auth/refresh")
        client.cookies.set("refresh_token", login_response.json()["accessToken"])
        refresh_response2 = await client.post("/auth/refresh")
        assert refresh_response1.status_code == 401
        assert "accessToken" not in refresh_response1.json()
        assert refresh_response1.json()["detail"] == "Not authenticated"
        assert refresh_response2.status_code == 401
        assert "accessToken" not in refresh_response2.json()
        assert refresh_response2.json()["detail"] == "Not authenticated"


class TestProfile:
    async def test_success(self, client):
        await client.post("/auth/register", json=valid_user_body)
        login_response = await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": valid_user_body["password"]}
        )
        profile_response = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {login_response.json()['accessToken']}"}
        )
        assert profile_response.status_code == 200
        user = profile_response.json()
        assert user["email"] == valid_user_body["email"]
        assert user["name"] == valid_user_body["name"]
        assert "password_hash" not in user

    async def test_invalid_token(self, client):
        await client.post("/auth/register", json=valid_user_body)
        login_response = await client.post(
            "/auth/login", json={"email": valid_user_body["email"], "password": valid_user_body["password"]}
        )
        profile_response1 = await client.get("/auth/me", headers={"Authorization": "Bearer invalid_token"})
        profile_response2 = await client.get(
            "/auth/me", headers={"Authorization": f"Bearer {login_response.cookies.get('refresh_token')}"}
        )
        assert profile_response1.status_code == 401
        assert profile_response1.json()["detail"] == "Not authenticated"
        assert profile_response2.status_code == 401
        assert profile_response2.json()["detail"] == "Not authenticated"
