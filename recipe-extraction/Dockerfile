FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PADDLE_HOME=/app/models/paddleocr
ENV PADDLEX_HOME=/app/models/paddleocr

RUN python download_models.py

EXPOSE 8001

CMD ["python", "run.py"]