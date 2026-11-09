# Modelo Ecuador

El detector RT-DETRv2-S de Ecuador se entrena con datos COCO específicos y se guarda bajo `detector/rtdetrv2_s/`: los pesos de entrenamiento en `transformers/` y el IR de producción en `openvino/`. La app carga el IR con OpenVINO Runtime. Si todavía no hay un IR ecuatoriano, el Space usa el modelo compartido de placas Apache-2.0, que no está validado específicamente para Ecuador. El OCR configurado es `fast-plate-ocr` y permanece independiente del detector.
