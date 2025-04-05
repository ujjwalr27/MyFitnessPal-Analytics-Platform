FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p backend/uploads

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "backend/app.py"] 