FROM python:3.11-slim

# Create a non-root user and group
RUN groupadd -r secai && useradd -r -g secai secai

WORKDIR /app
COPY . /app

# Install dependencies (Consider adding --require-hashes in the future)
RUN pip install --no-cache-dir -r requirements.txt

# Change ownership of the app directory and drop to the non-root user
RUN chown -R secai:secai /app
USER secai

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
