# from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy import Column, String, JSON, select, update
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from pydantic import BaseModel, EmailStr
# from typing import List, Dict, Optional
# import uuid
# import aiohttp

# # --- Database setup ---
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Async SQLite URL
# Base = declarative_base()
# engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # --- Models ---
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String, index=True)
#     email = Column(String, unique=True, index=True)
#     rented_books = Column(JSON, default=list)  # JSON column for storing book details

# # --- Pydantic Schemas ---
# class UserBase(BaseModel):
#     name: str
#     email: EmailStr

# class UserCreate(UserBase):
#     pass

# class UserUpdate(BaseModel):
#     name: Optional[str]
#     email: Optional[EmailStr]

# class UserResponse(UserBase):
#     id: str
#     rented_books: List[Dict[str, str]] = []  # List of rented books

#     class Config:
#         orm_mode = True

# # --- App initialization ---
# app = FastAPI()

# # Dependency to get DB session
# async def get_db():
#     async with SessionLocal() as db:
#         try:
#             yield db
#         finally:
#             await db.close()

# # --- Initialize Database ---
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # --- Endpoints ---
# BOOK_SERVICE_URL = "http://127.0.0.1:8000"  # Replace with the actual Book Service URL

# # Create User
# @app.post("/users/", response_model=UserResponse)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     db_user = User(
#         id=str(uuid.uuid4()),
#         name=user.name,
#         email=user.email,
#         rented_books=[],
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# # Get all users
# @app.get("/users/", response_model=List[UserResponse])
# async def read_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(User).offset(skip).limit(limit))
#     users = result.scalars().all()
#     return users

# # Get a single user
# @app.get("/users/{user_id}", response_model=UserResponse)
# async def read_user(user_id: str, db: AsyncSession = Depends(get_db)):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# # Rent a book
# @app.post("/users/{user_id}/rent_book/{book_id}")
# async def rent_book(user_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
#     # Fetch book details using aiohttp
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found")
#             book = await response.json()

#     # Check for book availability first
#     if book["available_copies"] <= 0:
#         raise HTTPException(status_code=400, detail="No copies available")

#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Check if the book is already rented by the user
#     if any(book["book_id"] == book_id for book in user.rented_books or []):
#         raise HTTPException(status_code=400, detail="You already have this book")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.put(
#             f"{BOOK_SERVICE_URL}/books/{book_id}",
#             json={"available_copies": book["available_copies"] - 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Append rented book details
#     rented_book_details = {"book_id": book_id, "title": book["title"], "author": book["author"]}
#     user.rented_books = user.rented_books or []  # Initialize if None
#     updated_rented_books = user.rented_books + [rented_book_details]  # Create new list
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book rented successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }
# @app.post("/users/{user_id}/return_book/{book_id}")
# async def return_book(user_id: str, book_id: str, db: AsyncSession = Depends(get_db)):
#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Check if the user has rented the book
#     rented_books = user.rented_books or []
#     book_to_return = next((book for book in rented_books if book["book_id"] == book_id), None)
#     if not book_to_return:
#         raise HTTPException(status_code=404, detail="No such book rented")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found in Book Service")
#             book = await response.json()

#         async with session.put(
#             f"{BOOK_SERVICE_URL}/books/{book_id}",
#             json={"available_copies": book["available_copies"] + 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Remove the returned book from the user's rented books
#     updated_rented_books = [book for book in rented_books if book["book_id"] != book_id]
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book returned successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }


#v2.0
# from fastapi import FastAPI, HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy import Column, String, JSON, select, update
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from pydantic import BaseModel, EmailStr, Field
# from typing import List, Dict, Optional
# import uuid
# import aiohttp
# import jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# import os

# # JWT Configuration
# SECRET_KEY = os.urandom(32)  # Generate a secure random secret key
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # --- Database setup ---
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Async SQLite URL
# Base = declarative_base()
# engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # --- Models ---
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     rented_books = Column(JSON, default=list)  # JSON column for storing book details

# # --- Pydantic Schemas ---
# class UserBase(BaseModel):
#     name: str
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str = Field(..., min_length=6)

# class UserUpdate(BaseModel):
#     name: Optional[str] = None
#     email: Optional[EmailStr] = None

# class UserResponse(UserBase):
#     id: str
#     rented_books: List[Dict[str, str]] = []

#     class Config:
#         orm_mode = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     email: Optional[str] = None

# # --- App initialization ---
# app = FastAPI()

# # OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Dependency to get DB session
# async def get_db():
#     async with SessionLocal() as db:
#         try:
#             yield db
#         finally:
#             await db.close()

# # Password utility functions
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# # Token utility functions
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# async def get_user_by_email(db: AsyncSession, email: str):
#     result = await db.execute(select(User).filter(User.email == email))
#     return result.scalars().first()

# async def authenticate_user(db: AsyncSession, email: str, password: str):
#     user = await get_user_by_email(db, email)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
#     user = await get_user_by_email(db, email=email)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#     return user

# # --- Initialize Database ---
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # Token endpoint
# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     user = await authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.email})
#     return {"access_token": access_token, "token_type": "bearer"}

# # Create User
# @app.post("/users/", response_model=UserResponse)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     # Check if user already exists
#     existing_user = await get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     db_user = User(
#         id=str(uuid.uuid4()),
#         name=user.name,
#         email=user.email,
#         hashed_password=get_password_hash(user.password),
#         rented_books=[],
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# # Get all users (protected route)
# @app.get("/users/", response_model=List[UserResponse])
# async def read_users(
#     skip: int = 0, 
#     limit: int = 10, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).offset(skip).limit(limit))
#     users = result.scalars().all()
#     return users

# # Get a single user (protected route)
# @app.get("/users/{user_id}", response_model=UserResponse)
# async def read_user(
#     user_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# # Rent a book (protected route)
# @app.post("/users/{user_id}/rent_book/{book_id}")
# async def rent_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Book rental logic remains the same as in the previous implementation
#     # Fetch book details using aiohttp
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"http://127.0.0.1:8000/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found")
#             book = await response.json()

#     # Check for book availability first
#     if book["available_copies"] <= 0:
#         raise HTTPException(status_code=400, detail="No copies available")

#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Ensure the current user is renting their own book
#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to rent for this user")

#     # Check if the book is already rented by the user
#     if any(book["book_id"] == book_id for book in user.rented_books or []):
#         raise HTTPException(status_code=400, detail="You already have this book")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.put(
#             f"http://127.0.0.1:8000/books/{book_id}",
#             json={"available_copies": book["available_copies"] - 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Append rented book details
#     rented_book_details = {"book_id": book_id, "title": book["title"], "author": book["author"]}
#     user.rented_books = user.rented_books or []  # Initialize if None
#     updated_rented_books = user.rented_books + [rented_book_details]  # Create new list
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book rented successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

# # Return a book (protected route)
# @app.post("/users/{user_id}/return_book/{book_id}")
# async def return_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Ensure the current user is returning their own book
#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to return for this user")

#     # Check if the user has rented the book
#     rented_books = user.rented_books or []
#     book_to_return = next((book for book in rented_books if book["book_id"] == book_id), None)
#     if not book_to_return:
#         raise HTTPException(status_code=404, detail="No such book rented")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"http://127.0.0.1:8000/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found in Book Service")
#             book = await response.json()

#         async with session.put(
#             f"http://127.0.0.1:8000/books/{book_id}",
#             json={"available_copies": book["available_copies"] + 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Remove the returned book from the user's rented books
#     updated_rented_books = [book for book in rented_books if book["book_id"] != book_id]
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book returned successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

#3.0
# from fastapi import FastAPI, HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy import Column, String, JSON, Boolean, select, update
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from pydantic import BaseModel, EmailStr, Field
# from typing import List, Dict, Optional
# import uuid
# import aiohttp
# import jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# import os

# # JWT Configuration
# SECRET_KEY = os.urandom(32)  # Generate a secure random secret key
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # --- Database setup ---
# DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # Async SQLite URL
# Base = declarative_base()
# engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # --- Models ---
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     rented_books = Column(JSON, default=list)  # JSON column for storing book details
#     is_admin = Column(Boolean, default=False)  # Add admin role

# # --- Pydantic Schemas ---
# class UserBase(BaseModel):
#     name: str
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str = Field(..., min_length=6)
#     is_admin: Optional[bool] = False

# class UserUpdate(BaseModel):
#     name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     # Optional password update
#     password: Optional[str] = Field(None, min_length=6)

# class UserResponse(UserBase):
#     id: str
#     rented_books: List[Dict[str, str]] = []
#     is_admin: bool

#     class Config:
#         orm_mode = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     email: Optional[str] = None
#     is_admin: Optional[bool] = False

# # --- App initialization ---
# app = FastAPI()

# # OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Dependency to get DB session
# async def get_db():
#     async with SessionLocal() as db:
#         try:
#             yield db
#         finally:
#             await db.close()

