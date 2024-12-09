"""
Library Management System - User Service API
==========================================

A FastAPI-based microservice that handles user management and book rental operations for a library system.
This service is part of a larger distributed system and interacts with a separate Book Service.

Key Features
-----------
* User Management (CRUD operations)
* Authentication using JWT tokens
* Book rental and return functionality
* Rental history tracking
* Role-based access control (admin/regular users)

Core Components
-------------
* User Model: Handles user data and authentication
* Rental Model: Manages book rental records
* OAuth2 Authentication: Provides secure access using JWT tokens
* SQLAlchemy Integration: Handles async database operations

API Endpoints
-----------
Authentication:
* POST /token: Login endpoint for obtaining access tokens

User Management:
* POST /users/: Create new user
* GET /users/: List all users (admin only)
* GET /users/me: Get current user details
* GET /users/{user_id}: Get specific user details
* PUT /users/{user_id}: Update user information
* DELETE /users/{user_id}: Delete user

Book Rental:
* POST /users/{user_id}/rent_book/{book_id}: Rent a book
* POST /users/{user_id}/return_book/{book_id}: Return a book
* GET /rentals/user/{user_id}: Get user's rental history
* GET /rentals/active: Get all active rentals (admin only)

Configuration
------------
Environment variables:
* SECRET_KEY: JWT encryption key
* DATABASE_URL: SQLAlchemy database URL
* BOOK_SERVICE_URL: URL of the Book Service
* ACCESS_TOKEN_EXPIRE_MINUTES: JWT token expiration time

Dependencies
-----------
* FastAPI: Web framework
* SQLAlchemy: Database ORM
* PyJWT: JWT token handling
* Passlib: Password hashing
* Pydantic: Data validation
* aiohttp: Async HTTP client for service communication

Database Models
-------------
User:
* id: UUID
* name: String
* email: String (unique)
* hashed_password: String
* rented_books: JSON
* is_admin: Boolean

Rental:
* id: UUID
* user_id: Foreign Key (User)
* book_id: String
* book_title: String
* book_author: String
* rental_date: DateTime
* return_date: DateTime (nullable)

Security
-------
* Password hashing using bcrypt
* JWT token-based authentication
* Role-based access control
* Input validation using Pydantic models

Error Handling
------------
* HTTP 400: Bad Request (validation errors)
* HTTP 401: Unauthorized (invalid credentials)
* HTTP 403: Forbidden (insufficient permissions)
* HTTP 404: Not Found (resource not found)
* HTTP 500: Internal Server Error (database/service errors)

Usage Example
-----------
```python
# Start the service
uvicorn main:app --reload

# Create a new user
POST /users/
{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123"
}

# Login and get token
POST /token
Form data: username=john@example.com&password=secure123

# Rent a book
POST /users/{user_id}/rent_book/{book_id}
Authorization: Bearer <token>
```

Notes
-----
* All database operations are asynchronous
* Book availability is managed by the separate Book Service
* User passwords are securely hashed before storage
* Admin users have additional privileges for user management
* All endpoints except user creation and login require authentication
"""