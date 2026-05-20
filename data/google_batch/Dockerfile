FROM python:3.9-slim

# Install system dependencies for geospatial libs
RUN apt-get update && apt-get install -y \
    libgdal-dev g++ --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install pandas numpy rasterio geopandas fiona shapely

# 1. Create and use /app for the code
WORKDIR /app
COPY process_list.py .
COPY gini.py .

# 2. Set the runtime directory for the Batch data mount
WORKDIR /mnt/disks/batch

# 3. Use the absolute path to ensure it finds the script
ENTRYPOINT ["python3", "/app/process_list.py"]