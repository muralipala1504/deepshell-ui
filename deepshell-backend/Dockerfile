# Use official Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy backend source code and config files
COPY . /app

# Install bash and Python dependencies, then install your package
RUN apt-get update && apt-get install -y bash \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir .

# Expose backend port (adjust if needed)
EXPOSE 8000

# Default command: start bash shell
CMD ["/bin/bash"]
