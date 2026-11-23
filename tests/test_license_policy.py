"""Guardas de licencias: impiden que vuelvan componentes con copyleft fuerte o datos AGPL.

Contexto y alcance: docs/auditoria_licencias.md. Estas pruebas no sustituyen una revisión legal;
solo evitan regresar a problemas ya corregidos (Levenshtein GPL, conjunto AGPL de OpenALPR).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENT_FILES = sorted(ROOT.glob("requirements*.in")) + sorted(ROOT.glob("requirements*.txt"))

# Paquetes de PyPI con GPL/AGPL (o con una variante GPL de la misma biblioteca): no deben entrar en
# dependencias que se distribuyen con un producto bajo Apache-2.0. «rapidfuzz» (MIT) reemplaza a Levenshtein.
COPYLEFT_PACKAGES = {
    "levenshtein", "python-levenshtein", "ultralytics", "ultralytics-thop", "yolov5",
    "pymupdf", "pymupdf4llm", "mysqlclient", "pyqt5", "pyqt6", "pyqt5-sip", "pyqt6-sip",
}
COPYLEFT_MODULES = ("ultralytics", "Levenshtein", "fitz", "pymupdf")
# Código que se publica o se ejecuta en la aplicación (el archivo histórico de YOLO queda fuera).
SHIPPED_CODE_DIRS = ("api", "src", "app", "deploy")


def _package_names(path: Path) -> set[str]:
    names: set[str] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        match = re.match(r"^([A-Za-z0-9][A-Za-z0-9._-]*)", line)
        if match and not line.startswith(("-", "--hash")):
            names.add(re.sub(r"[-_.]+", "-", match.group(1)).lower())
    return names


def test_requirement_files_are_found():
    assert {p.name for p in REQUIREMENT_FILES} >= {"requirements.in", "requirements.txt"}


@pytest.mark.parametrize("path", REQUIREMENT_FILES, ids=lambda p: p.name)
def test_no_copyleft_packages_in_requirements(path: Path):
    found = _package_names(path) & COPYLEFT_PACKAGES
    assert not found, f"{path.name} incluye paquetes con licencia copyleft: {sorted(found)}"


def test_edit_distance_dependency_is_rapidfuzz():
    assert "rapidfuzz" in _package_names(ROOT / "requirements.txt")


def test_shipped_code_does_not_import_copyleft_modules():
    pattern = re.compile(r"^\s*(?:import|from)\s+(" + "|".join(COPYLEFT_MODULES) + r")\b", re.M)
    offenders = []
    for directory in SHIPPED_CODE_DIRS:
        for file in (ROOT / directory).rglob("*.py"):
            if pattern.search(file.read_text(encoding="utf-8", errors="ignore")):
                offenders.append(str(file.relative_to(ROOT)))
    for file in ROOT.glob("*.py"):
        if pattern.search(file.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(file.name)
    assert not offenders, f"Importan módulos con copyleft: {offenders}"


@pytest.mark.parametrize("relative", ["datasets/usa/seg_and_ocr", "datasets/ecuador/seg_and_ocr", "USA_plates/seg_and_ocr"])
def test_openalpr_agpl_dataset_is_not_in_the_tree(relative: str):
    folder = ROOT / relative
    extra = [p.name for p in folder.rglob("*") if p.is_file() and p.name not in {"README.md", ".gitkeep"}]
    assert not extra, f"{relative} contiene archivos AGPL de openalpr/benchmarks: {extra[:5]}"


def test_no_loose_openalpr_crops_in_the_repository_root():
    # Las imágenes de seg_and_ocr se llaman <estado><número>.png (p. ej. «va82.png»); una vez se subieron sueltas a la raíz.
    loose = [p.name for p in ROOT.glob("*.png") if re.fullmatch(r"[a-z]{2}[0-9]+\.png", p.name)]
    assert not loose, f"Imágenes sueltas con el patrón de OpenALPR en la raíz: {loose[:5]}"


def test_space_sync_does_not_publish_the_agpl_dataset():
    source = (ROOT / "deploy" / "huggingface" / "sync_space.py").read_text(encoding="utf-8")
    assert "seg_and_ocr" not in source


def test_project_license_is_apache_2():
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Apache License" in text and "Version 2.0" in text
    assert "END OF TERMS AND CONDITIONS" in text


def test_notice_keeps_required_apache_attributions():
    notice = (ROOT / "NOTICE").read_text(encoding="utf-8")
    assert "Apache License, Version 2.0" in notice
    # El NOTICE de Apache ECharts (incluido en el paquete de la interfaz) debe reproducirse (§4(d)).
    assert "Apache ECharts" in notice and "The Apache Software Foundation" in notice


def test_third_party_notices_cover_datasets_with_conditions():
    text = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for needle in ("CC BY 4.0", "AGPL-3.0", "MPL-2.0", "J.D. Power", "rapidfuzz"):
        assert needle in text, f"THIRD_PARTY_NOTICES.md debe mencionar {needle}"
