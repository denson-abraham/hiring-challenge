# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY . .

# Install dependencies inside the container
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container


# Expose the application port (Flask runs on port 5000 by default)
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
