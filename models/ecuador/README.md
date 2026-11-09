# Perfil de modelos: Ecuador

El detector RT-DETRv2 R18 se guarda en `detector/rtdetr_r18/` al ajustarlo con datos ecuatorianos en formato COCO. Si la carpeta no contiene un checkpoint Transformers, la configuración usa temporalmente `merve/license-plates-rtdetrv2` (Apache-2.0), que no ha sido validado específicamente para Ecuador. El OCR configurado es `fast-plate-ocr` y no cambia con el detector.
