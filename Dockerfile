
# Stage 1: Base build stage
FROM python:3.13-slim AS builder
 
# Create the app directory
RUN mkdir /app
 
# Set the working directory inside the container
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install --upgrade pip 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
 
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt
 


# Stage 2: Production stage
FROM python:3.13-slim
 
RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app
 
# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
 
# Set the working directory
WORKDIR /app
 
# Copy application code
COPY . . 

# Collect static files
RUN python manage.py collectstatic --noinput


# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.prod.sh

# Change ownership of the application directory to the appuser
RUN chown -R appuser:appuser /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Switch to non-root user
USER appuser
 
# Expose the application port
EXPOSE 8000 

# Make entry file executable
RUN chmod +x  /app/entrypoint.prod.sh
 
# Start the application using Gunicorn
CMD ["/app/entrypoint.prod.sh"]