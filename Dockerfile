FROM python:3.10-slim

WORKDIR /app

# Install via pyproject (PEP 621)
COPY pyproject.toml .
# Only copy application code (avoid bringing extra files into image)
COPY src/ ./src
RUN pip install --no-cache-dir .

EXPOSE 30031

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "30031"]

