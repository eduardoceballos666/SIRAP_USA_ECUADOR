"""Path and publication helpers for SIRAP Ecuador Colab notebooks.

The repository clone is the working tree. Generated artifacts are saved in canonical
repository folders; publishing is explicit and uses a Colab secret/environment token.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

REPOSITORY_URL = "https://github.com/eduardoceballos666/SIRAP_USA_ECUADOR.git"


def ensure_repository(preferred: str | Path = "/content/SIRAP_USA_ECUADOR") -> Path:
    """Return a usable clone without deleting any pre-existing non-Git directory."""
    preferred = Path(preferred)
    candidates = [preferred, preferred.with_name(preferred.name + "_notebook")]
    for candidate in candidates:
        if (candidate / ".git").is_dir():
            status = subprocess.run(
                ["git", "-C", str(candidate), "status", "--porcelain"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            if not status:
                subprocess.run(
                    ["git", "-C", str(candidate), "pull", "--ff-only", "origin", "main"],
                    check=True, capture_output=True, text=True,
                )
            return candidate
        if not candidate.exists():
            subprocess.run(
                ["git", "clone", "--depth", "1", REPOSITORY_URL, str(candidate)],
                check=True,
            )
            return candidate
    raise RuntimeError(
        "No se encontró una carpeta Git segura para el repositorio. "
        "No se borró ninguna carpeta existente; revisa /content/SIRAP_USA_ECUADOR "
        "y /content/SIRAP_USA_ECUADOR_notebook."
    )


def repository_paths(repo_root: str | Path) -> dict[str, Path]:
    """Canonical input and output folders for the Ecuador notebooks."""
    root = Path(repo_root).resolve()
    paths = {
        "repo": root,
        "metrics": root / "results" / "metrics",
        "figures": root / "results" / "figures",
        "ecuador_results": root / "results" / "ecuador",
        "video_results": root / "results" / "ecuador" / "videos",
        "gate": root / "datasets" / "ecuador" / "gate",
        "savh": root / "datasets" / "ecuador" / "savh",
        "savh_ocr": root / "evaluation" / "ecuador" / "savh" / "artifacts" / "ocr",
        "blind_eval": root / "evaluation" / "ecuador" / "blind_evaluation",
        "models": root / "models" / "ecuador",
        "detector": root / "models" / "ecuador" / "detector",
        "ocr_models": root / "models" / "ecuador" / "ocr",
        "detector_checkpoint": root / "models" / "ecuador" / "detector" / "rtdetrv2_s",
        "ocr_onnx": root / "models" / "ecuador" / "ocr" / "ecuador_ocr.onnx",
        "workspace": Path("/content/SIRAP_workspace"),
    }
    for key in ("metrics", "figures", "ecuador_results", "video_results", "workspace", "detector", "ocr_models"):
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def _github_token() -> str | None:
    try:
        from google.colab import userdata
        token = userdata.get("GITHUB_TOKEN")
        if token:
            return token
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN")


def publish_artifacts(repo_root: str | Path, paths: list[str], message: str,
                      force_ignored: bool = False) -> list[str]:
    """Commit and push only changed files under the requested repository paths."""
    root = Path(repo_root).resolve()
    token = _github_token()
    if not token:
        print(
            "No se publicó: crea el secreto GITHUB_TOKEN en Colab (permiso Contents: Read and write) "
            "y vuelve a ejecutar esta celda. Los archivos ya quedaron en el clon local."
        )
        return []

    git = ["git", "-C", str(root)]
    allowed = []
    for item in paths:
        target = (root / item).resolve()
        if target != root and root not in target.parents:
            raise ValueError(f"Ruta fuera del repositorio: {item}")
        if target.exists():
            allowed.append(str(target.relative_to(root)))
    if not allowed:
        print("No hay rutas de salida existentes para publicar.")
        return []

    add_args = ["add"] + (["-f"] if force_ignored else []) + ["--", *allowed]
    subprocess.run(git + add_args, check=True)
    changed = subprocess.run(
        git + ["diff", "--cached", "--name-only"],
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    if not changed:
        print("No hay cambios nuevos para publicar.")
        return []

    too_large = []
    for rel in changed:
        size = (root / rel).stat().st_size
        if size >= 90 * 1024 * 1024:
            too_large.append((rel, size))
    if too_large:
        subprocess.run(git + ["reset", "--", *changed], check=False)
        details = ", ".join(f"{name} ({size / 1024 / 1024:.1f} MiB)" for name, size in too_large)
        raise RuntimeError(
            "GitHub rechaza archivos de 100 MiB o más; no se publicó ningún archivo. "
            f"Usa Git LFS o almacenamiento de artefactos para: {details}"
        )

    subprocess.run(git + ["config", "user.name", "SIRAP Notebook"], check=True)
    subprocess.run(git + ["config", "user.email", "sirap-notebook@users.noreply.github.com"], check=True)
    subprocess.run(git + ["commit", "-m", message], check=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        askpass = Path(temp_dir) / "askpass.sh"
        askpass.write_text(
            '#!/bin/sh\ncase "$1" in\n'
            '*Username*) echo "x-access-token" ;;\n'
            '*Password*) printf "%s" "$SIRAP_GITHUB_TOKEN" ;;\n'
            '*) exit 1 ;;\nesac\n',
            encoding="utf-8",
        )
        askpass.chmod(0o700)
        env = os.environ.copy()
        env["SIRAP_GITHUB_TOKEN"] = token
        env["GIT_ASKPASS"] = str(askpass)
        env["GIT_TERMINAL_PROMPT"] = "0"
        subprocess.run(git + ["push", "origin", "HEAD:main"], check=True, env=env)
    print("Publicados en GitHub:", *changed, sep="\n- ")
    return changed


def publish_detector_ir(repo_root: str | Path, country: str) -> list[str]:
    """Publica solo el IR por país; el Space recibe el commit desde GitHub Actions."""
    if country not in {"ecuador", "usa"}:
        raise ValueError("country debe ser 'ecuador' o 'usa'.")
    relative = Path("models") / country / "detector" / "rtdetrv2_s" / "openvino"
    root = Path(repo_root).resolve()
    model_dir = root / relative
    required = ("openvino_model.xml", "openvino_model.bin", "sirap_openvino.json", "sirap_training.json")
    missing = [name for name in required if not (model_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"El IR {country} está incompleto; faltan: {', '.join(missing)}")
    too_large = [(name, (model_dir / name).stat().st_size) for name in required
                 if (model_dir / name).stat().st_size >= 90 * 1024 * 1024]
    if too_large:
        details = ", ".join(f"{name} ({size / 1024 / 1024:.1f} MiB)" for name, size in too_large)
        raise RuntimeError(f"Los archivos superan el límite de publicación segura en GitHub: {details}")
    return publish_artifacts(root, [str(relative)],
                             f"Publicar RT-DETRv2-S OpenVINO para {country}", force_ignored=True)
