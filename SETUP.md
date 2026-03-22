# 🚀 SmartTransit: Project Setup Guide

Welcome to **SmartTransit**! Follow these instructions to set up the development environment on your local machine.

## 1. Prerequisites
- **Python 3.10+** (Ensure it's added to your PATH)
- **PostgreSQL** (Installed and running)
- **Git** (For cloning and version control)

## 2. Database Setup
1. Open your PostgreSQL client (pgAdmin, DBeaver, or psql).
2. Create a database named `smarttransit_db`:
   ```sql
   CREATE DATABASE smarttransit_db;
   ```
3. The application will handle table creation automatically when it first runs.

## 3. Environment Variables
1. Navigate to the `backend/` directory.
2. Copy `.env.example` to a new file named `.env`:
   ```powershell
   cp .env.example .env
   ```
3. Edit the `.env` file with your local credentials:
   - **DATABASE_URL**: Replace `YOUR_PASSWORD` with your PostgreSQL password.
   - **JWT_SECRET_KEY & SECRET_KEY**: Generate random 24-character hex strings:
     ```powershell
     python -c "import secrets; print(secrets.token_hex(24))"
     ```
   - **UPLOAD_FOLDER**: Keep as `uploads`.

## 4. Installation
From the project root, run:
1. **Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **AI & Vision Dependencies (Windows)**:
   ```powershell
   pip install dlib-bin
   pip install face-recognition-models Click numpy Pillow
   pip install face_recognition --no-deps
   pip install opencv-python
   ```
3. **Project Dependencies**:
   ```powershell
   pip install -r backend/requirements.txt
   ```

## 5. Running the Application
```powershell
python backend/app.py
```
- The server will start at `http://127.0.0.1:5000`.
- On first run, a default admin is created:
  - **Email**: `admin@smarttransit.com`
  - **Password**: `admin123`

## 6. Accessing Dashboards
- **Admin**: `http://127.0.0.1:5000/web/admin/dashboard.html`
- **User**: `http://127.0.0.1:5000/` (Home)
- **Police**: `http://127.0.0.1:5000/web/police/dashboard.html`

---
*Note: If `dlib` installation fails, you may need "Desktop development with C++" from the Visual Studio Installer.*
