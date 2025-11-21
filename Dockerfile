# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files into the container at /app
COPY requirements.txt requirements-dev.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the rest of the application's code into the container at /app
COPY . /app/

# Set the environment to production
ENV ENVIRONMENT=production

# Command to run the application
CMD ["python", "main.py"]
