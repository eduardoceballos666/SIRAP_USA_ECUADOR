# Modelo Estados Unidos

El detector vigente es la **semilla 2** (RT-DETRv2-S/OpenVINO), entrenada con placas de EE. UU. y compartida con Ecuador. Está en un repositorio de modelos privado y se identifica por commit y SHA-256 en [`selected_checkpoint.json`](selected_checkpoint.json); la aplicación lo descarga y verifica al iniciar (ver [models/README.md](../README.md)).

`detector/rtdetrv2_s/openvino/` guarda un IR de una corrida de prueba anterior (semilla 1, 64 imágenes de entrenamiento) y **no es el modelo vigente**: la aplicación no lo carga. La comprobación vigente es de desarrollo, no un test independiente; los resultados están en [`results/README.md`](../../results/README.md).
