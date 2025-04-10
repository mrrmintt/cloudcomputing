FROM python:3.9-slim

WORKDIR /app

# Install ODBC Driver for SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    curl \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for web server
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]