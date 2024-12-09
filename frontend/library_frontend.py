# import streamlit as st
# import requests

# # Configurations
# USER_SERVICE_URL = "http://127.0.0.1:8001"  # Replace with your User Service URL
# BOOK_SERVICE_URL = "http://127.0.0.1:8000"  # Replace with your Book Service URL

# # Helper Functions
# def get_books():
#     response = requests.get(f"{BOOK_SERVICE_URL}/books/")
#     if response.status_code == 200:
#         return response.json()
#     st.error("Failed to fetch books")
#     return []

# def get_users(token):
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get(f"{USER_SERVICE_URL}/users/", headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     st.error("Failed to fetch users")
#     return []

# def authenticate_user(email, password):
#     data = {"username": email, "password": password}
#     response = requests.post(f"{USER_SERVICE_URL}/token", data=data)
#     if response.status_code == 200:
#         return response.json()["access_token"]
#     st.error("Authentication failed")
#     return None

# def create_user(name, email, password, is_admin):
#     data = {"name": name, "email": email, "password": password, "is_admin": is_admin}
#     response = requests.post(f"{USER_SERVICE_URL}/users/", json=data)
#     if response.status_code == 200:
#         st.success("User created successfully!")
#         return response.json()
#     st.error("Failed to create user")
#     return None

# def rent_book(user_id, book_id, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(f"{USER_SERVICE_URL}/users/{user_id}/rent_book/{book_id}", headers=headers)
#     if response.status_code == 200:
#         st.success("Book rented successfully!")
#         return response.json()
#     st.error("Failed to rent book")
#     return None

# def return_book(user_id, book_id, token):
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.post(f"{USER_SERVICE_URL}/users/{user_id}/return_book/{book_id}", headers=headers)
#     if response.status_code == 200:
#         st.success("Book returned successfully!")
#         return response.json()
#     st.error("Failed to return book")
#     return None

# # Streamlit App
# st.title("Library Management System")

# # User Authentication
# st.sidebar.header("Login")
# email = st.sidebar.text_input("Email")
# password = st.sidebar.text_input("Password", type="password")
# if st.sidebar.button("Login"):
#     token = authenticate_user(email, password)
#     if token:
#         st.session_state["token"] = token
#         st.sidebar.success("Logged in successfully!")

# # Main Page
# if "token" in st.session_state:
#     token = st.session_state["token"]
#     st.header("Welcome to the Library Management System")

#     # Tabs
#     tab = st.selectbox("Choose an Action", ["View Books", "Manage Users", "Rent/Return Books", "Create User"])

#     # View Books
#     if tab == "View Books":
#         books = get_books()
#         st.subheader("Books Available")
#         for book in books:
#             st.write(f"**Title:** {book['title']}, **Author:** {book['author']}, **Genre:** {book['genre']}, **Copies:** {book['available_copies']}")

#     # Manage Users (Admin Only)
#     elif tab == "Manage Users":
#         st.subheader("User Management")
#         users = get_users(token)
#         for user in users:
#             st.write(f"**Name:** {user['name']}, **Email:** {user['email']}, **Is Admin:** {user['is_admin']}")

#     # Rent or Return Books
#     elif tab == "Rent/Return Books":
#         st.subheader("Rent or Return a Book")
#         user_id = st.text_input("User ID")
#         book_id = st.text_input("Book ID")
#         action = st.radio("Action", ["Rent", "Return"])
#         if st.button("Submit"):
#             if action == "Rent":
#                 rent_book(user_id, book_id, token)
#             elif action == "Return":
#                 return_book(user_id, book_id, token)

#     # Create User
#     elif tab == "Create User":
#         st.subheader("Create New User")
#         name = st.text_input("Name")
#         new_email = st.text_input("Email")
#         new_password = st.text_input("Password", type="password")
#         is_admin = st.checkbox("Admin User")
#         if st.button("Create"):
#             create_user(name, new_email, new_password, is_admin)

# else:
#     st.info("Please login to access the system.")


# import streamlit as st
# import requests

# # Service URLs
# USER_SERVICE_URL = "http://127.0.0.1:8001"  # Replace with actual User service URL
# BOOK_SERVICE_URL = "http://127.0.0.1:8000"  # Replace with actual Book service URL

# # Helper function for setting headers
# def get_headers():
#     if "auth_token" in st.session_state:
#         return {"Authorization": f"Bearer {st.session_state.auth_token}"}
#     return {}

# # Logout function
# def logout():
#     if "auth_token" in st.session_state:
#         del st.session_state.auth_token
#     st.sidebar.success("Logged out successfully!")
#     st.experimental_rerun()

# # Sidebar Navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["Login", "Books", "Users", "Rentals", "Logout"])

# # Login Page
# if page == "Login":
#     st.title("Login")
#     with st.form("Login Form"):
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             response = requests.post(
#                 f"{USER_SERVICE_URL}/token",
#                 data={"username": email, "password": password},
#             )
#             if response.status_code == 200:
#                 st.session_state.auth_token = response.json()["access_token"]
#                 st.success("Login successful!")
#                 st.experimental_rerun()
#             else:
#                 st.error("Invalid credentials. Please try again.")
                

# # Logout Page
# if page == "Logout":
#     logout()

# # Ensure the user is authenticated before allowing access to other pages
# if "auth_token" in st.session_state:
#     # Books Page
#     if page == "Books":
#         st.title("Books Management")
#         action = st.radio("Action", ["View Books", "Add Book", "Update Book", "Delete Book"])

#         if action == "View Books":
#             response = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=get_headers())
#             if response.status_code == 200:
#                 books = response.json()
#                 for book in books:
#                     st.write(book)
#             else:
#                 st.error("Failed to fetch books. Check authentication or service URL.")

#         elif action == "Add Book":
#             with st.form("Add Book Form"):
#                 title = st.text_input("Title")
#                 author = st.text_input("Author")
#                 genre = st.text_input("Genre")
#                 copies = st.number_input("Available Copies", min_value=0, step=1)
#                 submitted = st.form_submit_button("Add Book")

#                 if submitted:
#                     response = requests.post(
#                         f"{BOOK_SERVICE_URL}/books/",
#                         json={"title": title, "author": author, "genre": genre, "available_copies": copies},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("Book added successfully!")
#                     else:
#                         st.error("Failed to add book.")

#         elif action == "Update Book":
#             book_id = st.text_input("Book ID")
#             with st.form("Update Book Form"):
#                 title = st.text_input("New Title")
#                 author = st.text_input("New Author")
#                 genre = st.text_input("New Genre")
#                 copies = st.number_input("New Available Copies", min_value=0, step=1)
#                 submitted = st.form_submit_button("Update Book")

#                 if submitted:
#                     response = requests.put(
#                         f"{BOOK_SERVICE_URL}/books/{book_id}",
#                         json={"title": title, "author": author, "genre": genre, "available_copies": copies},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("Book updated successfully!")
#                     else:
#                         st.error("Failed to update book.")

#         elif action == "Delete Book":
#             book_id = st.text_input("Book ID")
#             if st.button("Delete Book"):
#                 response = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}", headers=get_headers())
#                 if response.status_code == 200:
#                     st.success("Book deleted successfully!")
#                 else:
#                     st.error("Failed to delete book.")

#     # Users Page
#     elif page == "Users":
#         st.title("User Management")

#         action = st.radio("Action", ["View Users", "Add User", "Update User", "Delete User"])

#         if action == "View Users":
#             response = requests.get(f"{USER_SERVICE_URL}/users/", headers=get_headers())
#             if response.status_code == 200:
#                 users = response.json()
#                 for user in users:
#                     st.write(user)
#             else:
#                 st.error("Failed to fetch users. Check authentication or service URL.")

#         elif action == "Add User":
#             with st.form("Add User Form"):
#                 name = st.text_input("Name")
#                 email = st.text_input("Email")
#                 password = st.text_input("Password", type="password")
#                 is_admin = st.checkbox("Admin?")
#                 submitted = st.form_submit_button("Add User")

#                 if submitted:
#                     response = requests.post(
#                         f"{USER_SERVICE_URL}/users/",
#                         json={"name": name, "email": email, "password": password, "is_admin": is_admin},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("User added successfully!")
#                     else:
#                         st.error("Failed to add user.")

#         elif action == "Update User":
#             user_id = st.text_input("User ID")
#             with st.form("Update User Form"):
#                 name = st.text_input("New Name")
#                 email = st.text_input("New Email")
#                 password = st.text_input("New Password", type="password")
#                 submitted = st.form_submit_button("Update User")

#                 if submitted:
#                     response = requests.put(
#                         f"{USER_SERVICE_URL}/users/{user_id}",
#                         json={"name": name, "email": email, "password": password},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("User updated successfully!")
#                     else:
#                         st.error("Failed to update user.")

#         elif action == "Delete User":
#             user_id = st.text_input("User ID")
#             if st.button("Delete User"):
#                 response = requests.delete(f"{USER_SERVICE_URL}/users/{user_id}", headers=get_headers())
#                 if response.status_code == 204:
#                     st.success("User deleted successfully!")
#                 else:
#                     st.error("Failed to delete user.")

#     # Rentals Page
#     elif page == "Rentals":
#         st.title("Book Rentals")
#         user_id = st.text_input("User ID")

#         action = st.radio("Action", ["Rent Book", "Return Book"])
#         book_id = st.text_input("Book ID")

#         if action == "Rent Book":
#             if st.button("Rent Book"):
#                 response = requests.post(
#                     f"{USER_SERVICE_URL}/users/{user_id}/rent_book/{book_id}",
#                     headers=get_headers(),
#                 )
#                 if response.status_code == 200:
#                     st.success("Book rented successfully!")
#                 else:
#                     st.error(response.json().get("detail", "Failed to rent book."))

#         elif action == "Return Book":
#             if st.button("Return Book"):
#                 response = requests.post(
#                     f"{USER_SERVICE_URL}/users/{user_id}/return_book/{book_id}",
#                     headers=get_headers(),
#                 )
#                 if response.status_code == 200:
#                     st.success("Book returned successfully!")
#                 else:
#                     st.error(response.json().get("detail", "Failed to return book."))
# else:
#     st.warning("You need to login first!")



#final
# import streamlit as st
# import requests

# # Service URLs
# USER_SERVICE_URL = "http://127.0.0.1:8001"  # Replace with actual User service URL
# BOOK_SERVICE_URL = "http://127.0.0.1:8000"  # Replace with actual Book service URL

# # Helper function for setting headers
# def get_headers():
#     if "auth_token" in st.session_state:
#         return {"Authorization": f"Bearer {st.session_state.auth_token}"}
#     return {}

# # Logout function
# def logout():
#     if "auth_token" in st.session_state:
#         del st.session_state.auth_token
#     st.sidebar.success("Logged out successfully!")
#     st.experimental_rerun()

# # Sidebar Navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Go to", ["Login", "Books", "Users", "Rentals", "Logout"])

# # Login Page
# if page == "Login":
#     st.title("Login")
#     with st.form("Login Form"):
#         email = st.text_input("Email")
#         password = st.text_input("Password", type="password")
#         submitted = st.form_submit_button("Login")

#         if submitted:
#             response = requests.post(
#                 f"{USER_SERVICE_URL}/token",
#                 data={"username": email, "password": password},
#             )
#             if response.status_code == 200:
#                 st.session_state.auth_token = response.json()["access_token"]
#                 st.success("Login successful!")
#                 st.experimental_rerun()
#             else:
#                 st.error("Invalid credentials. Please try again.")

# # Logout Page
# if page == "Logout":
#     logout()

# # Users Page (Accessible to All)
# if page == "Users":
#     st.title("User Management")

#     action = st.radio("Action", ["Add User (Accessible to All)", "Authenticated Actions"])

#     if action == "Add User (Accessible to All)":
#         with st.form("Add User Form"):
#             name = st.text_input("Name")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             is_admin = st.checkbox("Admin?")
#             submitted = st.form_submit_button("Add User")

#             if submitted:
#                 response = requests.post(
#                     f"{USER_SERVICE_URL}/users/",
#                     json={"name": name, "email": email, "password": password, "is_admin": is_admin},
#                 )
#                 if response.status_code == 200:
#                     st.success("User added successfully!")
#                 else:
#                     st.error("Failed to add user.")

#     if "auth_token" in st.session_state and action == "Authenticated Actions":
#         authenticated_action = st.radio("Authenticated Action", ["View Users", "Update User", "Delete User"])

#         if authenticated_action == "View Users":
#             response = requests.get(f"{USER_SERVICE_URL}/users/", headers=get_headers())
#             if response.status_code == 200:
#                 users = response.json()
#                 for user in users:
#                     st.write(user)
#             else:
#                 st.error("Failed to fetch users. Check authentication or service URL.")

#         elif authenticated_action == "Update User":
#             user_id = st.text_input("User ID")
#             with st.form("Update User Form"):
#                 name = st.text_input("New Name")
#                 email = st.text_input("New Email")
#                 password = st.text_input("New Password", type="password")
#                 submitted = st.form_submit_button("Update User")

#                 if submitted:
#                     response = requests.put(
#                         f"{USER_SERVICE_URL}/users/{user_id}",
#                         json={"name": name, "email": email, "password": password},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("User updated successfully!")
#                     else:
#                         st.error("Failed to update user.")

#         elif authenticated_action == "Delete User":
#             user_id = st.text_input("User ID")
#             if st.button("Delete User"):
#                 response = requests.delete(f"{USER_SERVICE_URL}/users/{user_id}", headers=get_headers())
#                 if response.status_code == 204:
#                     st.success("User deleted successfully!")
#                 else:
#                     st.error("Failed to delete user.")

# # Ensure the user is authenticated before allowing access to other pages
# if "auth_token" in st.session_state:
#     # Books Page
#     if page == "Books":
#         st.title("Books Management")
#         action = st.radio("Action", ["View Books", "Add Book", "Update Book", "Delete Book"])

#         if action == "View Books":
#             response = requests.get(f"{BOOK_SERVICE_URL}/books/", headers=get_headers())
#             if response.status_code == 200:
#                 books = response.json()
#                 for book in books:
#                     st.write(book)
#             else:
#                 st.error("Failed to fetch books. Check authentication or service URL.")

#         elif action == "Add Book":
#             with st.form("Add Book Form"):
#                 title = st.text_input("Title")
#                 author = st.text_input("Author")
#                 genre = st.text_input("Genre")
#                 copies = st.number_input("Available Copies", min_value=0, step=1)
#                 submitted = st.form_submit_button("Add Book")

#                 if submitted:
#                     response = requests.post(
#                         f"{BOOK_SERVICE_URL}/books/",
#                         json={"title": title, "author": author, "genre": genre, "available_copies": copies},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("Book added successfully!")
#                     else:
#                         st.error("Failed to add book.")

#         elif action == "Update Book":
#             book_id = st.text_input("Book ID")
#             with st.form("Update Book Form"):
#                 title = st.text_input("New Title")
#                 author = st.text_input("New Author")
#                 genre = st.text_input("New Genre")
#                 copies = st.number_input("New Available Copies", min_value=0, step=1)
#                 submitted = st.form_submit_button("Update Book")

#                 if submitted:
#                     response = requests.put(
#                         f"{BOOK_SERVICE_URL}/books/{book_id}",
#                         json={"title": title, "author": author, "genre": genre, "available_copies": copies},
#                         headers=get_headers(),
#                     )
#                     if response.status_code == 200:
#                         st.success("Book updated successfully!")
#                     else:
#                         st.error("Failed to update book.")

#         elif action == "Delete Book":
#             book_id = st.text_input("Book ID")
#             if st.button("Delete Book"):
#                 response = requests.delete(f"{BOOK_SERVICE_URL}/books/{book_id}", headers=get_headers())
#                 if response.status_code == 200:
#                     st.success("Book deleted successfully!")
#                 else:
#                     st.error("Failed to delete book.")

#     # Rentals Page
#     elif page == "Rentals":
#         st.title("Book Rentals")
#         user_id = st.text_input("User ID")

#         action = st.radio("Action", ["Rent Book", "Return Book"])
#         book_id = st.text_input("Book ID")

#         if action == "Rent Book":
#             if st.button("Rent Book"):
#                 response = requests.post(
#                     f"{USER_SERVICE_URL}/users/{user_id}/rent_book/{book_id}",
#                     headers=get_headers(),
#                 )
#                 if response.status_code == 200:
#                     st.success("Book rented successfully!")
#                 else:
#                     st.error(response.json().get("detail", "Failed to rent book."))

#         elif action == "Return Book":
#             if st.button("Return Book"):
#                 response = requests.post(
#                     f"{USER_SERVICE_URL}/users/{user_id}/return_book/{book_id}",
#                     headers=get_headers(),
#                 )
#                 if response.status_code == 200:
#                     st.success("Book returned successfully!")
#                 else:
#                     st.error(response.json().get("detail", "Failed to return book."))
# else:
#     st.warning("You need to login first!")




#final proj
# import streamlit as st
# import requests
# import pandas as pd
# from datetime import datetime
# import time


# import os

# # Constants
# USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
# BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://localhost:8000")
# # Constants
# # USER_SERVICE_URL = "http://localhost:8001"
# # BOOK_SERVICE_URL = "http://localhost:8000"

# # Initialize session state variables
# if 'token' not in st.session_state:
#     st.session_state.token = None
# if 'user_data' not in st.session_state:
#     st.session_state.user_data = None

# def get_headers():
#     if st.session_state.token:
#         return {"Authorization": f"Bearer {st.session_state.token}"}
#     return {}

# def login(email: str, password: str):
#     try:
#         response = requests.post(
#             f"{USER_SERVICE_URL}/token",
#             data={
#                 "username": email,
#                 "password": password,
#             }
#         )
        
#         if response.status_code == 200:
#             token_data = response.json()
#             st.session_state.token = token_data['access_token']
            
#             # Get user data
#             user_response = requests.get(
#                 f"{USER_SERVICE_URL}/users/me",
#                 headers=get_headers()
#             )
            
#             if user_response.status_code == 200:
#                 st.session_state.user_data = user_response.json()
#                 st.success("Login successful!")
#                 st.rerun()
#             else:
#                 st.error(f"Failed to fetch user data: {user_response.text}")
#         else:
#             st.error("Invalid credentials")
#     except Exception as e:
#         st.error(f"Login failed: {str(e)}")

# def register(name: str, email: str, password: str, is_admin: bool = False):
#     try:
#         response = requests.post(
#             f"{USER_SERVICE_URL}/users/",
#             json={
#                 "name": name,
#                 "email": email,
#                 "password": password,
#                 "is_admin": is_admin
#             }
#         )
#         if response.status_code == 200:
#             st.success("Registration successful! Please login.")
#             time.sleep(1)
#             st.rerun()
#         else:
#             st.error(f"Registration failed: {response.json().get('detail', 'Unknown error')}")
#     except Exception as e:
#         st.error(f"Registration failed: {str(e)}")

# def get_all_books():
#     try:
#         response = requests.get(f"{BOOK_SERVICE_URL}/books/")
#         if response.status_code == 200:
#             return response.json()
#         st.error("Failed to fetch books")
#         return []
#     except Exception as e:
#         st.error(f"Failed to fetch books: {str(e)}")
#         return []

# def get_rental_history(user_id: str):
#     try:
#         response = requests.get(
#             f"{USER_SERVICE_URL}/rentals/user/{user_id}",
#             headers=get_headers()
#         )
#         if response.status_code == 200:
#             return response.json()
#         return []
#     except Exception as e:
#         st.error(f"Failed to fetch rental history: {str(e)}")
#         return []

# def get_active_rentals():
#     try:
#         response = requests.get(
#             f"{USER_SERVICE_URL}/rentals/active",
#             headers=get_headers()
#         )
#         if response.status_code == 200:
#             return response.json()
#         return []
#     except Exception as e:
#         st.error(f"Failed to fetch active rentals: {str(e)}")
#         return []

# def add_book(title: str, author: str, genre: str, copies: int):
#     try:
#         response = requests.post(
#             f"{BOOK_SERVICE_URL}/books/",
#             json={
#                 "title": title,
#                 "author": author,
#                 "genre": genre,
#                 "available_copies": copies
#             }
#         )
#         if response.status_code == 200:
#             st.success("Book added successfully!")
#             return True
#         st.error("Failed to add book")
#         return False
#     except Exception as e:
#         st.error(f"Failed to add book: {str(e)}")
#         return False

# def rent_book(book_id: str):
#     try:
#         response = requests.post(
#             f"{USER_SERVICE_URL}/users/{st.session_state.user_data['id']}/rent_book/{book_id}",
#             headers=get_headers()
#         )
#         if response.status_code == 200:
#             st.success("Book rented successfully!")
#             st.session_state.user_data = response.json()['user']
#             return True
#         else:
#             st.error(f"Failed to rent book: {response.json().get('detail', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to rent book: {str(e)}")
#         return False

# def return_book(book_id: str):
#     try:
#         response = requests.post(
#             f"{USER_SERVICE_URL}/users/{st.session_state.user_data['id']}/return_book/{book_id}",
#             headers=get_headers()
#         )
#         if response.status_code == 200:
#             st.success("Book returned successfully!")
#             st.session_state.user_data = response.json()['user']
#             return True
#         else:
#             st.error(f"Failed to return book: {response.json().get('detail', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to return book: {str(e)}")
#         return False

# def show_login_page():
#     st.title("📚 Library Management System")
    
#     tab1, tab2 = st.tabs(["Login", "Register"])
    
#     with tab1:
#         with st.form("login_form"):
#             st.subheader("Login")
#             email = st.text_input("Email")
#             password = st.text_input("Password", type="password")
#             submitted = st.form_submit_button("Login")
#             if submitted:
#                 login(email, password)

#     with tab2:
#         with st.form("register_form"):
#             st.subheader("Register")
#             name = st.text_input("Name")
#             email = st.text_input("Email", key="reg_email")
#             password = st.text_input("Password", type="password", key="reg_pass")
#             is_admin = st.checkbox("Register as Admin")
#             submitted = st.form_submit_button("Register")
#             if submitted:
#                 if not name or not email or not password:
#                     st.error("Please fill in all fields")
#                 else:
#                     register(name, email, password, is_admin)
                    
# def delete_user(user_id: str):
#     try:
#         response = requests.delete(
#             f"{USER_SERVICE_URL}/users/{user_id}",
#             headers=get_headers()
#         )
#         if response.status_code == 204:
#             st.success("User deleted successfully!")
#             if user_id == st.session_state.user_data['id']:
#                 st.session_state.token = None
#                 st.session_state.user_data = None
#             st.rerun()
#         else:
#             st.error(f"Failed to delete user: {response.json().get('detail', 'Unknown error')}")
#     except Exception as e:
#         st.error(f"Failed to delete user: {str(e)}")

# def update_user(user_id: str, name: str = None, email: str = None, password: str = None):
#     try:
#         update_data = {}
#         if name:
#             update_data["name"] = name
#         if email:
#             update_data["email"] = email
#         if password:
#             update_data["password"] = password

#         response = requests.put(
#             f"{USER_SERVICE_URL}/users/{user_id}",
#             headers=get_headers(),
#             json=update_data
#         )
#         if response.status_code == 200:
#             st.success("User updated successfully!")
#             if user_id == st.session_state.user_data['id']:
#                 st.session_state.user_data = response.json()
#             return True
#         else:
#             st.error(f"Failed to update user: {response.json().get('detail', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to update user: {str(e)}")
#         return False

# def update_book(book_id: str, title: str = None, author: str = None, 
#                 genre: str = None, available_copies: int = None):
#     try:
#         update_data = {}
#         if title:
#             update_data["title"] = title
#         if author:
#             update_data["author"] = author
#         if genre:
#             update_data["genre"] = genre
#         if available_copies is not None:
#             update_data["available_copies"] = available_copies

#         response = requests.put(
#             f"{BOOK_SERVICE_URL}/books/{book_id}",
#             json=update_data
#         )
#         if response.status_code == 200:
#             st.success("Book updated successfully!")
#             return True
#         else:
#             st.error(f"Failed to update book: {response.json().get('detail', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to update book: {str(e)}")
#         return False

# def delete_book(book_id: str):
#     try:
#         response = requests.delete(
#             f"{BOOK_SERVICE_URL}/books/{book_id}"
#         )
#         if response.status_code in [200, 204]:
#             st.success("Book deleted successfully!")
#             return True
#         else:
#             st.error(f"Failed to delete book: {response.json().get('detail', 'Unknown error')}")
#             return False
#     except Exception as e:
#         st.error(f"Failed to delete book: {str(e)}")
#         return False


# def show_main_page():
#     st.title("📚 Library Management System")
    
#     # Sidebar
#     with st.sidebar:
#         st.write(f"Welcome, {st.session_state.user_data['name']}!")
#         if st.button("Logout"):
#             st.session_state.token = None
#             st.session_state.user_data = None
#             st.rerun()
#     with st.sidebar:
#             st.markdown("---")
#             st.subheader("Update Profile")
#             with st.form("update_profile_form"):
#                 name = st.text_input("Name", value=st.session_state.user_data['name'])
#                 email = st.text_input("Email", value=st.session_state.user_data['email'])
#                 password = st.text_input("New Password", type="password", 
#                                     help="Leave blank to keep current password")
#                 if st.form_submit_button("Update Profile"):
#                     update_data = {}
#                     if name != st.session_state.user_data['name']:
#                         update_data['name'] = name
#                     if email != st.session_state.user_data['email']:
#                         update_data['email'] = email
#                     if password:
#                         update_data['password'] = password
#                     if update_data:
#                         if update_user(st.session_state.user_data['id'], **update_data):
#                             st.rerun()

#     # Main content
#     if st.session_state.user_data.get('is_admin', False):
#         tab1, tab2, tab3, tab4, tab5 = st.tabs([
#             "Available Books", 
#             "My Rentals", 
#             "Rental History", 
#             "Active Rentals",
#             "Admin Panel"
#         ])
#     else:
#         tab1, tab2, tab3 = st.tabs([
#             "Available Books", 
#             "My Rentals", 
#             "Rental History"
#         ])

#     with tab1:
#         st.header("Available Books")
#         books = get_all_books()
#         if books:
#             df = pd.DataFrame(books)
#             df = df[['id', 'title', 'author', 'genre', 'available_copies']]
#             st.dataframe(df, hide_index=True)
            
#             # Rent book section
#             st.subheader("Rent a Book")
#             available_books = [b for b in books if b['available_copies'] > 0]
#             if available_books:
#                 book_choice = st.selectbox(
#                     "Select a book to rent",
#                     options=available_books,
#                     format_func=lambda x: f"{x['title']} by {x['author']} ({x['available_copies']} copies available)"
#                 )
#                 if st.button("Rent Book"):
#                     if rent_book(book_choice['id']):
#                         st.rerun()
#             else:
#                 st.info("No books available for rent at the moment.")

#     with tab2:
#         st.header("My Rented Books")
#         if st.session_state.user_data.get('rented_books'):
#             rented_df = pd.DataFrame(st.session_state.user_data['rented_books'])
#             st.dataframe(rented_df, hide_index=True)
            
#             book_to_return = st.selectbox(
#                 "Select a book to return",
#                 options=st.session_state.user_data['rented_books'],
#                 format_func=lambda x: f"{x['title']} by {x['author']}"
#             )
#             if st.button("Return Book"):
#                 if return_book(book_to_return['book_id']):
#                     st.rerun()
#         else:
#             st.info("You haven't rented any books yet.")

#     with tab3:
#         st.header("Rental History")
#         rentals = get_rental_history(st.session_state.user_data['id'])
#         if rentals:
#             df = pd.DataFrame(rentals)
#             df['rental_date'] = pd.to_datetime(df['rental_date']).dt.strftime('%Y-%m-%d %H:%M')
#             df['return_date'] = pd.to_datetime(df['return_date']).dt.strftime('%Y-%m-%d %H:%M')
#             st.dataframe(
#                 df[['book_title', 'book_author', 'rental_date', 'return_date']],
#                 hide_index=True
#             )
#         else:
#             st.info("No rental history found.")

#     if st.session_state.user_data.get('is_admin', False):
#         with tab4:
#             st.header("Active Rentals")
#             active_rentals = get_active_rentals()
#             if active_rentals:
#                 df = pd.DataFrame(active_rentals)
#                 df['rental_date'] = pd.to_datetime(df['rental_date']).dt.strftime('%Y-%m-%d %H:%M')
#                 st.dataframe(
#                     df[['book_title', 'book_author', 'rental_date']],
#                     hide_index=True
#                 )
#             else:
#                 st.info("No active rentals found.")

        
#         if st.session_state.user_data.get('is_admin', False):
#             with tab5:
#                 st.header("Admin Panel")
                
#                 admin_tabs = st.tabs(["Add Book", "Manage Books", "Manage Users"])
                
#                 with admin_tabs[0]:
#                     with st.form("add_book_form"):
#                         st.subheader("Add New Book")
#                         title = st.text_input("Title")
#                         author = st.text_input("Author")
#                         genre = st.text_input("Genre")
#                         copies = st.number_input("Number of Copies", min_value=1, value=1)
#                         submitted = st.form_submit_button("Add Book")
#                         if submitted:
#                             if not title or not author or not genre:
#                                 st.error("Please fill in all fields")
#                             elif add_book(title, author, genre, copies):
#                                 st.rerun()
                
#                 with admin_tabs[1]:
#                     st.subheader("Manage Books")
#                     books = get_all_books()
#                     if books:
#                         book_to_manage = st.selectbox(
#                             "Select a book to manage",
#                             options=books,
#                             format_func=lambda x: f"{x['title']} by {x['author']}"
#                         )
                        
#                         col1, col2 = st.columns(2)
                        
#                         with col1:
#                             st.subheader("Update Book")
#                             with st.form("update_book_form"):
#                                 new_title = st.text_input("New Title", value=book_to_manage['title'])
#                                 new_author = st.text_input("New Author", value=book_to_manage['author'])
#                                 new_genre = st.text_input("New Genre", value=book_to_manage['genre'])
#                                 new_copies = st.number_input("New Copies", 
#                                                         value=book_to_manage['available_copies'],
#                                                         min_value=0)
#                                 if st.form_submit_button("Update Book"):
#                                     if update_book(book_to_manage['id'], new_title, new_author, 
#                                                 new_genre, new_copies):
#                                         st.rerun()
                        
#                         with col2:
#                             st.subheader("Delete Book")
#                             if st.button("Delete Book", type="primary"):
#                                 if delete_book(book_to_manage['id']):
#                                     st.rerun()
                
#                 with admin_tabs[2]:
#                     st.subheader("Manage Users")
#                     try:
#                         response = requests.get(f"{USER_SERVICE_URL}/users/", headers=get_headers())
#                         if response.status_code == 200:
#                             users = response.json()
#                             if users:
#                                 user_to_manage = st.selectbox(
#                                     "Select a user to manage",
#                                     options=users,
#                                     format_func=lambda x: f"{x['name']} ({x['email']})"
#                                 )
                                
#                                 col1, col2 = st.columns(2)
                                
#                                 with col1:
#                                     st.subheader("Update User")
#                                     with st.form("update_user_form"):
#                                         new_name = st.text_input("New Name", value=user_to_manage['name'])
#                                         new_email = st.text_input("New Email", value=user_to_manage['email'])
#                                         new_password = st.text_input("New Password", type="password", 
#                                                                 help="Leave blank to keep current password")
#                                         if st.form_submit_button("Update User"):
#                                             update_data = {}
#                                             if new_name != user_to_manage['name']:
#                                                 update_data['name'] = new_name
#                                             if new_email != user_to_manage['email']:
#                                                 update_data['email'] = new_email
#                                             if new_password:
#                                                 update_data['password'] = new_password
#                                             if update_data:
#                                                 if update_user(user_to_manage['id'], **update_data):
#                                                     st.rerun()
                                
#                                 with col2:
#                                     st.subheader("Delete User")
#                                     if st.button("Delete User", type="primary"):
#                                         if delete_user(user_to_manage['id']):
#                                             st.rerun()
                                    
#                     except Exception as e:
#                         st.error(f"Failed to fetch users: {str(e)}")

#         # Add a profile update section for regular users in the sidebar
#         with st.sidebar:
#             st.markdown("---")
#             st.subheader("Update Profile")
#             with st.form("update_profile_form"):
#                 name = st.text_input("Name", value=st.session_state.user_data['name'])
#                 email = st.text_input("Email", value=st.session_state.user_data['email'])
#                 password = st.text_input("New Password", type="password", 
#                                     help="Leave blank to keep current password")
#                 if st.form_submit_button("Update Profile"):
#                     update_data = {}
#                     if name != st.session_state.user_data['name']:
#                         update_data['name'] = name
#                     if email != st.session_state.user_data['email']:
#                         update_data['email'] = email
#                     if password:
#                         update_data['password'] = password
#                     if update_data:
#                         if update_user(st.session_state.user_data['id'], **update_data):
#                             st.rerun()

# def main():
#     st.set_page_config(
#         page_title="Library Management System",
#         page_icon="📚",
#         layout="wide"
#     )
    
#     if not st.session_state.token or not st.session_state.user_data:
#         show_login_page()
#     else:
#         show_main_page()

# if __name__ == "__main__":
#     main()


import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import os

# Configuration
st.set_page_config(
    page_title="📚 Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
    }
    .st-emotion-cache-1v0mbdj {
        width: 100%;
    }
    .book-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        background-color: #ffffff;
        color: #1f1f1f;  /* Dark text color for contrast */
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);  /* Subtle shadow for depth */
    }
    .book-card h3 {
        color: #0066cc;  /* Blue color for titles */
        margin-bottom: 0.5rem;
    }
    .book-card p {
        color: #333333;  /* Dark gray for text */
        margin-bottom: 0.25rem;
    }
       .rental-history, .active-rental {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        background-color: #ffffff;
        color: #1f1f1f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .rental-history h4, .active-rental h4 {
        color: #0066cc;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    .rental-history p, .active-rental p {
        color: #333333;
        margin-bottom: 0.25rem;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-returned {
        color: #6c757d;
    }
    </style>
    """, unsafe_allow_html=True)

# Constants
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8001")
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://localhost:8000")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def get_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def login(email: str, password: str):
    with st.spinner('Logging in...'):
        try:
            response = requests.post(
                f"{USER_SERVICE_URL}/token",
                data={"username": email, "password": password}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                st.session_state.token = token_data['access_token']
                
                user_response = requests.get(
                    f"{USER_SERVICE_URL}/users/me",
                    headers=get_headers()
                )
                
                if user_response.status_code == 200:
                    st.session_state.user_data = user_response.json()
                    st.success('Welcome back! 👋')
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Failed to fetch user data: {user_response.text}")
            else:
                st.error("❌ Invalid credentials")
        except Exception as e:
            st.error(f"❌ Login failed: {str(e)}")

def register(name: str, email: str, password: str, is_admin: bool = False):
    with st.spinner('Creating your account...'):
        try:
            response = requests.post(
                f"{USER_SERVICE_URL}/users/",
                json={
                    "name": name,
                    "email": email,
                    "password": password,
                    "is_admin": is_admin
                }
            )
            if response.status_code == 200:
                st.success("✅ Registration successful! Please login.")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Registration failed: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Registration failed: {str(e)}")

def logout():
    st.session_state.token = None
    st.session_state.user_data = None
    st.rerun()

def get_all_books():
    try:
        response = requests.get(f"{BOOK_SERVICE_URL}/books/")
        if response.status_code == 200:
            return response.json()
        st.error("Failed to fetch books")
        return []
    except Exception as e:
        st.error(f"Failed to fetch books: {str(e)}")
        return []

def get_rental_history(user_id: str):
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/rentals/user/{user_id}",
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Failed to fetch rental history: {str(e)}")
        return []

def get_active_rentals():
    try:
        response = requests.get(
            f"{USER_SERVICE_URL}/rentals/active",
            headers=get_headers()
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"Failed to fetch active rentals: {str(e)}")
        return []

def add_book(title: str, author: str, genre: str, copies: int):
    try:
        response = requests.post(
            f"{BOOK_SERVICE_URL}/books/",
            json={
                "title": title,
                "author": author,
                "genre": genre,
                "available_copies": copies
            }
        )
        if response.status_code == 200:
            st.success("✅ Book added successfully!")
            return True
        st.error("Failed to add book")
        return False
    except Exception as e:
        st.error(f"Failed to add book: {str(e)}")
        return False

def rent_book(book_id: str):
    with st.spinner('Processing rental...'):
        try:
            response = requests.post(
                f"{USER_SERVICE_URL}/users/{st.session_state.user_data['id']}/rent_book/{book_id}",
                headers=get_headers()
            )
            if response.status_code == 200:
                st.success("✅ Book rented successfully!")
                st.session_state.user_data = response.json()['user']
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Failed to rent book: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Failed to rent book: {str(e)}")

def return_book(book_id: str):
    with st.spinner('Processing return...'):
        try:
            response = requests.post(
                f"{USER_SERVICE_URL}/users/{st.session_state.user_data['id']}/return_book/{book_id}",
                headers=get_headers()
            )
            if response.status_code == 200:
                st.success("✅ Book returned successfully!")
                st.session_state.user_data = response.json()['user']
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ Failed to return book: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Failed to return book: {str(e)}")

def update_book(book_id: str, title: str = None, author: str = None, 
                genre: str = None, available_copies: int = None):
    try:
        update_data = {}
        if title:
            update_data["title"] = title
        if author:
            update_data["author"] = author
        if genre:
            update_data["genre"] = genre
        if available_copies is not None:
            update_data["available_copies"] = available_copies

        response = requests.put(
            f"{BOOK_SERVICE_URL}/books/{book_id}",
            json=update_data
        )
        if response.status_code == 200:
            st.success("✅ Book updated successfully!")
            return True
        else:
            st.error(f"❌ Failed to update book: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"❌ Failed to update book: {str(e)}")
        return False

def delete_book(book_id: str):
    try:
        response = requests.delete(
            f"{BOOK_SERVICE_URL}/books/{book_id}"
        )
        if response.status_code in [200, 204]:
            st.success("✅ Book deleted successfully!")
            return True
        else:
            st.error(f"❌ Failed to delete book: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"❌ Failed to delete book: {str(e)}")
        return False

def update_user(user_id: str, name: str = None, email: str = None, password: str = None):
    try:
        update_data = {}
        if name:
            update_data["name"] = name
        if email:
            update_data["email"] = email
        if password:
            update_data["password"] = password

        response = requests.put(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers=get_headers(),
            json=update_data
        )
        if response.status_code == 200:
            st.success("✅ User updated successfully!")
            if user_id == st.session_state.user_data['id']:
                st.session_state.user_data = response.json()
            return True
        else:
            st.error(f"❌ Failed to update user: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"❌ Failed to update user: {str(e)}")
        return False

def delete_user(user_id: str):
    try:
        response = requests.delete(
            f"{USER_SERVICE_URL}/users/{user_id}",
            headers=get_headers()
        )
        if response.status_code == 204:
            st.success("✅ User deleted successfully!")
            if user_id == st.session_state.user_data['id']:
                logout()
            return True
        else:
            st.error(f"❌ Failed to delete user: {response.json().get('detail', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"❌ Failed to delete user: {str(e)}")
        return False

def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title('📚 Library Management System')
        st.markdown('---')
        
        tab1, tab2 = st.tabs(['🔑 Login', '📝 Register'])
        
        with tab1:
            with st.form('login_form', clear_on_submit=True):
                st.subheader('Welcome Back!')
                email = st.text_input('📧 Email')
                password = st.text_input('🔒 Password', type='password')
                submit = st.form_submit_button('Login', use_container_width=True)
                if submit:
                    login(email, password)

        with tab2:
            with st.form('register_form', clear_on_submit=True):
                st.subheader('Create New Account')
                name = st.text_input('👤 Full Name')
                email = st.text_input('📧 Email', key='reg_email')
                password = st.text_input('🔒 Password', type='password', key='reg_pass')
                is_admin = st.checkbox('🔰 Register as Admin')
                submit = st.form_submit_button('Register', use_container_width=True)
                if submit:
                    if not all([name, email, password]):
                        st.error('❌ Please fill in all fields')
                    else:
                        register(name, email, password, is_admin)

def show_available_books():
    st.header('📖 Available Books')
    books = get_all_books()
    
    if not books:
        st.info('📚 No books available at the moment.')
        return
    
    cols = st.columns(3)
    for idx, book in enumerate(books):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <h3>{book['title']}</h3>
                    <p style="color: #333333;"><strong>Author:</strong> {book['author']}</p>
                    <p style="color: #333333;"><strong>Genre:</strong> {book['genre']}</p>
                    <p style="color: #333333;"><strong>Available:</strong> {book['available_copies']} copies</p>
                </div>
                """, unsafe_allow_html=True)
                
                if book['available_copies'] > 0:
                    if st.button('📚 Rent', key=f"rent_{book['id']}", 
                               use_container_width=True):
                        rent_book(book['id'])