# # Password utility functions
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# # Token utility functions
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# async def get_user_by_email(db: AsyncSession, email: str):
#     result = await db.execute(select(User).filter(User.email == email))
#     return result.scalars().first()

# async def authenticate_user(db: AsyncSession, email: str, password: str):
#     user = await get_user_by_email(db, email)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         is_admin: bool = payload.get("is_admin", False)
#         if email is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
#     user = await get_user_by_email(db, email=email)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
#     # Add is_admin to the user
#     user.is_admin = is_admin
#     return user

# # --- Initialize Database ---
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # Token endpoint
# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     user = await authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(
#         data={"sub": user.email, "is_admin": user.is_admin}
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# # Create User
# @app.post("/users/", response_model=UserResponse)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     # Check if user already exists
#     existing_user = await get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create new user
#     db_user = User(
#         id=str(uuid.uuid4()),
#         name=user.name,
#         email=user.email,
#         hashed_password=get_password_hash(user.password),
#         rented_books=[],
#         is_admin=user.is_admin or False,  # Default to False if not specified
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# # Get all users (admin-only route)
# @app.get("/users/", response_model=List[UserResponse])
# async def read_users(
#     skip: int = 0, 
#     limit: int = 10, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Check if current user is admin
#     if not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to list users")
    
#     result = await db.execute(select(User).offset(skip).limit(limit))
#     users = result.scalars().all()
#     return users

# # Get a single user (self or admin route)
# @app.get("/users/{user_id}", response_model=UserResponse)
# async def read_user(
#     user_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # User can only see their own profile or if they are admin
#     if user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to view this user")
    
#     return user

# # Update User Profile
# @app.put("/users/{user_id}", response_model=UserResponse)
# async def update_user(
#     user_id: str, 
#     user_update: UserUpdate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Find the user to update
#     result = await db.execute(select(User).filter(User.id == user_id))
#     db_user = result.scalars().first()
    
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Check authorization: user can only update their own profile unless they are admin
#     if db_user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
#     # Update fields if provided
#     if user_update.name is not None:
#         db_user.name = user_update.name
    
#     if user_update.email is not None:
#         # Check if new email is already in use
#         existing_user = await get_user_by_email(db, user_update.email)
#         if existing_user and existing_user.id != user_id:
#             raise HTTPException(status_code=400, detail="Email already in use")
#         db_user.email = user_update.email
    
#     # Update password if provided
#     if user_update.password is not None:
#         db_user.hashed_password = get_password_hash(user_update.password)
    
#     # Commit changes
#     await db.commit()
#     await db.refresh(db_user)
    
#     return db_user

# # Delete User
# @app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Find the user to delete
#     result = await db.execute(select(User).filter(User.id == user_id))
#     db_user = result.scalars().first()
    
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     # Check authorization: user can only delete their own profile or if they are admin
#     if db_user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
#     # Delete user
#     await db.delete(db_user)
#     await db.commit()
    
#     return None

# # Keep existing book rental routes from the previous implementation
# # (rent_book and return_book methods remain the same)
# # # Rent a book (protected route)
# @app.post("/users/{user_id}/rent_book/{book_id}")
# async def rent_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Book rental logic remains the same as in the previous implementation
#     # Fetch book details using aiohttp
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"http://127.0.0.1:8000/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found")
#             book = await response.json()

#     # Check for book availability first
#     if book["available_copies"] <= 0:
#         raise HTTPException(status_code=400, detail="No copies available")

#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Ensure the current user is renting their own book
#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to rent for this user")

#     # Check if the book is already rented by the user
#     if any(book["book_id"] == book_id for book in user.rented_books or []):
#         raise HTTPException(status_code=400, detail="You already have this book")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.put(
#             f"http://127.0.0.1:8000/books/{book_id}",
#             json={"available_copies": book["available_copies"] - 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Append rented book details
#     rented_book_details = {"book_id": book_id, "title": book["title"], "author": book["author"]}
#     user.rented_books = user.rented_books or []  # Initialize if None
#     updated_rented_books = user.rented_books + [rented_book_details]  # Create new list
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book rented successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

# # Return a book (protected route)
# @app.post("/users/{user_id}/return_book/{book_id}")
# async def return_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     # Fetch user details
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Ensure the current user is returning their own book
#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to return for this user")

#     # Check if the user has rented the book
#     rented_books = user.rented_books or []
#     book_to_return = next((book for book in rented_books if book["book_id"] == book_id), None)
#     if not book_to_return:
#         raise HTTPException(status_code=404, detail="No such book rented")

