# Autofinetune: How It Works

A complete guide to the autonomous LoRA fine-tuning workbench.

---

## The Big Idea

You describe a goal ("train a 4B model for sentiment analysis"). Claude sets up the experiment, runs a baseline, then enters an autonomous loop: tweak config, train, measure, keep or discard, repeat. You wake up to a results table and the best adapter.

This is [autoresearch](https://github.com/karpathy/autoresearch) adapted for LoRA fine-tuning. Same loop, different domain.

## The Research Loop

```
                    ┌─────────────────────┐
                    │   Read results.tsv  │
                    │   + config.py       │
                    │   + goal.md         │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Decide what to try │
                    │  (based on past     │
                    │   results + goal)   │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  Edit config.py     │
                    │  git commit         │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  uv run train.py    │
                    │  > run.log 2>&1     │
                    │  (5 min budget)     │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │  grep results from  │
                    │  run.log            │
                    └─────────┬───────────┘
                              │
                    ┌─────────┴───────────┐
                    │                     │
                    ▼                     ▼
           ┌──────────────┐     ┌──────────────┐
           │  Improved?   │     │  Worse or    │
           │  KEEP        │     │  same?       │
           │  (advance    │     │  DISCARD     │
           │   branch)    │     │  (git reset) │
           └──────┬───────┘     └──────┬───────┘
                  │                     │
                  └─────────┬───────────┘
                            │
                            ▼
                     Log to results.tsv
                            │
                            ▼
                      LOOP FOREVER
```

Each experiment takes ~5 minutes (configurable). That's ~12 experiments per hour, ~100 overnight. The agent never stops until you interrupt it.

## Architecture: 5 Files That Matter

```
autofinetune/
├── program.md    ← How the loop works (agent reads this)
├── goal.md       ← What we're optimizing (per-branch, you define this)
├── config.py     ← The ONLY file the agent edits during experiments
├── train.py      ← Fixed: loads model, trains LoRA, evaluates, saves
├── prepare.py    ← Fixed: constants, data loading, utilities
```

### Why so few files?

Autoresearch's power is simplicity. The agent needs to understand the entire codebase to make good decisions. 5 files fit comfortably in context. 50 files don't.

### config.py — The Agent's Canvas

This is the only file that changes during experiments. It's Python (not YAML) so the agent can define helper functions:

```python
# The agent can write custom eval functions right here
def eval_custom(model, tokenizer, eval_dataset_path):
    correct, total = 0, 0
    # ... run inference, compare predictions ...
    return {"eval_accuracy": correct / total}

CONFIG = {
    "model_name": "unsloth/Qwen3-4B",
    "learning_rate": 2e-4,
    "lora_r": 16,
    # ... everything the agent experiments with ...
    "eval_custom_func": eval_custom,
}
```

Every CONFIG key is a knob the agent can turn. Learning rate, LoRA rank, batch size, target modules, data formatting, custom evaluation — all configurable.

### train.py — The Fixed Harness

Does one thing: reads CONFIG, trains a LoRA adapter, prints results. The flow:

1. Verify setup (model exists, data files exist)
2. Load model via Unsloth (`FastLanguageModel`)
3. Apply LoRA with CONFIG parameters
4. Load dataset (auto-detects chat/alpaca/completion format)
5. Train with `SFTTrainer` + `TimeBudgetCallback` (stops at time limit)
6. Evaluate (validation loss + optional custom metric)
7. Save adapter to `adapters/<commit_hash>/`
8. Print grep-friendly summary:

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

The agent extracts results with `grep "^eval_loss:" run.log`.

### prepare.py — Utilities

Constants and helpers that both train.py and config.py use:

- **`TIME_BUDGET`** — How long to train (default 300s, override with env var)
- **`load_dataset_auto()`** — Loads .jsonl/.json/.parquet, auto-detects format
- **`merge_replay_data()`** — Mixes general data into training to prevent forgetting
- **`TimeBudgetCallback`** — Stops training when time's up
- **`merge_adapter()`** — Merges LoRA back into base model for deployment
- **`verify_setup()`** — Pre-flight checks before training

### goal.md — What We're Optimizing

Each experiment branch gets its own goal.md. This is the flexibility mechanism — not code, not config schemas. Different goals, same infrastructure:

- **Sentiment analysis:** "Optimize eval_accuracy on held-out reviews"
- **Text summarization:** "Minimize eval_loss on summary generation"
- **Code review:** "Maximize relevance score on review comment quality"

Goal.md tells the agent what data to use, what metric matters, and what directions to explore.

### program.md — Agent Instructions

The agent's operating manual. Covers:

- How to set up a new goal (branch, goal.md, config.py, baseline)
- The experiment loop (modify → commit → train → measure → keep/discard)
- What the agent can and cannot edit
- Crash recovery procedures
- The "never stop" rule (autonomous until interrupted)

## Branching Strategy

Each goal gets its own git branch:

```
main                                ← Infrastructure (train.py, prepare.py, program.md)
├── autofinetune/sentiment-4b       ← Sentiment analysis with 4B model
├── autofinetune/sentiment-0.6b     ← Same task, smaller model
├── autofinetune/summarizer         ← Document summarization
└── autofinetune/code-review        ← Code review comment generation
```

The agent commits config.py changes on its branch. Good experiments advance the branch. Bad ones get `git reset`. The branch tip is always the best config found so far.

`results.tsv` is untracked — it stays local as a running log of all experiments (including discarded ones).

## Data Formats

The harness supports three formats (auto-detected from file content):

**Chat** (recommended for most tasks):
```json
{"messages": [
  {"role": "system", "content": "Classify the sentiment. Output JSON only."},
  {"role": "user", "content": "Classify: This product is amazing, highly recommend!"},
  {"role": "assistant", "content": "{\"sentiment\": \"positive\"}"}
]}
```

**Alpaca** (instruction-following):
```json
{"instruction": "Summarize this article", "input": "...", "output": "..."}
```

**Completion** (raw text):
```json
{"text": "The quick brown fox jumps over the lazy dog."}
```

Files can be `.jsonl`, `.json`, or `.parquet`.

## The Replay Buffer

When fine-tuning a model for a specialized domain, it can forget general knowledge. The replay buffer mixes general instruction data into training:

```python
CONFIG = {
    "replay_dataset": "~/data/general_instructions.jsonl",
    "replay_ratio": 0.1,  # 10% of training batch from replay data
}
```

This is opt-in and off by default.

## Custom Evaluation

The agent can define evaluation functions directly in config.py:

```python
def eval_custom(model, tokenizer, eval_dataset_path):
    """Compute whatever metric matters for this goal."""
    # Run inference on eval set, compare predictions...
    return {"eval_accuracy": 0.87, "eval_f1": 0.83}

CONFIG["eval_custom_func"] = eval_custom
```

All returned keys are printed in the grep-friendly summary, so the agent can track multiple metrics.

## Getting Started

```bash
# 1. Clone and install
git clone https://github.com/ajbmachon/autofinetune
cd autofinetune
uv sync

# 2. Prepare your data in chat format (.jsonl)
# 3. Tell Claude your goal
# 4. Claude creates a branch, writes goal.md, configures config.py
# 5. Claude runs the autonomous experiment loop
# 6. Check results.tsv when you're ready
```

## Merging an Adapter

After finding a good adapter:

```bash
uv run prepare.py --merge adapters/abc1234 --output ~/models/my-finetuned-model
```

This merges the LoRA weights back into the base model for deployment.

## Hardware

Built for NVIDIA GB10 Spark (128GB unified memory, Blackwell sm_121), but works on any CUDA GPU. Memory budget:

| Model | Training Total | Fits on 24GB? |
|-------|---------------|---------------|
| 0.8B  | ~10GB         | Yes           |
| 2B    | ~13GB         | Yes           |
| 4B    | ~17GB         | Yes           |
| 9B    | ~30GB         | No            |
| 27B   | ~63GB         | No            |

## Attribution

Inspired by and adapted from [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) (MIT license). The experiment loop, program.md agent instruction pattern, results.tsv logging, and keep/discard branching strategy all originate from autoresearch. We adapt these patterns from pretraining-from-scratch to LoRA fine-tuning of existing models.
