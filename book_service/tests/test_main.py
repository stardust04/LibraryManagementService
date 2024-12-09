# # tests/test_main.py

# import sys
# import os
# import pytest
# import pytest_asyncio
# from httpx import AsyncClient
# from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.pool import StaticPool

# # Add the app directory to Python path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from app.main import app, Base, get_db

# # Test database URL
# TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# # Create async engine for testing
# engine_test = create_async_engine(
#     TEST_DATABASE_URL,
#     connect_args={"check_same_thread": False},
#     poolclass=StaticPool,
# )

# # Create async session for testing
# TestAsyncSessionLocal = sessionmaker(
#     engine_test, 
#     class_=AsyncSession, 
#     expire_on_commit=False
# )

# @pytest_asyncio.fixture
# async def db_session():
#     """
#     Create a fresh database for each test.
#     """
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
    
#     async with TestAsyncSessionLocal() as session:
#         yield session
        
#     async with engine_test.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)

# @pytest_asyncio.fixture
# async def client(db_session):
#     """
#     Create a test client using the test database session.
#     """
#     async def override_get_db():
#         yield db_session

#     app.dependency_overrides[get_db] = override_get_db
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
#     app.dependency_overrides.clear()

# @pytest.mark.asyncio
# async def test_create_book(client):
#     """Test creating a new book"""
#     book_data = {
#         "title": "Test Book",
#         "author": "Test Author",
#         "genre": "Test Genre",
#         "available_copies": 5
#     }
    
#     response = await client.post("/books/", json=book_data)
#     assert response.status_code == 200
    
#     data = response.json()
#     assert data["title"] == book_data["title"]
#     assert data["author"] == book_data["author"]
#     assert data["genre"] == book_data["genre"]
#     assert data["available_copies"] == book_data["available_copies"]
#     assert "id" in data

# @pytest.mark.asyncio
# async def test_get_books(client):
#     """Test getting all books"""
#     # First create some books
#     book_data = [
#         {
#             "title": "Book 1",
#             "author": "Author 1",
#             "genre": "Genre 1",
#             "available_copies": 3
#         },
#         {
#             "title": "Book 2",
#             "author": "Author 2",
#             "genre": "Genre 2",
#             "available_copies": 2
#         }
#     ]
    
#     for book in book_data:
#         await client.post("/books/", json=book)
    
#     response = await client.get("/books/")
#     assert response.status_code == 200
    
#     data = response.json()
#     assert len(data) == 2
#     assert data[0]["title"] == "Book 1"
#     assert data[1]["title"] == "Book 2"

# @pytest.mark.asyncio
# async def test_get_book(client):
#     """Test getting a specific book"""
#     # First create a book
#     book_data = {
#         "title": "Test Book",
#         "author": "Test Author",
#         "genre": "Test Genre",
#         "available_copies": 5
#     }
    
#     create_response = await client.post("/books/", json=book_data)
#     book_id = create_response.json()["id"]
    
#     response = await client.get(f"/books/{book_id}")
#     assert response.status_code == 200
    
#     data = response.json()
#     assert data["title"] == book_data["title"]
#     assert data["id"] == book_id

# @pytest.mark.asyncio
# async def test_update_book(client):
#     """Test updating a book"""
#     # First create a book
#     book_data = {
#         "title": "Original Title",
#         "author": "Original Author",
#         "genre": "Original Genre",
#         "available_copies": 5
#     }
    
#     create_response = await client.post("/books/", json=book_data)
#     book_id = create_response.json()["id"]
    
#     # Update the book
#     update_data = {
#         "title": "Updated Title",
#         "available_copies": 3
#     }
    
#     response = await client.put(f"/books/{book_id}", json=update_data)
#     assert response.status_code == 200
    
#     data = response.json()
#     assert data["title"] == update_data["title"]
#     assert data["available_copies"] == update_data["available_copies"]
#     assert data["author"] == book_data["author"]  # Unchanged field

