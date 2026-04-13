# ROA — Backend

Minimal, practical README for the ROA backend service.

## Project overview
ROA is the backend service for the ROA application. This repository contains the API, business logic, and data access layers. The README below provides setup, configuration, development, and deployment instructions.

## Features
- RESTful JSON API
- Environment-driven configuration
- Migrations and seeding (if a relational DB is used)
- Docker support
- Tests and linting

## Environment variables
Create a `.env` in the backend folder. Example variables:
```
PORT=4000
NODE_ENV=development
DATABASE_URL=postgres://user:pass@localhost:5432/roa
JWT_SECRET=change-me
LOG_LEVEL=info
```
Adjust names/types to match this project's config.



## Stack
- Django 4.2
- Django REST Framework
- SimpleJWT (access + refresh tokens, blacklisting)
- drf-yasg (Swagger UI + ReDoc)
- Custom User model (email auth, phone, address, dashboard)

## Quickstart

```bash
# 1. Create and activate virtualenv
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy and fill in env vars
cp .env.example .env

# 4. Run migrations
python manage.py makemigrations accounts
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Run dev server
python manage.py runserver
```

## API endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | `/api/auth/register/` | Public | Register new user |
| POST | `/api/auth/login/` | Public | Login, get tokens |
| POST | `/api/auth/token/refresh/` | Public | Refresh access token |
| POST | `/api/auth/logout/` | Bearer | Blacklist refresh token |
| POST | `/api/auth/change-password/` | Bearer | Change password |
| GET/PATCH | `/api/auth/profile/` | Bearer | View / update profile |
| GET | `/api/auth/dashboard/` | Bearer | Dashboard summary |

## Docs

| URL | Description |
|-----|-------------|
| `/swagger/` | Swagger UI |
| `/redoc/` | ReDoc UI |
| `/swagger.json` | OpenAPI JSON schema |

## JWT usage

1. Login via `POST /api/auth/login/`
2. Use the returned `access` token in headers: `Authorization: Bearer <token>`
3. Access tokens expire in **60 minutes**; refresh tokens in **7 days**
4. Refresh tokens rotate on each use and are blacklisted on logout

## User model fields

**Auth:** `email` (username), `password`  
**Profile:** `first_name`, `last_name`, `avatar`, `bio`, `date_of_birth`  
**Contact:** `phone_number`  
**Address:** `address_line1`, `address_line2`, `city`, `state`, `postal_code`, `country`  
**Dashboard:** `notification_preference`, `is_email_verified`, `profile_completion`, `last_activity`