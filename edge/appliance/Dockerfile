FROM python:3.11-slim

# Install system dependencies: ffmpeg, networking tools, VA-API drivers for Intel
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    iproute2 \
    iputils-ping \
    net-tools \
    vainfo \
    i965-va-driver \
    intel-media-va-driver-non-free \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy appliance source code
COPY . .

# Run the master discovery and sync entrypoint
CMD ["python3", "appliance_entrypoint.py"]