#     # Update book availability in Book Service
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"http://127.0.0.1:8000/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found in Book Service")
#             book = await response.json()

#         async with session.put(
#             f"http://127.0.0.1:8000/books/{book_id}",
#             json={"available_copies": book["available_copies"] + 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     # Remove the returned book from the user's rented books
#     updated_rented_books = [book for book in rented_books if book["book_id"] != book_id]
#     user.rented_books = updated_rented_books  # Reassign to trigger SQLAlchemy tracking

#     # Commit changes to the database
#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book returned successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

#docker
# from fastapi import FastAPI, HTTPException, Depends, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from sqlalchemy import Column, String, JSON, Boolean, select, update
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# from pydantic import BaseModel, EmailStr, Field
# from typing import List, Dict, Optional
# import uuid
# import aiohttp
# import jwt
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# import os

# # Environment Configuration
# SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
# DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite+aiosqlite:///./test.db")
# BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://127.0.0.1:8000')
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Database setup
# Base = declarative_base()
# engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Password hashing context
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # User Model
# class User(Base):
#     __tablename__ = "users"

#     id = Column(String, primary_key=True, index=True)
#     name = Column(String, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     rented_books = Column(JSON, default=list)
#     is_admin = Column(Boolean, default=False)

# # Pydantic Schemas
# class UserBase(BaseModel):
#     name: str
#     email: EmailStr

# class UserCreate(UserBase):
#     password: str = Field(..., min_length=6)
#     is_admin: Optional[bool] = False

# class UserUpdate(BaseModel):
#     name: Optional[str] = None
#     email: Optional[EmailStr] = None
#     password: Optional[str] = Field(None, min_length=6)

# class UserResponse(UserBase):
#     id: str
#     rented_books: List[Dict[str, str]] = []
#     is_admin: bool

#     class Config:
#         orm_mode = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str

# class TokenData(BaseModel):
#     email: Optional[str] = None
#     is_admin: Optional[bool] = False

# # FastAPI App
# app = FastAPI(title="User Service", description="User Management and Book Rental Service")

# # OAuth2 scheme
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Database Session Dependency
# async def get_db():
#     async with SessionLocal() as db:
#         try:
#             yield db
#         finally:
#             await db.close()

# # Password Utility Functions
# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

# # Token Utility Functions
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# # User Retrieval Functions
# async def get_user_by_email(db: AsyncSession, email: str):
#     result = await db.execute(select(User).filter(User.email == email))
#     return result.scalars().first()

# async def authenticate_user(db: AsyncSession, email: str, password: str):
#     user = await get_user_by_email(db, email)
#     if not user:
#         return False
#     if not verify_password(password, user.hashed_password):
#         return False
#     return user

# async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         is_admin: bool = payload.get("is_admin", False)
#         if email is None:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
#     user = await get_user_by_email(db, email=email)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
#     user.is_admin = is_admin
#     return user

# # Database Initialization
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# # Authentication Endpoints
# @app.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
#     user = await authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(
#         data={"sub": user.email, "is_admin": user.is_admin}
#     )
#     return {"access_token": access_token, "token_type": "bearer"}

# # User Management Endpoints
# @app.post("/users/", response_model=UserResponse)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     existing_user = await get_user_by_email(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     db_user = User(
#         id=str(uuid.uuid4()),
#         name=user.name,
#         email=user.email,
#         hashed_password=get_password_hash(user.password),
#         rented_books=[],
#         is_admin=user.is_admin or False,
#     )
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

# @app.get("/users/", response_model=List[UserResponse])
# async def read_users(
#     skip: int = 0, 
#     limit: int = 10, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     if not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to list users")
    
#     result = await db.execute(select(User).offset(skip).limit(limit))
#     users = result.scalars().all()
#     return users

# @app.get("/users/{user_id}", response_model=UserResponse)
# async def read_user(
#     user_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to view this user")
    
#     return user

# @app.put("/users/{user_id}", response_model=UserResponse)
# async def update_user(
#     user_id: str, 
#     user_update: UserUpdate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     db_user = result.scalars().first()
    
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if db_user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
#     if user_update.name is not None:
#         db_user.name = user_update.name
    
#     if user_update.email is not None:
#         existing_user = await get_user_by_email(db, user_update.email)
#         if existing_user and existing_user.id != user_id:
#             raise HTTPException(status_code=400, detail="Email already in use")
#         db_user.email = user_update.email
    
