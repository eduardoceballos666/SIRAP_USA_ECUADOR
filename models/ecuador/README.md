# Modelo Ecuador

Ecuador **no tiene un detector propio**: usa el mismo RT-DETRv2-S/OpenVINO de la semilla 2 que Estados Unidos, descargado y verificado al iniciar (ver [models/README.md](../README.md)). Para Ecuador solo cambian la normalización de la matrícula (`XXX-0000`) y las reglas de acceso. El desempeño del detector con placas ecuatorianas **todavía no se ha evaluado**.

La carpeta `detector/rtdetrv2_s/openvino/` contiene solo archivos de relleno de una publicación de prueba y la aplicación no los carga. El OCR es `cct-s-v2-global-model` de `fast-plate-ocr`, el mismo que usa Estados Unidos; `ocr/archive/` conserva un OCR afinado anterior que no se usa.
