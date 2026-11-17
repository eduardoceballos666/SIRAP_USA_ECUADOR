# api/providers

> Purpose: Vehicle data source adapters for each country.

## Español

Ecuador usa la integración del SRI. Para EE. UU., `usa_jdpower.py` consulta el informe público de J.D. Power con Chromium (Playwright) y devuelve Year and model, Color, Body type y State. Se controla con `vehicle_lookup.enabled` en `config/countries/usa.yaml`; si J.D. Power niega el acceso (401/403/429) no se reintenta y se muestran solo los datos locales.

## English

Ecuador uses the SRI integration. For the U.S., `usa_jdpower.py` reads J.D. Power's public report with Chromium (Playwright) and returns Year and model, Color, Body type and State. It is controlled by `vehicle_lookup.enabled` in `config/countries/usa.yaml`; if J.D. Power denies access (401/403/429) it is not retried and only local data is shown.
