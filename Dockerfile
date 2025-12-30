# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for PyMuPDF/fitz)
# standard slim image usually works, but sometimes needs build-essential or mupdf-tools
# PyMuPDF binary wheels usually include dependencies, so simple pip install works on standard linux
# We might need to install 'poppler-utils' if using pdf2image, but we are using fitz.
# Let's keep it simple first.

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port (Cloud Run / Render usually expect 8000 or 8080)
EXPOSE 8000

# Define environment variable (Default, can be overridden)
# ENV GOOGLE_API_KEY="" 

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
