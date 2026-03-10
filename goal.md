# Goal: Sentiment Analysis

## Objective

Train Qwen3-4B to classify text sentiment with structured JSON output.

- **Primary metric:** `eval_accuracy` (classification accuracy on held-out test set, higher is better)
- **Secondary metric:** `eval_loss` (validation loss, lower is better)

## Data

- Training: `~/data/sentiment_train.jsonl` (chat format)
- Validation: `~/data/sentiment_val.jsonl` (chat format)
- Format: `{"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}`

The assistant output should be parseable JSON with a `"sentiment"` field. Example:

```json
{"messages": [
  {"role": "system", "content": "Classify the sentiment. Output JSON only."},
  {"role": "user", "content": "Classify:\n\nThis product exceeded my expectations, absolutely love it!"},
  {"role": "assistant", "content": "{\"sentiment\": \"positive\", \"confidence\": \"high\"}"}
]}
```

## Evaluation

After training, run classification accuracy on the validation set:
1. For each example, generate a response using the model
2. Parse the response as JSON
3. Compare `predicted["sentiment"]` to `expected["sentiment"]`
4. Accuracy = fraction of correct predictions

A custom `eval_custom_func` should be defined in `config.py` to compute this.

## Research Directions

1. **Learning rate sweep** — try 1e-5, 5e-5, 1e-4, 2e-4, 5e-4
2. **LoRA rank** — compare 8, 16, 32
3. **Sequence length** — profile actual text lengths, set to p95 + margin
4. **System prompt variations** — try more detailed classification instructions
5. **Number of epochs** — 1-5, watch for overfitting
6. **Replay buffer** — mix general instruction data to prevent forgetting

## Constraints

- **Thinking mode:** OFF (classification doesn't need chain-of-thought reasoning)
- **Max memory:** 20GB target (4B model is small, leave room for other processes)
- **Time budget:** 5 min default (small model trains fast)
- **Precision:** bf16 only, no QLoRA
