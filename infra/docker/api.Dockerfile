FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY apps/api /app/apps/api
COPY packages /app/packages

WORKDIR /app/apps/api
RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
