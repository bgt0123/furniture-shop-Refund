FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY pyproject.toml ./

EXPOSE 8001

CMD ["uvicorn", "src.presentation.main:app", "--host", "0.0.0.0", "--port", "8001"]