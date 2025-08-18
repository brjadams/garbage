FROM python:3.12-slim-trixie

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh
# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh
# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

ADD . /app
WORKDIR /app

# Install dependencies
RUN uv sync --locked

# Expose the port FastAPI will run on
EXPOSE 80

# Command to run the FastAPI application
# CMD ["uv", "run", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["/app/.venv/bin/fastapi", "run", "api.py", "--port", "80", "--host", "0.0.0.0"]