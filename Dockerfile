FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dbt
RUN pip install dbt-core dbt-postgres dbt-snowflake dbt-bigquery

# Install other Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Create dbt profiles directory
RUN mkdir -p /root/.dbt

# Set environment variables
ENV PYTHONPATH=/app
ENV DBT_PROFILES_DIR=/root/.dbt

# Expose port for FastAPI
EXPOSE 8000

# Default command
CMD ["python", "api/main.py"]