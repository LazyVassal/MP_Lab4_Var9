FROM python:3.11-slim
WORKDIR /app
COPY . /app/backend
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pydantic
EXPOSE 8010
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8010"]