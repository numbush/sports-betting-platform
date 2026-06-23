FROM python:3.11-slim

WORKDIR /app

# Install deps in a separate layer — rebuilds skip this step when only app code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

# Uvicorn serves the FastAPI app; K8s probes hit /health on this port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0" , "--port", "8000"]