def show_my_rentals():
    st.header('📚 My Rented Books')
    
    if not st.session_state.user_data.get('rented_books'):
        st.info('📚 You haven\'t rented any books yet.')
        return
    
    cols = st.columns(2)
    for idx, book in enumerate(st.session_state.user_data['rented_books']):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button('📤 Return', key=f"return_{book['book_id']}", 
                           use_container_width=True):
                    return_book(book['book_id'])

def show_rental_history():
    st.header('📋 Rental History')
    rentals = get_rental_history(st.session_state.user_data['id'])
    
    if not rentals:
        st.info('📚 No rental history found.')
        return
    
    for rental in rentals:
        return_status = "Not returned" if not rental['return_date'] else pd.to_datetime(rental['return_date']).strftime('%Y-%m-%d %H:%M')
        status_class = "status-active" if not rental['return_date'] else "status-returned"
        
        st.markdown(f"""
        <div class="rental-history">
            <h4>{rental['book_title']}</h4>
            <p><strong>Author:</strong> {rental['book_author']}</p>
            <p><strong>Rented:</strong> {pd.to_datetime(rental['rental_date']).strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong> Return Status:</strong> <span class="{status_class}">{return_status}</span></p>
        </div>
        """, unsafe_allow_html=True)

def show_active_rentals():
    st.header('👥 Active Rentals')
    rentals = get_active_rentals()
    
    if not rentals:
        st.info('📚 No active rentals found.')
        return
    
    for rental in rentals:
        rental_duration = (datetime.utcnow() - pd.to_datetime(rental['rental_date'])).days
        
        st.markdown(f"""
        <div class="active-rental">
            <h4>{rental['book_title']}</h4>
            <p><strong>Author:</strong> {rental['book_author']}</p>
            <p><strong>User ID:</strong> {rental['user_id']}</p>
            <p><strong>Rented:</strong> {pd.to_datetime(rental['rental_date']).strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Duration:</strong> <span class="status-active">{rental_duration} days</span></p>
        </div>
        """, unsafe_allow_html=True)

