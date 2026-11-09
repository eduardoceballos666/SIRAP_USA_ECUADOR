# Modelo Estados Unidos

Mantén el detector independiente en `detector/rtdetrv2_s/`. Entrénalo con placas estadounidenses anotadas en COCO y evalúalo en un conjunto reservado antes de declararlo modelo USA. Los pesos de entrenamiento quedan en `transformers/` y el modelo de inferencia en `openvino/`; la app carga el segundo con OpenVINO Runtime. Si aún no existe, puede usarse el IR compartido `merve/license-plates-rtdetrv2` (Apache-2.0), cuyas métricas no son específicas de Estados Unidos.
