# Use official Python 3.11 slim image (Debian Bookworm-based)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install build dependencies + Microsoft ODBC Driver 18 for SQL Server
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    apt-transport-https \
    unixodbc-dev \
    build-essential \
    libpq-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev && \
    # Microsoft repo for ODBC Driver 18
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set STATIC_ROOT explicitly for collectstatic (fallback-safe)
ENV DJANGO_STATIC_ROOT=/app/staticfiles

# Collect static files – now it should succeed
RUN python manage.py collectstatic --noinput --clear

# Expose port
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "project_manager_ai.wsgi:application", "--bind", "0.0.0.0:8000"]