def show_admin_panel():
    st.header('⚙️ Admin Panel')
    
    admin_tabs = st.tabs(["📚 Add Book", "📖 Manage Books", "👥 Manage Users"])
    
    # Add Book Tab
    with admin_tabs[0]:
        with st.form("add_book_form"):
            st.subheader("📚 Add New Book")
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("📕 Title")
                author = st.text_input("✍️ Author")
            with col2:
                genre = st.text_input("📑 Genre")
                copies = st.number_input("📚 Number of Copies", min_value=1, value=1)
            
            submitted = st.form_submit_button("Add Book", use_container_width=True)
            if submitted:
                if not all([title, author, genre]):
                    st.error("❌ Please fill in all fields")
                elif add_book(title, author, genre, copies):
                    st.rerun()
    
    # Manage Books Tab
    with admin_tabs[1]:
        st.subheader("📖 Manage Books")
        books = get_all_books()
        if books:
            book_to_manage = st.selectbox(
                "Select a book to manage",
                options=books,
                format_func=lambda x: f"{x['title']} by {x['author']}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📝 Update Book")
                with st.form("update_book_form"):
                    new_title = st.text_input("New Title", value=book_to_manage['title'])
                    new_author = st.text_input("New Author", value=book_to_manage['author'])
                    new_genre = st.text_input("New Genre", value=book_to_manage['genre'])
                    new_copies = st.number_input("Available Copies", 
                                               value=book_to_manage['available_copies'],
                                               min_value=0)
                    if st.form_submit_button("Update Book", use_container_width=True):
                        if update_book(book_to_manage['id'], new_title, new_author, 
                                    new_genre, new_copies):
                            st.rerun()
            
            with col2:
                st.subheader("🗑️ Delete Book")
                with st.form("delete_book_form"):
                    st.warning("This action cannot be undone!")
                    if st.form_submit_button("Delete Book", use_container_width=True):
                        if delete_book(book_to_manage['id']):
                            st.rerun()
    
    # Manage Users Tab
    with admin_tabs[2]:
        st.subheader("👥 Manage Users")
        try:
            response = requests.get(f"{USER_SERVICE_URL}/users/", headers=get_headers())
            if response.status_code == 200:
                users = response.json()
                if users:
                    user_to_manage = st.selectbox(
                        "Select a user to manage",
                        options=users,
                        format_func=lambda x: f"{x['name']} ({x['email']})"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📝 Update User")
                        with st.form("update_user_form"):
                            new_name = st.text_input("New Name", value=user_to_manage['name'])
                            new_email = st.text_input("New Email", value=user_to_manage['email'])
                            new_password = st.text_input("New Password", type="password", 
                                                    help="Leave blank to keep current password")
                            if st.form_submit_button("Update User", use_container_width=True):
                                update_data = {}
                                if new_name != user_to_manage['name']:
                                    update_data['name'] = new_name
                                if new_email != user_to_manage['email']:
                                    update_data['email'] = new_email
                                if new_password:
                                    update_data['password'] = new_password
                                if update_data:
                                    if update_user(user_to_manage['id'], **update_data):
                                        st.rerun()
                    
                    with col2:
                        st.subheader("🗑️ Delete User")
                        with st.form("delete_user_form"):
                            st.warning("This action cannot be undone!")
                            if st.form_submit_button("Delete User", use_container_width=True):
                                if delete_user(user_to_manage['id']):
                                    st.rerun()
                else:
                    st.info("No users found.")
        except Exception as e:
            st.error(f"Failed to fetch users: {str(e)}")

def show_main_page():
    # Sidebar with user profile
    with st.sidebar:
        st.title('👤 User Profile')
        st.markdown(f"""
        ### Welcome, {st.session_state.user_data['name']}!
        #### Role: {'👨‍💼 Admin' if st.session_state.user_data.get('is_admin') else '👤 User'}
        """)
        
        st.markdown('---')
        
        # Profile Update Section
        with st.expander('✏️ Update Profile', expanded=False):
            with st.form('profile_update'):
                new_name = st.text_input('Name', value=st.session_state.user_data['name'])
                new_email = st.text_input('Email', value=st.session_state.user_data['email'])
                new_password = st.text_input('New Password', type='password', 
                                           help='Leave blank to keep current password')
                submit = st.form_submit_button('Update', use_container_width=True)
                if submit:
                    update_data = {}
                    if new_name != st.session_state.user_data['name']:
                        update_data['name'] = new_name
                    if new_email != st.session_state.user_data['email']:
                        update_data['email'] = new_email
                    if new_password:
                        update_data['password'] = new_password
                    if update_data:
                        if update_user(st.session_state.user_data['id'], **update_data):
                            st.rerun()
        
        st.button('🚪 Logout', on_click=logout, use_container_width=True)

    # Main content
    st.title('📚 Library Management System')
    
    # Tabs
    if st.session_state.user_data.get('is_admin'):
        tabs = st.tabs([
            "📖 Available Books", 
            "📚 My Rentals", 
            "📋 Rental History",
            "👥 Active Rentals",
            "⚙️ Admin Panel"
        ])
    else:
        tabs = st.tabs([
            "📖 Available Books", 
            "📚 My Rentals", 
            "📋 Rental History"
        ])

    # Available Books Tab
    with tabs[0]:
        show_available_books()
    
    # My Rentals Tab
    with tabs[1]:
        show_my_rentals()
    
    # Rental History Tab
    with tabs[2]:
        show_rental_history()
    
    # Admin Tabs
    if st.session_state.user_data.get('is_admin'):
        with tabs[3]:
            show_active_rentals()
        with tabs[4]:
            show_admin_panel()

def main():
    if not st.session_state.token or not st.session_state.user_data:
        show_login_page()
    else:
        show_main_page()

if __name__ == "__main__":
    main()