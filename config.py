"""
Experiment configuration — the autonomous agent modifies this file.
See goal.md for current objective and constraints.

You can define helper functions above CONFIG for custom formatting or evaluation.
The CONFIG dict is imported by train.py.
"""

# Example custom eval function (uncomment and modify for your goal):
# def eval_custom(model, tokenizer, eval_dataset_path):
#     """Custom evaluation — e.g., classification accuracy on held-out set."""
#     import json
#     from prepare import load_dataset_auto
#     dataset = load_dataset_auto(eval_dataset_path, "chat")
#     correct, total = 0, 0
#     for example in dataset:
#         messages = example["messages"]
#         # Build prompt from all messages except the last (assistant) message
#         prompt = tokenizer.apply_chat_template(
#             messages[:-1], tokenize=False, add_generation_prompt=True
#         )
#         inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
#         outputs = model.generate(**inputs, max_new_tokens=256, temperature=0.0)
#         response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
#         try:
#             predicted = json.loads(response)
#             expected = json.loads(messages[-1]["content"])
#             if predicted.get("category") == expected.get("category"):
#                 correct += 1
#         except (json.JSONDecodeError, KeyError):
#             pass
#         total += 1
#     return {"eval_accuracy": correct / total if total > 0 else 0.0}


CONFIG = {
    # Model
    "model_name": "unsloth/Qwen3-4B",
    "max_seq_length": 2048,

    # LoRA
    "lora_r": 16,
    "lora_alpha": 16,
    "lora_dropout": 0,
    "lora_target_modules": [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],

    # Training
    "learning_rate": 2e-4,
    "lr_scheduler_type": "cosine",
    "per_device_train_batch_size": 4,
    "gradient_accumulation_steps": 4,
    "warmup_ratio": 0.03,
    "weight_decay": 0.01,
    "optim": "adamw_8bit",
    "num_train_epochs": 3,
    "bf16": True,

    # Data
    "train_dataset": "~/data/train.jsonl",
    "eval_dataset": "~/data/eval.jsonl",
    "dataset_format": "chat",  # "chat", "alpaca", "completion"

    # Optional: custom formatting function (define above CONFIG, reference here)
    "formatting_func": None,

    # Optional: custom eval function (define above CONFIG, reference here)
    "eval_custom_func": None,

    # Optional: replay buffer for forgetting mitigation
    "replay_dataset": None,
    "replay_ratio": 0.0,
}
