# Pull official base image.
FROM python:3.10-bullseye

# Prevents Python from writing .pyc files,
# equivalent to python -B.
ENV PYTHONDONTWRITEBYTECODE=1
# Prevents Python from buffering stdout and
# stderr, equivalent to python -u.
ENV PYTHONUNBUFFERED=1

# Set work directory, create if not existing.
WORKDIR /home/app

# Install system dependencies.
# Fix libmysqlclient-dev has no installation candidate:
# libmysqlclient-dev -> default-libmysqlclient-dev,
# specific to Docker.
RUN apt update \
    && apt install -y --no-install-recommends \
        netcat \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies.
COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set up entry point.
COPY ./entrypoint.sh .
# Replace CR, carriage return character (\r or ^M), with ''.
# -i: edit in place; $//g: only replace CR right before '\n'
RUN sed -i "s/\r$//g" entrypoint.sh
RUN chmod +x entrypoint.sh

# Run entrypoint.sh.
ENTRYPOINT ["sh", "/home/app/entrypoint.sh"]
