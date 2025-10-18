FROM python:3.10-slim

# Basic deps
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Copy requirements and install as non-root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy config (explicit) and app
COPY config.json ./
COPY . .
RUN chown -R appuser:appuser /home/appuser/app

USER appuser

EXPOSE 8501

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
