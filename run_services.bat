@echo off

start cmd /k "cd book_service\app && uvicorn main:app --host 0.0.0.0 --port 8000"

start cmd /k "cd user_service\app && uvicorn main:app --host 0.0.0.0 --port 8001"

cd frontend
venv\Scripts\activate
streamlit run library_frontend.py