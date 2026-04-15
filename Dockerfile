# syntax=docker/dockerfile:1

FROM node:20-alpine AS frontend-build
WORKDIR /work/frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --loglevel=error

COPY frontend/ .
RUN npm run build


FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt backend/constraints.txt ./backend/
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r backend/requirements.txt -c backend/constraints.txt

COPY backend/ ./backend/
COPY --from=frontend-build /work/frontend/dist ./backend/app/static/dist

EXPOSE 8000

CMD ["sh", "-c", "alembic -c backend/alembic.ini upgrade head && uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000"]

