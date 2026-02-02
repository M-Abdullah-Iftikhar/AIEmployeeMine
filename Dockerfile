# Use official Python 3.11 slim image (Debian Bookworm-based)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies:
# - Build tools for compiling extensions (pyodbc, pycairo, etc.)
# - Microsoft ODBC Driver 18 for SQL Server (matches 'ODBC Driver 18 for SQL Server' in settings.py)
# - unixodbc-dev for pyodbc build
# - cairo + pkg-config for reportlab/pycairo
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
    # Add Microsoft package signing key and repo (Debian 12 / Bookworm)
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    # Install the ODBC driver (accept EULA automatically)
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    # Optional: if you need sqlcmd/bcp tools inside the container later, uncomment:
    # ACCEPT_EULA=Y apt-get install -y mssql-tools18 && \
    # Clean up to keep image small
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Collect static files (should now succeed — pyodbc can import without libodbc.so error)
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "project_manager_ai.wsgi:application", "--bind", "0.0.0.0:8000"]
