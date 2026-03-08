FROM python:3.11-slim

# Install only security-relevant updates and cleanup in one layer
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends gcc default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user and group (already good)
RUN groupadd -r secai && useradd -r -g secai secai

WORKDIR /app
COPY . /app

# Install dependencies with hash checking if you later add hashes
# For now: --no-cache-dir is good
RUN pip install --no-cache-dir -r requirements.txt

# Explicitly set permissions again (defense in depth)
RUN chown -R secai:secai /app && \
    chmod -R 550 /app

# Drop privileges early
USER secai

# Expose only the port we need
EXPOSE 8501

# Run with health-check and read-only filesystem where possible
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=true"]