#     if user_update.password is not None:
#         db_user.hashed_password = get_password_hash(user_update.password)
    
#     await db.commit()
#     await db.refresh(db_user)
    
#     return db_user

# @app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(
#     user_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     db_user = result.scalars().first()
    
#     if not db_user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     if db_user.id != current_user.id and not current_user.is_admin:
#         raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
#     await db.delete(db_user)
#     await db.commit()
    
#     return None

# # Book Rental Endpoints
# @app.post("/users/{user_id}/rent_book/{book_id}")
# async def rent_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found")
#             book = await response.json()

#     if book["available_copies"] <= 0:
#         raise HTTPException(status_code=400, detail="No copies available")

#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to rent for this user")

#     if any(rented_book["book_id"] == book_id for rented_book in user.rented_books or []):
#         raise HTTPException(status_code=400, detail="You already have this book")

#     async with aiohttp.ClientSession() as session:
#         async with session.put(
#             f"{BOOK_SERVICE_URL}/books/{book_id}",
#             json={"available_copies": book["available_copies"] - 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     rented_book_details = {"book_id": book_id, "title": book["title"], "author": book["author"]}
#     user.rented_books = user.rented_books or []
#     updated_rented_books = user.rented_books + [rented_book_details]
#     user.rented_books = updated_rented_books

#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book rented successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

# @app.post("/users/{user_id}/return_book/{book_id}")
# async def return_book(
#     user_id: str, 
#     book_id: str, 
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(select(User).filter(User.id == user_id))
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.id != current_user.id:
#         raise HTTPException(status_code=403, detail="Not authorized to return for this user")

#     rented_books = user.rented_books or []
#     book_to_return = next((book for book in rented_books if book["book_id"] == book_id), None)
#     if not book_to_return:
#         raise HTTPException(status_code=404, detail="No such book rented")

#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
#             if response.status != 200:
#                 raise HTTPException(status_code=404, detail="Book not found in Book Service")
#             book = await response.json()

#         async with session.put(
#             f"{BOOK_SERVICE_URL}/books/{book_id}",
#             json={"available_copies": book["available_copies"] + 1},
#         ) as update_response:
#             if update_response.status != 200:
#                 raise HTTPException(status_code=500, detail="Failed to update book availability")

#     updated_rented_books = [book for book in rented_books if book["book_id"] != book_id]
#     user.rented_books = updated_rented_books

#     await db.commit()
#     await db.refresh(user)

#     return {
#         "detail": "Book returned successfully",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "rented_books": user.rented_books,
#         },
#     }

# # Health Check Endpoint
# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}




from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, String, JSON, Boolean, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional
import uuid
import aiohttp
import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from jose import jwt


# Environment Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
DATABASE_URL = os.environ.get('DATABASE_URL', "sqlite+aiosqlite:///./test.db")
BOOK_SERVICE_URL = os.environ.get('BOOK_SERVICE_URL', 'http://127.0.0.1:8000')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database setup
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User Model
class Rental(Base):
    __tablename__ = "rentals"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    book_id = Column(String)
    book_title = Column(String)
    book_author = Column(String)
    rental_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="rentals")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rented_books = Column(JSON, default=list)
    is_admin = Column(Boolean, default=False)
    
    rentals = relationship("Rental", back_populates="user")

# Add these Pydantic models
class RentalBase(BaseModel):
    book_id: str
    book_title: str
    book_author: str

class RentalCreate(RentalBase):
    pass

class RentalResponse(RentalBase):
    id: str
    user_id: str
    rental_date: datetime
    return_date: Optional[datetime]

    class Config:
        orm_mode = True
# Pydantic Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    is_admin: Optional[bool] = False

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(UserBase):
    id: str
    rented_books: List[Dict[str, str]] = []
    is_admin: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    is_admin: Optional[bool] = False

# FastAPI App
app = FastAPI(title="User Service", description="User Management and Book Rental Service")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database Session Dependency
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

# Password Utility Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Token Utility Functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# User Retrieval Functions
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        is_admin: bool = payload.get("is_admin", False)
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    
    user = await get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    user.is_admin = is_admin
    return user

# Database Initialization
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Authentication Endpoints
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "is_admin": user.is_admin}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
# User Management Endpoints
@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user = User(
        id=str(uuid.uuid4()),
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        rented_books=[],
        is_admin=user.is_admin or False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 10, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to list users")
    
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@app.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view this user")
    
    return user

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, 
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    if user_update.name is not None:
        db_user.name = user_update.name
    
    if user_update.email is not None:
        existing_user = await get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        db_user.email = user_update.email
    
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)
    
    await db.commit()
    await db.refresh(db_user)
    
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    
    await db.delete(db_user)
    await db.commit()
    
    return None

