FROM python:3.12-slim-bookworm

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libssl-dev ca-certificates wget && apt-get clean

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY . .

# Expose port if needed (optional, for HTTP endpoints)
EXPOSE 8000

# Entrypoint: run the agent service
CMD ["python", "agent.py"] 