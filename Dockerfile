FROM python:3.10-slim

RUN apt-get update && apt-get install -y build-essential libolm-dev libmagic-dev ffmpeg && pip3 install matrix-nio[e2e] pyyaml python-magic Pillow aiohttp aiofiles markdown
WORKDIR /app
COPY . .
RUN chmod +x /app/main.py

CMD "/app/main.py"