# Book Rental Endpoints

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON, create_engine
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
import uuid

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rented_books = Column(JSON, default=list)
    is_admin = Column(Boolean, default=False)
    
    rentals = relationship("Rental", back_populates="user")

class Rental(Base):
    __tablename__ = "rentals"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    book_id = Column(String)
    book_title = Column(String)
    book_author = Column(String)
    rental_date = Column(DateTime, default=datetime.utcnow)
    return_date = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="rentals")

# Update these endpoints in your user service
@app.post("/users/{user_id}/rent_book/{book_id}")
async def rent_book(
    user_id: str, 
    book_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
            if response.status != 200:
                raise HTTPException(status_code=404, detail="Book not found")
            book = await response.json()

    if book["available_copies"] <= 0:
        raise HTTPException(status_code=400, detail="No copies available")

    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to rent for this user")

    if any(rented_book["book_id"] == book_id for rented_book in user.rented_books or []):
        raise HTTPException(status_code=400, detail="You already have this book")

    # Create new rental record
    new_rental = Rental(
        id=str(uuid.uuid4()),
        user_id=user.id,
        book_id=book_id,
        book_title=book["title"],
        book_author=book["author"],
        rental_date=datetime.utcnow()
    )
    db.add(new_rental)

    # Update book availability
    async with aiohttp.ClientSession() as session:
        async with session.put(
            f"{BOOK_SERVICE_URL}/books/{book_id}",
            json={"available_copies": book["available_copies"] - 1},
        ) as update_response:
            if update_response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to update book availability")

    # Update user's rented_books JSON field
    rented_book_details = {"book_id": book_id, "title": book["title"], "author": book["author"]}
    user.rented_books = user.rented_books or []
    updated_rented_books = user.rented_books + [rented_book_details]
    user.rented_books = updated_rented_books

    try:
        await db.commit()
        await db.refresh(user)
        await db.refresh(new_rental)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save rental: {str(e)}")

    return {
        "detail": "Book rented successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "rented_books": user.rented_books,
        },
        "rental": {
            "id": new_rental.id,
            "book_title": new_rental.book_title,
            "rental_date": new_rental.rental_date
        }
    }

@app.post("/users/{user_id}/return_book/{book_id}")
async def return_book(
    user_id: str, 
    book_id: str, 
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to return for this user")

    # Find active rental
    rental_result = await db.execute(
        select(Rental).filter(
            Rental.user_id == user_id,
            Rental.book_id == book_id,
            Rental.return_date.is_(None)
        )
    )
    rental = rental_result.scalars().first()
    
    if not rental:
        raise HTTPException(status_code=404, detail="No active rental found for this book")

    # Update rental record
    rental.return_date = datetime.utcnow()

    # Update book availability
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BOOK_SERVICE_URL}/books/{book_id}") as response:
            if response.status != 200:
                raise HTTPException(status_code=404, detail="Book not found in Book Service")
            book = await response.json()

        async with session.put(
            f"{BOOK_SERVICE_URL}/books/{book_id}",
            json={"available_copies": book["available_copies"] + 1},
        ) as update_response:
            if update_response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to update book availability")

    # Update user's rented_books JSON field
    rented_books = user.rented_books or []
    updated_rented_books = [book for book in rented_books if book["book_id"] != book_id]
    user.rented_books = updated_rented_books

    try:
        await db.commit()
        await db.refresh(user)
        await db.refresh(rental)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save return: {str(e)}")

    return {
        "detail": "Book returned successfully",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "rented_books": user.rented_books,
        },
        "rental": {
            "id": rental.id,
            "book_title": rental.book_title,
            "return_date": rental.return_date
        }
    }

@app.get("/rentals/user/{user_id}", response_model=List[RentalResponse])
async def get_user_rentals(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view these rentals")
    
    result = await db.execute(
        select(Rental)
        .filter(Rental.user_id == user_id)
        .order_by(Rental.rental_date.desc())
    )
    rentals = result.scalars().all()
    return rentals

@app.get("/rentals/active", response_model=List[RentalResponse])
async def get_active_rentals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view all rentals")
    
    result = await db.execute(
        select(Rental)
        .filter(Rental.return_date.is_(None))
        .order_by(Rental.rental_date.desc())
    )
    rentals = result.scalars().all()
    return rentals

