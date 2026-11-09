"""Compara dos configuraciones de RT-DETRv2-S con semillas emparejadas.

La selección de hiperparámetros debe realizarse con train/validación; el split de
prueba se reserva para la evaluación final y no se utiliza en este helper.
"""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


def save_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def summary_for(rows: list[dict[str, Any]], seeds: list[int]) -> dict[str, Any]:
    by_seed: dict[int, dict[str, dict[str, Any]]] = {}
    for row in rows:
        by_seed.setdefault(int(row["semilla"]), {})[str(row["modelo"])] = row
    pairs = []
    for seed in seeds:
        models = by_seed.get(seed, {})
        if "base" in models and "candidata" in models:
            base, candidate = models["base"], models["candidata"]
            pairs.append({
                "semilla": seed,
                "map50_95_base": base["map50_95"],
                "map50_95_candidata": candidate["map50_95"],
                "delta_map50_95": candidate["map50_95"] - base["map50_95"],
                "delta_recall": candidate["recall"] - base["recall"],
            })
    deltas = [pair["delta_map50_95"] for pair in pairs]
    return {
        "detector": "RT-DETRv2-S",
        "estado": "completo" if len(pairs) == len(seeds) else "parcial",
        "semillas_planeadas": seeds,
        "split_evaluacion": "val",
        "pares_completos": len(pairs),
        "comparaciones_pareadas": pairs,
        "delta_medio_map50_95": statistics.mean(deltas) if deltas else None,
        "delta_std_map50_95": statistics.stdev(deltas) if len(deltas) > 1 else None,
        "semillas_con_mejora": sum(delta > 0 for delta in deltas),
        "nota": "Comparación descriptiva en validación; requiere evaluación final única en test reservado.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validación multisemilla RT-DETRv2-S")
    parser.add_argument("--data-dir", type=Path, required=True, help="Dataset COCO con train/ y valid/")
    parser.add_argument("--configs", type=Path, required=True,
                        help="JSON con configuraciones base y candidata; cada una admite epochs, batch_size, learning_rate y weight_decay")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--country", choices=("ecuador", "usa"), default="ecuador")
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    parser.add_argument("--model-id", default="merve/license-plates-rtdetrv2")
    args = parser.parse_args()
    if len(set(args.seeds)) != len(args.seeds) or len(args.seeds) < 2:
        parser.error("Indique al menos dos semillas distintas.")
    config = json.loads(args.configs.read_text(encoding="utf-8"))
    if set(config) != {"base", "candidata"}:
        parser.error("El JSON debe tener exactamente las claves 'base' y 'candidata'.")

    import pandas as pd
    from src.evaluate import evaluate_detector
    from src.train import train_detector

    output = args.output_dir.expanduser().resolve()
    rows = []
    for seed in args.seeds:
        for label, params in config.items():
            checkpoint = output / "models" / f"{label}_seed_{seed}"
            run_dir = output / "runs" / f"{label}_seed_{seed}"
            train_detector(
                args.data_dir, country=args.country, model_id=args.model_id,
                output_dir=checkpoint, run_dir=run_dir,
                epochs=int(params.get("epochs", 30)),
                batch_size=int(params.get("batch_size", 8)),
                learning_rate=float(params.get("learning_rate", 5e-5)),
                weight_decay=float(params.get("weight_decay", 1e-4)),
                seed=seed, force=False,
            )
            metrics = evaluate_detector(args.data_dir, args.country, "val", checkpoint,
                                        args.model_id, threshold=0.001,
                                        result_path=output / "metrics" / f"{label}_seed_{seed}_val.json")
            row = {"semilla": seed, "modelo": label, **metrics}
            rows.append(row)
            save_json(output / "metrics" / f"{label}_seed_{seed}.json", row)
            frame = pd.DataFrame(rows).sort_values(["semilla", "modelo"])
            output.mkdir(parents=True, exist_ok=True)
            frame.to_csv(output / "comparacion_multisemilla_rtdetr.csv", index=False)
            save_json(output / "resumen_multisemilla_rtdetr.json", summary_for(rows, args.seeds))
    print(json.dumps(summary_for(rows, args.seeds), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
