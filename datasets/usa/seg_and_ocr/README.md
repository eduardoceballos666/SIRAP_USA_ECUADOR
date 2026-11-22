# Recortes de matrículas de EE. UU. (evaluación de OCR y del estado emisor)

**Esta carpeta ya no incluye los archivos.** Las 751 imágenes (`usimages/*.png`), `groundtruth.csv` y los scripts de referencia pertenecen al conjunto `seg_and_ocr` del repositorio [`openalpr/benchmarks`](https://github.com/openalpr/benchmarks), que se distribuye bajo **GNU AGPL-3.0**. Un proyecto publicado bajo Apache-2.0 no debe redistribuirlas, así que se retiraron del árbol de trabajo (siguen en el historial de git anterior a este cambio).

## Cómo reproducir las mediciones que las usaban

1. Descargue `seg_and_ocr/` desde `openalpr/benchmarks` en una carpeta **fuera de este repositorio**.
2. Cada fila de `groundtruth.csv` es `archivo.png,<código de estado>,<matrícula>` (por ejemplo `ak1165.png,ak,FUW999`).
3. Pase los recortes por la API o por el pipeline como se describe en [docs/optimizacion.md](../../../docs/optimizacion.md) y en `notebooks/usa/`. No copie las imágenes dentro de `datasets/` ni de `docs/`.

Las cifras ya publicadas (por ejemplo, lectura del estado en 523 de 751 recortes, 0 erróneas) son resultados de desarrollo calculados con ese conjunto; no son un test independiente. Para un producto comercial conviene reemplazarlas por una evaluación con imágenes propias o con licencia permisiva.
