"""
Library Management System - Book Service API
=========================================

A FastAPI-based microservice that handles book inventory management for a library system.
This service is part of a distributed library management system and provides CRUD operations
for managing books and their availability.

Key Features
-----------
* Book inventory management (CRUD operations)
* Asynchronous database operations
* Book availability tracking
* Simple and efficient API design

Core Components
-------------
* Book Model: Manages book data and inventory
* FastAPI Application: Handles HTTP requests
* SQLAlchemy Integration: Provides async database operations
* Pydantic Models: Ensures data validation

API Endpoints
-----------
Book Management:
* POST /books/: Create a new book
* GET /books/: List all books
* GET /books/{book_id}: Get specific book details
* PUT /books/{book_id}: Update book information
* DELETE /books/{book_id}: Remove a book from inventory

Database Configuration
--------------------
* Database: SQLite (using aiosqlite for async operations)
* URL Format: "sqlite+aiosqlite:///./test.db"
* Async Engine: SQLAlchemy async engine with echo enabled

Database Model
------------
Book:
* id: String (UUID, primary key)
* title: String (indexed)
* author: String (indexed)
* genre: String (indexed)
* available_copies: Integer

Data Models
----------
BookCreate (Input):
* title: String
* author: String
* genre: String
* available_copies: Integer

BookUpdate (Input):
* title: Optional[String]
* author: Optional[String]
* genre: Optional[String]
* available_copies: Optional[Integer]

BookResponse (Output):
* id: String
* title: String
* author: String
* genre: String
* available_copies: Integer

Error Handling
------------
* HTTP 404: Book not found
* HTTP 422: Validation error (invalid input data)
* HTTP 500: Internal server error (database errors)

Usage Example
-----------
```python
# Start the service
uvicorn main:app --reload

# Create a new book
POST /books/
{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction",
    "available_copies": 5
}

# Update book availability
PUT /books/{book_id}
{
    "available_copies": 4
}
```

Technical Notes
-------------
* All database operations are asynchronous
* Uses SQLAlchemy's new async query syntax
* Implements proper dependency injection for database sessions
* Automatic schema validation using Pydantic models
* Database connections are properly managed and cleaned up
* Uses UUID for book identification
* Indexes on frequently queried fields

Integration Points
---------------
This service is designed to work with other microservices in the library system,
particularly the User Service which manages book rentals and returns. The Book
Service maintains the source of truth for book availability and inventory.
"""