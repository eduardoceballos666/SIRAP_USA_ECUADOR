# tests

> Purpose: Automated checks for application and data processing behavior.

The API contract tests explicitly use a synthetic detector that returns no
detections and a reader that must never be called. They check authentication,
serialization, server decisions and the manual-review response without loading
private or large deployment weights. They do not assert model accuracy. Real
OpenVINO inference is evaluated separately with the recorded checkpoint and
scene split; coordinate regressions have dedicated tests in
`test_openvino_geometry.py`.

## Español

Group tests by shared behavior or country-specific rules when the country workflows are implemented.

## English

Agrupa las pruebas por comportamiento común o reglas por país cuando se implementen los flujos específicos.

