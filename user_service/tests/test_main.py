import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

from app.main import (
    app, Base, get_db, SECRET_KEY, ALGORITHM,
    User, Rental, get_password_hash
)

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    engine_test, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Test data
test_user_data = {
    "name": "Test User",
    "email": "test@example.com",
    "password": "testpass123",
    "is_admin": False
}

test_admin_data = {
    "name": "Admin User",
    "email": "admin@example.com",
    "password": "adminpass123",
    "is_admin": True
}

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_user(client):
    response = await client.post("/users/", json=test_user_data)
    return response.json()

@pytest_asyncio.fixture
async def test_admin(client):
    response = await client.post("/users/", json=test_admin_data)
    return response.json()

@pytest_asyncio.fixture
async def user_token(test_user, client):
    response = await client.post(
        "/token",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    return response.json()["access_token"]

@pytest_asyncio.fixture
async def admin_token(test_admin, client):
    response = await client.post(
        "/token",
        data={
            "username": test_admin_data["email"],
            "password": test_admin_data["password"]
        }
    )
    return response.json()["access_token"]

# Authentication Tests
@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["name"] == test_user_data["name"]
    assert "id" in data

@pytest.mark.asyncio
async def test_create_duplicate_user(client, test_user):
    response = await client.post("/users/", json=test_user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login(client, test_user):
    response = await client.post(
        "/token",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# User Management Tests
@pytest.mark.asyncio
async def test_read_users_me(client, user_token):
    response = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]

@pytest.mark.asyncio
async def test_read_users_unauthorized(client):
    response = await client.get("/users/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_read_users_admin(client, admin_token):
    response = await client.get(
        "/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_update_user(client, test_user, user_token):
    update_data = {"name": "Updated Name"}
    response = await client.put(
        f"/users/{test_user['id']}",
        headers={"Authorization": f"Bearer {user_token}"},
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"

# Rental Tests
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_rent_book(client, test_user, user_token):
    book_id = "test-book-id"
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "available_copies": 1
    }

    # Create mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=book_data)

    # Create mock context manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response

    # Mock both get and put requests
    with patch('aiohttp.ClientSession.get', return_value=mock_context), \
         patch('aiohttp.ClientSession.put', return_value=mock_context):
        
        response = await client.post(
            f"/users/{test_user['id']}/rent_book/{book_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "rental" in data
        assert data["rental"]["book_title"] == book_data["title"]

# @pytest.mark.asyncio
# async def test_return_book(client, test_user, user_token, db_session):
#     book_id = "test-book-id"
#     book_data = {
#         "title": "Test Book",
#         "author": "Test Author",
#         "available_copies": 0
#     }

#     # Create mock response for book service
#     mock_response = AsyncMock()
#     mock_response.status = 200
#     mock_response.json = AsyncMock(return_value=book_data)

#     # Create mock context manager
#     mock_context = AsyncMock()
#     mock_context.__aenter__.return_value = mock_response

#     # First rent a book
#     with patch('aiohttp.ClientSession.get', return_value=mock_context), \
#          patch('aiohttp.ClientSession.put', return_value=mock_context):
        
#         rent_response = await client.post(
#             f"/users/{test_user['id']}/rent_book/{book_id}",
#             headers={"Authorization": f"Bearer {user_token}"}
#         )
#         assert rent_response.status_code == 200
        
#         # Verify the rental record exists
#         rent_data = rent_response.json()
#         assert rent_data["rental"]["book_title"] == book_data["title"]

#     # Update book data for return (available copies increased)
#     book_data["available_copies"] = 1
#     mock_response.json = AsyncMock(return_value=book_data)

#     # Then return it
#     with patch('aiohttp.ClientSession.get', return_value=mock_context), \
#          patch('aiohttp.ClientSession.put', return_value=mock_context):
        
#         return_response = await client.post(
#             f"/users/{test_user['id']}/return_book/{book_id}",
#             headers={"Authorization": f"Bearer {user_token}"}
#         )
        
#         assert return_response.status_code == 200
#         return_data = return_response.json()
#         assert "rental" in return_data
#         assert return_data["rental"]["return_date"] is not None
#         assert return_data["rental"]["book_title"] == book_data["title"]

#         # Verify the book is removed from user's rented_books
#         assert not any(book["book_id"] == book_id for book in return_data["user"]["rented_books"])
@pytest.mark.asyncio
async def test_get_user_rentals(client, test_user, user_token):
    response = await client.get(
        f"/rentals/user/{test_user['id']}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_active_rentals_admin(client, admin_token):
    response = await client.get(
        "/rentals/active",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_get_active_rentals_unauthorized(client, user_token):
    response = await client.get(
        "/rentals/active",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403