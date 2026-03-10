"""
Autofinetune training script. Single-GPU, LoRA fine-tuning with Unsloth.
Reads CONFIG from config.py, trains, evaluates, saves adapter, prints summary.

Usage: uv run train.py
"""

import os
import subprocess
import time

os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
import torch

t_script_start = time.time()

from config import CONFIG
from prepare import (
    ADAPTER_DIR,
    TIME_BUDGET,
    TimeBudgetCallback,
    load_dataset_auto,
    merge_replay_data,
    verify_setup,
)

# ---------------------------------------------------------------------------
# Verify setup
# ---------------------------------------------------------------------------

verify_setup(CONFIG)

# ---------------------------------------------------------------------------
# Load model + apply LoRA
# ---------------------------------------------------------------------------

from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=CONFIG["model_name"],
    max_seq_length=CONFIG["max_seq_length"],
    dtype=None,
    load_in_4bit=False,
)

model = FastLanguageModel.get_peft_model(
    model,
    r=CONFIG["lora_r"],
    lora_alpha=CONFIG["lora_alpha"],
    lora_dropout=CONFIG["lora_dropout"],
    target_modules=CONFIG["lora_target_modules"],
    bias=CONFIG.get("lora_bias", "none"),
    use_gradient_checkpointing=CONFIG.get("gradient_checkpointing", "unsloth"),
)

# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------

dataset_format = CONFIG.get("dataset_format", "chat")
train_dataset = load_dataset_auto(CONFIG["train_dataset"], dataset_format)

# Optional replay buffer
replay_path = CONFIG.get("replay_dataset")
replay_ratio = CONFIG.get("replay_ratio", 0.0)
if replay_path and replay_ratio > 0:
    train_dataset = merge_replay_data(train_dataset, replay_path, replay_ratio)

eval_dataset = None
eval_path = CONFIG.get("eval_dataset")
if eval_path:
    eval_dataset = load_dataset_auto(eval_path, dataset_format)

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

formatting_func = CONFIG.get("formatting_func")

if formatting_func is None and dataset_format == "alpaca":
    alpaca_template = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""

    def formatting_func(example):
        return alpaca_template.format(
            instruction=example.get("instruction", ""),
            input=example.get("input", ""),
            output=example.get("output", ""),
        )

elif formatting_func is None and dataset_format == "completion":
    def formatting_func(example):
        return example["text"]

# For chat format, SFTTrainer handles it natively via the "messages" column

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

from trl import SFTConfig, SFTTrainer

try:
    commit_hash = subprocess.check_output(
        ["git", "rev-parse", "--short", "HEAD"],
        stderr=subprocess.DEVNULL,
    ).decode().strip()
except Exception:
    commit_hash = "unknown"

adapter_save_path = os.path.join(ADAPTER_DIR, commit_hash)

training_args = SFTConfig(
    output_dir=adapter_save_path,
    learning_rate=CONFIG["learning_rate"],
    lr_scheduler_type=CONFIG.get("lr_scheduler_type", "cosine"),
    per_device_train_batch_size=CONFIG["per_device_train_batch_size"],
    gradient_accumulation_steps=CONFIG.get("gradient_accumulation_steps", 4),
    warmup_ratio=CONFIG.get("warmup_ratio", 0.03),
    weight_decay=CONFIG.get("weight_decay", 0.01),
    optim=CONFIG.get("optim", "adamw_8bit"),
    num_train_epochs=CONFIG["num_train_epochs"],
    bf16=CONFIG.get("bf16", True),
    logging_steps=10,
    save_strategy="no",
    eval_strategy="no",
    report_to="none",
    seed=CONFIG.get("seed", 42),
    max_seq_length=CONFIG["max_seq_length"],
)

trainer_kwargs = dict(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    processing_class=tokenizer,
    callbacks=[TimeBudgetCallback(TIME_BUDGET)],
)

if formatting_func is not None:
    trainer_kwargs["formatting_func"] = formatting_func

trainer = SFTTrainer(**trainer_kwargs)

print(f"\nTraining for up to {CONFIG['num_train_epochs']} epochs "
      f"(time budget: {TIME_BUDGET}s)...")
print(f"Train samples: {len(train_dataset)}")
if eval_dataset:
    print(f"Eval samples: {len(eval_dataset)}")

t_start = time.time()
trainer.train()
training_seconds = time.time() - t_start

# ---------------------------------------------------------------------------
# Evaluate
# ---------------------------------------------------------------------------

eval_loss = None
if eval_dataset is not None:
    eval_results = trainer.evaluate(eval_dataset=eval_dataset)
    eval_loss = eval_results.get("eval_loss")

# Custom eval (defined in config.py)
custom_results = {}
eval_custom_func = CONFIG.get("eval_custom_func")
if eval_custom_func:
    FastLanguageModel.for_inference(model)
    custom_results = eval_custom_func(
        model, tokenizer, CONFIG.get("eval_dataset")
    )

# ---------------------------------------------------------------------------
# Save adapter
# ---------------------------------------------------------------------------

os.makedirs(adapter_save_path, exist_ok=True)
model.save_pretrained(adapter_save_path)
tokenizer.save_pretrained(adapter_save_path)

adapter_size_mb = sum(
    os.path.getsize(os.path.join(dp, f))
    for dp, _, filenames in os.walk(adapter_save_path)
    for f in filenames
) / (1024 * 1024)

# ---------------------------------------------------------------------------
# Summary (grep-friendly)
# ---------------------------------------------------------------------------

peak_memory_gb = torch.cuda.max_memory_allocated() / (1024**3)
total_seconds = time.time() - t_script_start

print("\n---")
if eval_loss is not None:
    print(f"eval_loss:        {eval_loss:.4f}")
for key, value in custom_results.items():
    if isinstance(value, float):
        print(f"{key}:{' ' * max(1, 16 - len(key))}{value:.4f}")
    else:
        print(f"{key}:{' ' * max(1, 16 - len(key))}{value}")
print(f"training_seconds: {training_seconds:.1f}")
print(f"total_seconds:    {total_seconds:.1f}")
print(f"peak_memory_gb:   {peak_memory_gb:.1f}")
print(f"adapter_size_mb:  {adapter_size_mb:.1f}")
print(f"num_epochs:       {CONFIG['num_train_epochs']}")
