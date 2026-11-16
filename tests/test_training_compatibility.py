"""Construct the optional training recipe without a model, network, or training run."""
from src.train import _training_arguments


def test_locked_transformers_accepts_warmup_and_variable_detection_targets(tmp_path):
    args = _training_arguments(output_dir=str(tmp_path), use_cpu=True, report_to="none",
        eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
        metric_for_best_model="eval_loss", greater_is_better=False)
    assert args.get_warmup_steps(100) == 5
    assert args.prediction_loss_only is True
    assert args.metric_for_best_model == "eval_loss"
