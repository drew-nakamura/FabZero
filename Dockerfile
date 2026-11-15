FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iverilog \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server.py ./
COPY siliconos ./siliconos
COPY web ./web
COPY hardware ./hardware
COPY hw/matmul_board ./hw/matmul_board

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SILICONOS_PUBLIC_DEMO=1

CMD ["python", "server.py"]
