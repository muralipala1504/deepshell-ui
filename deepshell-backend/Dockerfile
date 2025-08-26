FROM python:3.9-slim

WORKDIR /app

# Copy only necessary files first for caching
COPY setup.py requirements.txt pyproject.toml README.md /app/

# Copy source code before installing
COPY deepshell /app/deepshell
COPY docs /app/docs

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install .

RUN useradd -m deepshelluser
USER deepshelluser

# Default command if no entrypoint override
CMD ["--help"]
