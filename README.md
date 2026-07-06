# Placement Journal — MVP

A social work placement record system. MVP stage: login + Placement Log + Reflection Note + Dashboard.
Data structures for Case Note / Review-Feedback / Supervisor roles are reserved but not yet exposed via API or UI.

## Directory Structure

```
placement-tracker/
├── backend/       FastAPI + PostgreSQL
└── frontend/      React + Vite + Tailwind
```

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # adjust JWT_SECRET etc. as needed
docker compose up -d               # start a local PostgreSQL (skip this if you already have a production database, and update DATABASE_URL in .env instead)

uvicorn app.main:app --reload --port 8000
```

Tables are created automatically on first startup. Since registration is not open to the public, use the script below to create the first account:

```bash
python -m app.seed --username alice --password "a-strong-password" --full-name "Alice Chen" --role student
```

If a user forgets their password, reset it with:

```bash
python -m app.reset_password --username alice --password "a-new-strong-password"
```

Visit http://localhost:8000/docs to see the auto-generated API documentation.

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env               # make sure VITE_API_BASE points to your backend address
npm run dev
```

Visit http://localhost:5173 and log in with the account you just created.

## Deploying to Your Own Server (Key Points)

1. Backend: run with `gunicorn -k uvicorn.workers.UvicornWorker app.main:app` or `uvicorn` directly, kept alive via `systemd`; make sure to replace `JWT_SECRET` in `.env` with a random string — don't use the example value.
2. Frontend: `npm run build` produces static files (`dist/`) to be served directly by Nginx.
3. Have Nginx reverse-proxy `/api/` to the backend port, and serve static files from the frontend `dist/`; remember to relax `client_max_body_size` for the upload endpoint (the default 1MB is too small — set it a bit larger than `MAX_UPLOAD_SIZE_MB`, e.g. 20m).
4. Attachments are currently stored on local disk (`UPLOAD_DIR`) — make sure to include this directory in your backup scope, and schedule regular `pg_dump` database backups.
5. CORS: update `CORS_ORIGINS` in `.env` to your production domain — don't leave localhost in there.

## Reserved Extension Points (Not Enabled in MVP)

- `case_notes` / `case_note_links` tables: data structures for the Case Note feature, with fields based on common social work record elements (presenting issue / intervention / plan / risk assessment / case closure summary). A router and frontend pages can be added directly later without changing the schema.
- `feedback` table: supervisor review feedback; the `is_read` field is used for Dashboard todo reminders.
- `supervisor_interns` table: binding relationship between supervisors and interns — currently an empty table.
- `status` and `reviewer_id` fields on `placement_logs` / `reflection_notes`: currently always `draft`; can be used directly once the review feature is added.
- Backend authorization currently only enforces "users can edit their own records" — the cross-user viewing logic for supervisors needs to be implemented properly (in the backend, not just hidden in the frontend) when the supervisor feature is added.


## TODO
new features:
