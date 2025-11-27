# QR-Code-Attendance-system-prototype  
QR Attendance System – FastAPI Backend & Web Dashboard

This project is a complete QR-based attendance management system.
It includes a FastAPI backend, HTML/Jinja2 dashboard, SQLite database, and QR token generator.
The system allows students to scan a daily QR code and mark attendance securely.

- Features

FastAPI backend

QR token generator

Attendance marking API

Admin dashboard (HTML + Jinja2)

SQLite database

Token expiration support

Fully responsive UI

Works with mobile scanner app

Ready for local or cloud deployment

- Project Structure
backend/
│ app.py
│ database.py
│ requirements.txt
│ README.md
│ attendance.db (auto-created)
│
├── templates/
│     index.html
│     dashboard.html
│
└── static/
      style.css
      scripts.js

- Requirements

Python 3.10+

pip

Any OS (Windows, Mac, Linux)

- Installation

Open a terminal inside the project folder and run:

pip install -r requirements.txt


This installs:

fastapi

uvicorn

jinja2

pillow

qrcode

python-multipart

SQLite requires no installation (built-in).

- Running the Server

Start the development server:

uvicorn app:app --reload


API: http://127.0.0.1:8000

Dashboard: http://127.0.0.1:8000/dashboard

QR Generator: http://127.0.0.1:8000/

- Deployment Guide

You may deploy the backend to:

Render

Railway

Replit

Heroku (legacy)

Any VPS or cloud provider

Common Render settings:

Build command:
pip install -r requirements.txt

Start command:
uvicorn app:app --host 0.0.0.0 --port 10000

Replace the API base URL in your mobile app after deployment.

📡 API Endpoints
POST /scan

Marks attendance when the scanner app submits:

student_id: string  
token: string

GET /

QR Code generator UI.

GET /dashboard

Admin attendance viewer.

- Database

Attendance is stored in attendance.db under:

students

attendance

tokens

You may reset the database by deleting the file; it autogenerates on next run.

- License

Free to modify and use for personal or academic work.
Redistribution of the code as a commercial product requires permission.
