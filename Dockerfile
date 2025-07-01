# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI runs on
EXPOSE 8000

# Run the FastAPI server
# ``main.py`` lives inside the ``app`` package so we need to reference it as
# ``app.main`` when starting Uvicorn. The previous command failed to locate the
# module resulting in an import error.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
