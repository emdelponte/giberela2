FROM rocker/r-ver:4.4.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Install R packages
RUN Rscript -e "install.packages(c('rms', 'jsonlite'), repos='https://cloud.r-project.org')"

# Set up working directory
WORKDIR /app
COPY . /app

# Set up Python virtual environment and install dependencies
RUN python3 -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN pip install --no-cache-dir "fastmcp>=2.0.0" "mcp<2" pydantic uvicorn

# Expose web port (Hugging Face uses port 7860)
EXPOSE 7860
ENV PORT=7860

# Run FastMCP over SSE / HTTP
CMD ["python3", "server.py", "--transport", "sse", "--port", "7860", "--host", "0.0.0.0"]
