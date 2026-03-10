"""
prepare.py — Fixed constants and utilities for autofinetune.

READ-ONLY module imported by train.py. The agent never modifies this
file during experiments.
"""

import json
import os
import time

from datasets import Dataset, concatenate_datasets, load_dataset
from transformers import TrainerCallback

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TIME_BUDGET = int(os.environ.get("TIME_BUDGET", 300))  # seconds (5 min default)
MAX_MEMORY_GB = 120
ADAPTER_DIR = "adapters/"

# ---------------------------------------------------------------------------
# verify_setup
# ---------------------------------------------------------------------------


def verify_setup(config: dict) -> None:
    """Sanity-check a CONFIG dict before training begins."""
    model = config.get("model_name", "")
    assert model, "CONFIG['model_name'] must be a non-empty HuggingFace model path"

    train_path = os.path.expanduser(config.get("train_dataset", ""))
    assert os.path.isfile(train_path), f"Training data not found: {train_path}"

    eval_path = config.get("eval_dataset")
    if eval_path:
        eval_path = os.path.expanduser(eval_path)
        assert os.path.isfile(eval_path), f"Eval data not found: {eval_path}"

    print("=== Setup verified ===")
    print(f"  Model        : {model}")
    print(f"  Train data   : {train_path}")
    print(f"  Eval data    : {eval_path or '(none)'}")
    print(f"  Time budget  : {TIME_BUDGET}s")
    print(f"  Max memory   : {MAX_MEMORY_GB} GB")


# ---------------------------------------------------------------------------
# load_dataset_auto
# ---------------------------------------------------------------------------


def _detect_jsonl_format(path: str) -> str:
    """Peek at the first record of a JSONL/JSON file to guess the format."""
    with open(path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        if first.startswith("["):
            # JSON array — read a small prefix to extract first element
            f.seek(0)
            chunk = f.read(65536)
            decoder = json.JSONDecoder()
            idx = chunk.index("[") + 1
            while idx < len(chunk) and chunk[idx] in " \t\n\r":
                idx += 1
            obj, _ = decoder.raw_decode(chunk, idx)
        else:
            obj = json.loads(first)

    if "messages" in obj:
        return "chat"
    if "instruction" in obj:
        return "alpaca"
    if "text" in obj:
        return "completion"
    raise ValueError(
        f"Cannot auto-detect format from keys: {list(obj.keys())}. "
        "Expected 'messages', 'instruction', or 'text'."
    )


def load_dataset_auto(path: str, fmt: str = "auto", tokenizer=None) -> Dataset:
    """Load a dataset from *path* and return an HF ``Dataset``.

    Parameters
    ----------
    path : str
        File path (.jsonl, .json, or .parquet).
    fmt : str
        One of ``"auto"``, ``"chat"``, ``"alpaca"``, ``"completion"``.
    tokenizer :
        Optional tokenizer (reserved for future chat-template use).
    """
    path = os.path.expanduser(path)
    ext = os.path.splitext(path)[1].lower()

    # --- Parquet --------------------------------------------------------
    if ext == ".parquet":
        ds = load_dataset("parquet", data_files=path, split="train")
        return ds

    # --- JSON / JSONL ---------------------------------------------------
    if fmt == "auto":
        fmt = _detect_jsonl_format(path)

    ds = load_dataset("json", data_files=path, split="train")
    return ds


# ---------------------------------------------------------------------------
# merge_replay_data
# ---------------------------------------------------------------------------


def merge_replay_data(
    train_dataset: Dataset,
    replay_path: str | None,
    replay_ratio: float = 0.1,
) -> Dataset:
    """Optionally mix in replay samples to mitigate catastrophic forgetting.

    If *replay_path* is ``None`` or empty the original dataset is returned
    unchanged.
    """
    if not replay_path:
        return train_dataset

    replay_ds = load_dataset_auto(replay_path)
    n_replay = int(replay_ratio * len(train_dataset))
    n_replay = min(n_replay, len(replay_ds))

    if n_replay == 0:
        return train_dataset

    replay_sample = replay_ds.shuffle(seed=42).select(range(n_replay))
    merged = concatenate_datasets([train_dataset, replay_sample])
    print(
        f"Replay: added {n_replay} samples from {replay_path} "
        f"(total {len(merged)})"
    )
    return merged


# ---------------------------------------------------------------------------
# TimeBudgetCallback
# ---------------------------------------------------------------------------


class TimeBudgetCallback(TrainerCallback):
    """Stop training after *budget_seconds* wall-clock seconds."""

    def __init__(self, budget_seconds: int = TIME_BUDGET):
        self.budget = budget_seconds
        self.start_time: float | None = None

    def on_train_begin(self, args, state, control, **kwargs):
        self.start_time = time.time()

    def on_step_end(self, args, state, control, **kwargs):
        if self.start_time and (time.time() - self.start_time) >= self.budget:
            control.should_training_stop = True


# ---------------------------------------------------------------------------
# merge_adapter
# ---------------------------------------------------------------------------


def merge_adapter(adapter_path: str, output_path: str, config: dict) -> None:
    """Merge a saved LoRA adapter back into its base model and save."""
    from peft import PeftModel
    from unsloth import FastLanguageModel as FastModel

    model_name = config["model_name"]
    print(f"Loading base model: {model_name}")
    model, tokenizer = FastModel.from_pretrained(
        model_name,
        load_in_4bit=False,
    )

    print(f"Loading adapter: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)
    model = model.merge_and_unload()

    output_path = os.path.expanduser(output_path)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    print(f"Merged model saved to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="autofinetune utilities — verify setup or merge adapters"
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify setup for current config"
    )
    parser.add_argument("--merge", type=str, help="Path to adapter to merge")
    parser.add_argument("--output", type=str, help="Output path for merged model")
    args = parser.parse_args()

    if args.verify:
        from config import CONFIG

        verify_setup(CONFIG)
    elif args.merge:
        from config import CONFIG

        merge_adapter(args.merge, args.output or "merged_model", CONFIG)
    else:
        parser.print_help()
