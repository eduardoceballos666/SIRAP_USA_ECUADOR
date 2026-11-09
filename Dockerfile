# SIRAP · API FastAPI + interfaz Vue en una sola imagen.
# Compatible con Hugging Face Spaces (usuario 1000, puerto 7860), Render, Railway o un servidor propio.

# 1) Compilar el frontend Vue
FROM node:22-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 2) Convertir el checkpoint Apache-2.0 a OpenVINO IR antes del runtime.
FROM python:3.11-slim AS detector-export
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HF_HOME=/root/.cache/huggingface
WORKDIR /build
COPY requirements-training.txt ./
RUN pip install --require-hashes -r requirements-training.txt
COPY src/__init__.py src/export_openvino.py ./src/
RUN python -m src.export_openvino \
    --model-id merve/license-plates-rtdetrv2 \
    --output-dir /build/models/shared/detector/rtdetrv2_s/openvino

# 3) Runtime de la API: OpenVINO + OCR, sin Torch ni Transformers.
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH HF_HOME=/home/user/.cache/huggingface \
    SIRAP_DATA_DIR=/home/user/app/data/processed \
    SIRAP_GITHUB_REQUIRED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
WORKDIR /home/user/app
RUN chown user:user /home/user/app

COPY --chown=user requirements.txt ./
COPY --chown=user api/requirements.txt api/requirements.txt
RUN pip install --require-hashes -r api/requirements.txt
# Chromium se incluye para satisfacer la dependencia de Playwright; SIRAP no lo usa para consultar EcuadorLegalOnline.
RUN PLAYWRIGHT_BROWSERS_PATH=/ms-playwright python -m playwright install --with-deps chromium \
    && chmod -R a+rX /ms-playwright \
    && rm -rf /var/lib/apt/lists/*
USER user
# Descarga el OCR (≈5 MB) durante la construcción para que el primer reconocimiento sea inmediato.
RUN python -c "from fast_plate_ocr import LicensePlateRecognizer as R; R('cct-s-v2-global-model')"

COPY --chown=user . .
COPY --chown=user --from=frontend /app/frontend/dist frontend/dist
COPY --chown=user --from=detector-export /build/models/shared/detector/rtdetrv2_s/openvino models/shared/detector/rtdetrv2_s/openvino
RUN mkdir -p data/processed

EXPOSE 7860
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
