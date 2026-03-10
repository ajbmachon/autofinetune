# Support Ticket Classification & KB Generation: Fine-Tuning Research

**Date:** 2026-03-10
**Purpose:** Research for autofinetune project — approaches to ticket classification and KB article generation

---

## Classification Approaches for Small LLMs

### SFT with Structured JSON Output (Recommended)

The most effective approach for small models. Format training data as chat conversations:

```json
{"messages": [
  {"role": "system", "content": "You classify support tickets. Output JSON only."},
  {"role": "user", "content": "Classify this ticket:\n\n[ticket_text]"},
  {"role": "assistant", "content": "{\"category\": \"network\", \"priority\": \"high\", \"problem_type\": \"connectivity\"}"}
]}
```

**Why this works:**
- Structured JSON output is reliable and parseable in production
- Small models (4B) match or beat models 30x larger when fine-tuned this way
- Generalizes better than classifier head approaches to unseen variations
- Naturally handles edge cases and ambiguous tickets

### Alternative Approaches (Less Recommended)

- **Classifier head:** Adding classification layers to LLM. Less flexible, harder to update categories.
- **Embedding-based:** Good for retrieval but SFT outperforms on domain-specific classification.
- **Hybrid LLM + Traditional ML:** Best accuracy in some benchmarks but more complex to deploy.

## KB Article Generation

Train on pairs of (ticket_resolution -> kb_article). This is a generation task with longer output sequences.

**Training format:**
```json
{"messages": [
  {"role": "system", "content": "You write knowledge base articles from support ticket data."},
  {"role": "user", "content": "Write a KB article based on this ticket and resolution:\n\nTicket: [text]\nResolution: [text]"},
  {"role": "assistant", "content": "# [Article Title]\n\n## Problem\n[description]\n\n## Solution\n[steps]\n\n## Additional Notes\n[notes]"}
]}
```

**Existing commercial approaches:**
- InvGate: Automated KB article generation from ticket resolutions (~30 seconds per article)
- Desk365 AI: Uses context from ticket resolution notes
- AiseraGPT: Analyzes tickets, resolution notes, and chat logs

## Multi-Task: One Model or Specialized?

### Research Findings

- Meta research shows single models can handle both single-task and multi-task classification
- Stanford (Multitask BERT): Layer sharing achieves 0.886 accuracy across 3 different tasks
- Facebook (Muppet): Massive multi-task pre-finetuning with 50+ datasets shows strong benefits

### Recommendation for This Project

**For models < 4B: Use specialized models** (one for classification, one for generation)
- Better accuracy per task
- Cheaper inference (classification model doesn't need generation capacity)
- Clearer evaluation metrics

**For models >= 4B: One model with task prefixes is viable**
- Format examples with explicit task instructions in the system prompt
- "Classify this ticket: [ticket]" vs "Write a KB article for: [ticket]"
- More convenient to deploy

## Catastrophic Forgetting Mitigation

### 1. Replay Buffers (Most Practical)

Mix 10-20% of general/pretraining data with client-specific data during fine-tuning.
- Simplest and most effective for small models
- No additional memory/computation needed
- No access to original pretraining data required (use general instruction data instead)

### 2. Easy Sample Upweighting (Feb 2026 Research)

Upweight samples the model already handles well (entropy-based weighting).
- Prevents aggressive forgetting of general capabilities
- Works without access to original pretraining data
- Recent paper: "Upweighting Easy Samples in Fine-Tuning Mitigates Forgetting"

### 3. Elastic Weight Consolidation (EWC)

Add regularization penalizing changes to important weights.
- Computationally heavier
- Overkill for single fine-tuning task
- Better for continual learning scenarios

### Practical Recommendation for Client-Specific Models

1. Start with **branch per client** (LoRA adapter per client from shared base)
2. Use **replay buffer** (10% general instruction data mixed in)
3. Monitor validation on both client-specific AND general benchmarks
4. If client needs laser-focused model, accept forgetting — it's a feature, not a bug

## Data Formatting Best Practices

### For the User's Available Data

The user has:
1. **Raw tickets (JSON)** -> Extract text, metadata for training inputs
2. **Classifications (labels)** -> Direct supervision for classification SFT
3. **Problem-solution pairs** -> Train for both classification and resolution generation
4. **LLM-written KB articles** -> Train for article generation (already high quality)

### Recommended Data Pipeline

1. **Classification dataset:** Raw ticket text -> JSON classification label
2. **KB generation dataset:** Ticket + resolution -> Structured KB article
3. **Validation split:** Hold out 10-15% from each, stratified by category
4. **Custom eval:** Classification accuracy on held-out set (not just loss)

### Quality Over Quantity

- 500-1000 high-quality labeled examples for classification
- 1000-5000 examples for generation
- Include edge cases and ambiguous tickets
- Consistent labeling is critical — noisy labels hurt small models disproportionately

## Practical Hyperparameters Summary

| Setting | Classification (4B) | KB Generation (4B) | Client-Specific |
|---------|---------------------|---------------------|-----------------|
| LoRA rank | 8 | 16 | 8 |
| Learning rate | 2e-5 | 1e-5 | 2e-5 |
| Batch size | 8-16 | 4-8 | 8 |
| Epochs | 3-5 | 2-3 | 3-5 |
| Max seq length | Profile data first | 2048 | Profile data first |
| Thinking mode | OFF | OFF | OFF |
| Replay buffer | 0% (first pass) | 0% (first pass) | 10-20% general data |

## Production Deployment

- **Inference latency:** Fine-tuned 4B models run 50-100ms per token on consumer GPUs
- **Memory:** Classification needs ~12GB VRAM (4B model + LoRA adapter)
- **Cost:** One-time fine-tuning vs ongoing API costs
- **Serving:** Can serve multiple LoRA adapters from same base model using vLLM/SGLang
