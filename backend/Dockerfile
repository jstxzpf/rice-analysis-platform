FROM python:3.10-slim

WORKDIR /app

# --- AGGRESSIVE APT CONFIGURATION ---
# 1. Remove any existing source list files to prevent conflicts.
RUN rm -vf /etc/apt/sources.list.d/*

# 2. Create a new, clean sources.list pointing to Aliyun.
#    'backports' was removed as it was problematic and not needed.
RUN echo "deb http://mirrors.aliyun.com/debian/ bullseye main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian/ bullseye-updates main contrib non-free" >> /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-security/ bullseye-security main contrib non-free" >> /etc/apt/sources.list

# --- END OF APT CONFIGURATION ---

# Install system dependencies that might be needed by CV libraries
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install python packages from Aliyun mirror
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
