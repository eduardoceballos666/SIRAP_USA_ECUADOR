"""SIRAP – Sistema de Detección y Reconocimiento Automático de Placas.

Módulos:
    data_processing  validación de imágenes, recortes y normalización de placas
    model            detector RT-DETRv2 R18 con Transformers, OCR y pipeline ALPR
    access_control   regla de decisión y controlador de barrera
    storage           archivos CSV locales: vehículos, listas e historial
    train            ajuste fino RT-DETRv2 R18 con Transformers
    evaluate         métricas del detector y del sistema completo
    utils            configuración, secretos y logging
"""

__version__ = "1.0.0"
