# Supabase Microservice CRUD Project

This workspace contains:

- `frontend/` – React + Vite application with login/register UI and CRUD form
- `backend/auth-service/` – Flask microservice for register/login using JWT and Supabase-backed user storage
- `backend/crud-service/` – Flask microservice for CRUD operations protected by JWT and Supabase-backed item storage
- `database/` – SQL schema definitions for the Supabase tables used by the services

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Run auth service

```bash
cd backend/auth-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Run CRUD service

```bash
cd backend/crud-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

## Supabase setup

1. Open the SQL editor in your Supabase project.
2. Run the statements from `database/schemas.sql`.
3. Fill in the real `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` values in each service `.env` file.

## Notes

- The frontend is set up to call `http://localhost:5001` and `http://localhost:5002`.
- The backend is now designed to use Supabase persistence instead of in-memory arrays.
