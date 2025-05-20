# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /app
COPY ./requirements.txt /usr/src/app/requirements.txt

# Install any needed packages specified in requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container at /usr/src/app
# Assumes your FastAPI app code is in a subdirectory named 'app' within the 'backend' directory
COPY ./app /usr/src/app

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the Python path if needed,
# so that imports like 'from app.main import ...' work.
# If your app structure is flat within /usr/src/app (e.g. main.py directly in /usr/src/app),
# you might not need this, or CMD would be "uvicorn main:app..."
ENV PYTHONPATH=/usr/src

# Run uvicorn server when the container launches
# Assumes your FastAPI app instance is named 'app' in 'app/main.py'
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
