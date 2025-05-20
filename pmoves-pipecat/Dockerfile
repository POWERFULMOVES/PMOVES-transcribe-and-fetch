FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Command to run your pipecat service
# CMD ["python", "your_pipecat_entrypoint.py"] 