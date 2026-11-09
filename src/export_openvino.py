"""Exporta un checkpoint RT-DETRv2-S a OpenVINO IR para inferencia nativa.

El ajuste fino usa Transformers/PyTorch antes del despliegue. La aplicación final
carga únicamente openvino_model.xml + openvino_model.bin con openvino.Core.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_MODEL_ID = "merve/license-plates-rtdetrv2"
DEFAULT_IMAGE_SIZE = 640


def export_openvino_model(model_source: str | Path, output_dir: str | Path,
                          image_size: int = DEFAULT_IMAGE_SIZE,
                          compress_to_fp16: bool = False) -> Path:
    """Convierte los logits y cajas de un checkpoint HF a OpenVINO IR."""
    import openvino as ov
    import torch
    from transformers import AutoImageProcessor, RTDetrV2ForObjectDetection

    source = str(model_source)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    processor = AutoImageProcessor.from_pretrained(source, trust_remote_code=False, use_fast=False)
    model = RTDetrV2ForObjectDetection.from_pretrained(source, trust_remote_code=False)
    model.eval()

    class DetectionOutputs(torch.nn.Module):
        def __init__(self, wrapped: torch.nn.Module):
            super().__init__()
            self.wrapped = wrapped

        def forward(self, pixel_values: torch.Tensor, pixel_mask: torch.Tensor):
            output = self.wrapped(pixel_values=pixel_values, pixel_mask=pixel_mask, return_dict=True)
            return output.logits, output.pred_boxes

    wrapped = DetectionOutputs(model).eval()
    pixels = torch.zeros((1, 3, image_size, image_size), dtype=torch.float32)
    mask = torch.ones((1, image_size, image_size), dtype=torch.long)
    with torch.inference_mode():
        ov_model = ov.convert_model(wrapped, example_input=(pixels, mask))

    # Keep the public model's two tensors stable for the native Runtime postprocessor.
    for port, name in zip(ov_model.inputs, ("pixel_values", "pixel_mask")):
        port.get_tensor().set_names({name})
    for port, name in zip(ov_model.outputs, ("logits", "pred_boxes")):
        port.get_tensor().set_names({name})
    model_file = target / "openvino_model.xml"
    ov.save_model(ov_model, str(model_file), compress_to_fp16=compress_to_fp16)

    size = getattr(processor, "size", {}) or {}
    image_mean = list(getattr(processor, "image_mean", [0.485, 0.456, 0.406]))
    image_std = list(getattr(processor, "image_std", [0.229, 0.224, 0.225]))
    resample = getattr(processor, "resample", 2)
    manifest: dict[str, Any] = {
        "architecture": "RT-DETRv2-S",
        "backbone": "ResNet-18vd",
        "runtime": "OpenVINO Runtime Python API",
        "source_checkpoint": source,
        "source_license": "Apache-2.0",
        "input_shape": [1, 3, image_size, image_size],
        "input_names": ["pixel_values", "pixel_mask"],
        "output_names": ["logits", "pred_boxes"],
        "num_labels": int(getattr(model.config, "num_labels", 1)),
        "id2label": {str(key): value for key, value in model.config.id2label.items()},
        "do_resize": bool(getattr(processor, "do_resize", True)),
        "do_rescale": bool(getattr(processor, "do_rescale", True)),
        "do_normalize": bool(getattr(processor, "do_normalize", False)),
        "image_mean": image_mean,
        "image_std": image_std,
        "rescale_factor": float(getattr(processor, "rescale_factor", 1 / 255)),
        "resample": int(resample) if isinstance(resample, int) else str(resample),
        "resize_max_height": int(size.get("max_height", image_size)),
        "resize_max_width": int(size.get("max_width", image_size)),
        "pad_value_after_normalization": 0.0,
        "compressed_to_fp16": bool(compress_to_fp16),
    }
    (target / "sirap_openvino.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return model_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta RT-DETRv2-S a OpenVINO IR")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID,
                        help="ID del Hub o carpeta local con pesos Transformers")
    parser.add_argument("--output-dir", default="models/shared/detector/rtdetrv2_s/openvino")
    parser.add_argument("--image-size", type=int, default=DEFAULT_IMAGE_SIZE)
    parser.add_argument("--compress-to-fp16", action="store_true",
                        help="Reduce el tamaño del IR comprimiendo pesos constantes a FP16")
    args = parser.parse_args()
    model_file = export_openvino_model(args.model_id, args.output_dir, args.image_size,
                                       args.compress_to_fp16)
    print(f"OpenVINO IR guardado: {model_file}")


if __name__ == "__main__":
    main()
