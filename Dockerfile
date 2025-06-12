# Use Python official image
FROM python:3.11

RUN apt-get update && apt-get install -y postgresql-client

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8888
EXPOSE 8888

# Default command to run the app
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8888"]