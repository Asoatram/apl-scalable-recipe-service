# Use official Python slim image for smaller size
FROM python:3.11-slim

# Set working directory in container
WORKDIR /APL

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

ENV DATABASE_URL=postgresql+asyncpg://postgres:daffa213@local-postgres:5432/localdb
ENV SECRET_KEY=Rareu1Oea+GSZgqDu7NMwZ0m9u0pjtI+jeavvt3astU=
ENV KAFKA_TOPIC=cooking-tips-requests
ENV KAFKA_RESPONSE_TOPIC=cooking-tips-response
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port FastAPI will run on
EXPOSE 8000

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
