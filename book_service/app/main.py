# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy import Column, String, Integer, create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# import uuid
# from pydantic import BaseModel

# # Database Configuration
# DATABASE_URL = "sqlite:///./test.db"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Base = declarative_base()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Initialize FastAPI
# app = FastAPI()

# # Database Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # Book Model
# class Book(Base):
#     __tablename__ = "books"

#     id = Column(String, primary_key=True, index=True)
#     title = Column(String, index=True)
#     author = Column(String, index=True)
#     genre = Column(String, index=True)
#     available_copies = Column(Integer)

# # Pydantic Models
# class BookCreate(BaseModel):
#     title: str
#     author: str
#     genre: str
#     available_copies: int

# class BookUpdate(BaseModel):
#     title: str | None = None
#     author: str | None = None
#     genre: str | None = None
#     available_copies: int | None = None

# class BookResponse(BookCreate):
#     id: str

#     class Config:
#         orm_mode = True

# # Create Database Tables
# @app.on_event("startup")
# def startup():
#     Base.metadata.create_all(bind=engine)

# # CRUD Operations

# ## Create a Book
# @app.post("/books/", response_model=BookResponse)
# def create_book(book: BookCreate, db: Session = Depends(get_db)):
#     db_book = Book(
#         id=str(uuid.uuid4()),
#         title=book.title,
#         author=book.author,
#         genre=book.genre,
#         available_copies=book.available_copies,
#     )
#     db.add(db_book)
#     db.commit()
#     db.refresh(db_book)
#     return db_book

# ## Read All Books
# @app.get("/books/", response_model=list[BookResponse])
# def get_books(db: Session = Depends(get_db)):
#     return db.query(Book).all()

# ## Read a Book by ID
# @app.get("/books/{book_id}", response_model=BookResponse)
# def get_book(book_id: str, db: Session = Depends(get_db)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")
#     return book

# ## Update a Book
# @app.put("/books/{book_id}", response_model=BookResponse)
# def update_book(book_id: str, book_update: BookUpdate, db: Session = Depends(get_db)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     # Update fields if provided
#     if book_update.title is not None:
#         book.title = book_update.title
#     if book_update.author is not None:
#         book.author = book_update.author
#     if book_update.genre is not None:
#         book.genre = book_update.genre
#     if book_update.available_copies is not None:
#         book.available_copies = book_update.available_copies

#     db.commit()
#     db.refresh(book)
#     return book

# ## Delete a Book
# @app.delete("/books/{book_id}")
# def delete_book(book_id: str, db: Session = Depends(get_db)):
#     book = db.query(Book).filter(Book.id == book_id).first()
#     if not book:
#         raise HTTPException(status_code=404, detail="Book not found")
    
#     db.delete(book)
#     db.commit()
#     return {"message": f"Book with id {book_id} deleted successfully"}

# # Root Route
# @app.get("/")
# def root():
#     return {"message": "Welcome to the Book Service!"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer
import uuid
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy import text
from typing import AsyncGenerator 
from sqlalchemy.future import select

# Database Configuration
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Initialize FastAPI
app = FastAPI(title = "Book Service" , description="Books Management")

# Database Dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db

# Book Model
class Book(Base):
    __tablename__ = "books"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    genre = Column(String, index=True)
    available_copies = Column(Integer)

# Pydantic Models
class BookCreate(BaseModel):
    title: str
    author: str
    genre: str
    available_copies: int

class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    available_copies: int | None = None

# For API responses
class BookResponse(BookCreate):
    id: str

    class Config:
        orm_mode = True

# Create Database Tables
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CRUD Operations

## Create a Book
@app.post("/books/", response_model=BookResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = Book(
        id=str(uuid.uuid4()),
        title=book.title,
        author=book.author,
        genre=book.genre,
        available_copies=book.available_copies,
    )
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

## Read All Books
# Get Books Route
@app.get("/books/", response_model=list[BookResponse])
async def get_books(db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(Book))  # Use execute with select for async query
        books = result.scalars().all()  # Get results
    return books

## Read a Book by ID
@app.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).filter(Book.id == book_id))  # Use select with filter
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, book_update: BookUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).filter(Book.id == book_id))  # Use select with filter
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update fields if provided
    for field, value in book_update.dict(exclude_unset=True).items():
        setattr(book, field, value)

    await db.commit()  # Commit changes
    await db.refresh(book)  # Refresh the object to reflect changes
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).filter(Book.id == book_id))  # Use select with filter
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(book)  # Delete the book
    await db.commit()  # Commit changes
    return {"message": f"Book with id {book_id} deleted successfully"}