# @pytest.mark.asyncio
# async def test_delete_book(client):
#     """Test deleting a book"""
#     # First create a book
#     book_data = {
#         "title": "Test Book",
#         "author": "Test Author",
#         "genre": "Test Genre",
#         "available_copies": 5
#     }
    
#     create_response = await client.post("/books/", json=book_data)
#     book_id = create_response.json()["id"]
    
#     # Delete the book
#     response = await client.delete(f"/books/{book_id}")
#     assert response.status_code == 200
    
#     # Verify book is deleted
#     get_response = await client.get(f"/books/{book_id}")
#     assert get_response.status_code == 404

# tests/test_main.py

import sys
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app, Base, get_db

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for testing
engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create async session for testing
TestAsyncSessionLocal = sessionmaker(
    engine_test, 
    class_=AsyncSession, 
    expire_on_commit=False
)

@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Set up the database before each test"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session():
    """Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback occurs automatically."""
    async with TestAsyncSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """Get test client with overridden dependencies"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_book(client):
    """Test creating a new book"""
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Test Genre",
        "available_copies": 5
    }
    
    response = await client.post("/books/", json=book_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert data["genre"] == book_data["genre"]
    assert data["available_copies"] == book_data["available_copies"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_books(client, db_session):
    """Test getting all books"""
    # Create books one by one to avoid transaction issues
    book_data = [
        {
            "title": "Book 1",
            "author": "Author 1",
            "genre": "Genre 1",
            "available_copies": 3
        },
        {
            "title": "Book 2",
            "author": "Author 2",
            "genre": "Genre 2",
            "available_copies": 2
        }
    ]
    
    # Create books sequentially with proper transaction handling
    for book in book_data:
        response = await client.post("/books/", json=book)
        assert response.status_code == 200
        await db_session.commit()
    
    # Get all books
    response = await client.get("/books/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    
    # Sort the results by title to ensure consistent ordering
    data = sorted(data, key=lambda x: x["title"])
    assert data[0]["title"] == "Book 1"
    assert data[1]["title"] == "Book 2"
@pytest.mark.asyncio
async def test_get_book(client):
    """Test getting a specific book"""
    # First create a book
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Test Genre",
        "available_copies": 5
    }
    
    create_response = await client.post("/books/", json=book_data)
    assert create_response.status_code == 200
    book_id = create_response.json()["id"]
    
    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["id"] == book_id

@pytest.mark.asyncio
async def test_update_book(client):
    """Test updating a book"""
    # First create a book
    book_data = {
        "title": "Original Title",
        "author": "Original Author",
        "genre": "Original Genre",
        "available_copies": 5
    }
    
    create_response = await client.post("/books/", json=book_data)
    assert create_response.status_code == 200
    book_id = create_response.json()["id"]
    
    # Update the book
    update_data = {
        "title": "Updated Title",
        "available_copies": 3
    }
    
    response = await client.put(f"/books/{book_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["available_copies"] == update_data["available_copies"]
    assert data["author"] == book_data["author"]  # Unchanged field

@pytest.mark.asyncio
async def test_delete_book(client):
    """Test deleting a book"""
    # First create a book
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "genre": "Test Genre",
        "available_copies": 5
    }
    
    create_response = await client.post("/books/", json=book_data)
    assert create_response.status_code == 200
    book_id = create_response.json()["id"]
    
    # Delete the book
    response = await client.delete(f"/books/{book_id}")
    assert response.status_code == 200
    
    # Verify book is deleted
    get_response = await client.get(f"/books/{book_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_get_nonexistent_book(client):
    """Test getting a book that doesn't exist"""
    response = await client.get("/books/nonexistent-id")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_book(client):
    """Test updating a book that doesn't exist"""
    update_data = {
        "title": "Updated Title"
    }
    response = await client.put("/books/nonexistent-id", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_book(client):
    """Test deleting a book that doesn't exist"""
    response = await client.delete("/books/nonexistent-id")
    assert response.status_code == 404