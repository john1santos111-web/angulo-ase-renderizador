FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get install -y --no-install-recommends chromium poppler-utils ca-certificates fonts-liberation && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /tmp /home/ase && chmod 1777 /tmp && chown 65534:65534 /home/ase
ENV HOME=/home/ase XDG_CONFIG_HOME=/home/ase/.config XDG_CACHE_HOME=/home/ase/.cache
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY handler.py /app/handler.py
USER 65534:65534
CMD ["python", "-u", "handler.py"]
