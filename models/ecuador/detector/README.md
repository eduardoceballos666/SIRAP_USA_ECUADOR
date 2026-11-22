# Detector Ecuador

No hay un detector ecuatoriano: la aplicación usa el detector compartido de la semilla 2 (ver [models/README.md](../../README.md)). `rtdetrv2_s/openvino/` contiene solo archivos de relleno de una publicación de prueba y no se carga.

Si en el futuro se entrena un modelo para Ecuador (`python -m src.train --country ecuador --data-dir <COCO>`), debe evaluarse en un conjunto ecuatoriano reservado antes de proponerlo, y adoptarlo exige actualizar el registro de selección como se explica en [docs/optimizacion.md](../../../docs/optimizacion.md).
