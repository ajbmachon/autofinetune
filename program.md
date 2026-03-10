# autofinetune

Autonomous LoRA fine-tuning workbench. Inspired by [autoresearch](https://github.com/karpathy/autoresearch) — the same modify → train → measure → keep/discard loop, adapted from pretraining-from-scratch to LoRA fine-tuning with Unsloth.

## Setup

To set up a new goal, work with the user to:

1. **Agree on a goal tag**: propose a tag based on the objective (e.g. `sentiment-4b`, `summarizer`). The branch `autofinetune/<tag>` must not already exist.
2. **Create the branch**: `git checkout -b autofinetune/<tag> main`
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `program.md` — these instructions (you're reading them now)
   - `prepare.py` — fixed constants, data loading, utilities. Do not modify.
   - `train.py` — fixed training harness. Do not modify.
   - `config.py` — **the only file you edit** during experiments.
4. **Write `goal.md`**: Based on the user's objective, write a `goal.md` that defines:
   - Objective (what are we training for?)
   - Primary metric (what number are we optimizing?)
   - Data paths (where is training/eval data?)
   - Evaluation criteria (how do we measure success?)
   - Research directions (what knobs to try?)
   - Constraints (memory, time, thinking mode on/off)
5. **Set up `config.py`**: Configure for this specific goal:
   - Model name, data paths, format
   - Initial hyperparameters (reasonable defaults from goal.md)
   - Custom `eval_custom_func` if the goal needs accuracy or other metrics beyond eval_loss
6. **Verify**: `uv run prepare.py --verify` — checks model name and data files exist
7. **Initialize `results.tsv`**: Create with just the header row:
   ```
   commit	eval_loss	metric	memory_gb	status	description
   ```
8. **Confirm and go**: Confirm setup looks good, then start the experiment loop.

## Experimentation

Each experiment trains a LoRA adapter. The training script runs for a **fixed time budget** (default 5 minutes, configurable via `TIME_BUDGET` env var). Launch it as: `uv run train.py > run.log 2>&1`

**What you CAN do:**
- Modify `config.py` — this is the only file you edit. Everything is fair game: model choice, LoRA rank, learning rate, batch size, epochs, data formatting, custom eval functions, replay buffers, target modules, etc.

**What you CANNOT do:**
- Modify `train.py` or `prepare.py`. They are read-only infrastructure.
- Install new packages or add dependencies.
- Modify the training harness or evaluation logic (use `eval_custom_func` in config.py for custom metrics).

**The goal is defined in `goal.md`**. Read it to know what metric you're optimizing. Usually `eval_loss` (lower is better) or a custom metric like `eval_accuracy` (higher is better).

**The first run**: Always establish a baseline first — run with the initial config.py unchanged.

## Output format

The training script prints a summary like this:

```
---
eval_loss:        1.2345
eval_accuracy:    0.8750
training_seconds: 300.1
total_seconds:    320.5
peak_memory_gb:   12.3
adapter_size_mb:  45.2
num_epochs:       3
```

Extract key metrics:

```bash
grep "^eval_loss:\|^eval_accuracy:" run.log
```

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated).

The TSV has a header row and 6 columns:

```
commit	eval_loss	metric	memory_gb	status	description
```

1. git commit hash (short, 7 chars)
2. eval_loss achieved (e.g. 1.2345) — use 0.0000 for crashes
3. primary metric from goal.md if applicable (e.g. eval_accuracy) — use 0.0000 if N/A or crash
4. peak memory in GB, round to .1f — use 0.0 for crashes
5. status: `keep`, `discard`, or `crash`
6. short text description of what this experiment tried

Example:

```
commit	eval_loss	metric	memory_gb	status	description
a1b2c3d	1.2345	0.8750	12.3	keep	baseline
b2c3d4e	1.1890	0.9100	12.5	keep	increase LR to 5e-4
c3d4e5f	1.3200	0.8200	12.3	discard	LoRA rank 8
d4e5f6g	0.0000	0.0000	0.0	crash	batch size 32 (OOM)
```

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autofinetune/sentiment-4b`).

LOOP FOREVER:

1. Read `results.tsv`, `config.py`, and `goal.md` to understand current state
2. Decide what to try next (informed by goal.md research directions and past results)
3. Edit `config.py` with your experimental change
4. `git commit config.py -m "experiment: [description]"`
5. Run: `uv run train.py > run.log 2>&1` (redirect everything — do NOT let output flood your context)
6. Extract results: `grep "^eval_loss:\|^eval_accuracy:\|^peak_memory_gb:" run.log`
7. If grep output is empty → crash. Run `tail -n 50 run.log` to read the stack trace
8. Log to `results.tsv` (do NOT commit results.tsv — keep it untracked)
9. If primary metric improved → **keep** (advance the branch, keep the commit)
10. If worse or no improvement → **discard**: `git reset --hard HEAD~1` and delete the adapter

## Available knobs

These are the dimensions you can explore. The order and priority is up to you — decide based on results, intuition, and what goal.md suggests:

- **Learning rate** — the full range from 1e-5 to 5e-4 (and beyond)
- **LoRA rank** — 8, 16, 32, 64. Higher rank = more capacity but more memory
- **Number of epochs** — 1-5+. More can help or overfit
- **Data formatting** — system prompt variations, input structure
- **Sequence length** — profile your data, match to actual distribution
- **Batch size / gradient accumulation** — effective batch size = per_device * grad_accum
- **LoRA target modules** — add or remove projection layers
- **Scheduler** — cosine, linear, constant, warmup variations
- **Custom eval function** — measure what actually matters for the goal
- **Replay buffer** — mix general data to prevent forgetting
- **LoRA alpha** — scaling factor, experiment with alpha:rank ratio
- **Weight decay, dropout** — regularization knobs

Use results.tsv to guide your strategy. If something works, explore nearby. If stuck, try something radically different.

## Crash recovery

- **Typo/import error**: Fix config.py, recommit, retry.
- **OOM**: Log as crash. Decide how to address the memory constraint.
- **Training divergence** (loss goes to inf/nan): Log as crash. Investigate what caused it.
- **Broken idea**: Log as crash, discard, try something else.
- **Can't fix after 2-3 attempts**: Skip the idea entirely. Log crash, move on.

## NEVER STOP

Once the experiment loop has begun (after initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep or away and expects you to continue working **indefinitely** until manually interrupted. You are autonomous.

If you run out of ideas:
- Re-read goal.md for research directions you haven't tried
- Try combining successful changes
- Try more radical changes (different model size, very different LR)
- Try the opposite of what worked (sometimes reveals insights)
- Read the research docs in `docs/research/` for domain-specific tips

The loop runs until the human interrupts you, period.

## Tips for Qwen3.5 models

- **Thinking mode**: Disable for classification tasks (add `/no_think` or use `enable_thinking=False`). Enable for reasoning tasks.
- **Precision**: Always bf16. Never use QLoRA/4-bit quantization.
- **Chat template**: Uses `<|im_start|>`/`<|im_end|>` format. SFTTrainer handles this automatically with chat-format datasets.
- **Model names**: Use `unsloth/Qwen3-{size}` for optimized versions (e.g. `unsloth/Qwen3-4B`, `unsloth/Qwen3-0.6B`).
- **Target modules**: `q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj` covers all projection layers.

## Config.py power features

Since config.py is Python (not YAML), you can:

1. **Define custom eval functions** above CONFIG:
   ```python
   def eval_custom(model, tokenizer, eval_dataset_path):
       # ... run inference, compute accuracy ...
       return {"eval_accuracy": accuracy}

   CONFIG["eval_custom_func"] = eval_custom
   ```

2. **Define custom formatting functions**:
   ```python
   def my_formatter(example):
       return f"Task: {example['task']}\nAnswer: {example['answer']}"

   CONFIG["formatting_func"] = my_formatter
   ```

3. **Use conditional logic**:
   ```python
   import os
   CONFIG["per_device_train_batch_size"] = 8 if os.environ.get("BIG_GPU") else 4
   ```
