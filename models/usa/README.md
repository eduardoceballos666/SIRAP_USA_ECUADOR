# Perfil de modelos: Estados Unidos

Mantén el detector independiente en `detector/rtdetr_r18/`. Entrénalo con placas estadounidenses anotadas en COCO y valídalo en un conjunto reservado antes de declararlo modelo USA. Mientras esa carpeta no contenga un checkpoint Transformers, el pipeline puede usar `merve/license-plates-rtdetrv2` como punto de partida general; sus métricas no son específicas de Estados Unidos.

El OCR también requiere normalización y reglas propias de placas estadounidenses. Esta migración no da por completada esa validación.
