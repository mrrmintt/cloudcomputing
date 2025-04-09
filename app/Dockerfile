FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port for web server
EXPOSE 8080

# Run the application
CMD ["python", "app.py"]