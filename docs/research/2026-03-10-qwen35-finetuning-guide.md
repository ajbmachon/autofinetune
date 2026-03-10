# Qwen3.5: Fine-Tuning Guide

**Date:** 2026-03-10
**Purpose:** Research for autofinetune project — comprehensive Qwen3.5 fine-tuning reference

---

## Model Variants

| Model | Type | Architecture | VRAM (bf16 LoRA) | Notes |
|-------|------|-------------|------------------|-------|
| 0.8B | Dense | Multimodal | 3GB | Edge devices, basic tasks |
| 2B | Dense | Multimodal | 5GB | Embedded systems, lightweight |
| 4B | Dense | Multimodal | 10GB | Best under 5B, reasoning score 27 |
| 9B | Dense | Hybrid attention | 22GB | Outperforms Qwen3-30B on many benchmarks |
| 27B | Dense | Gated DeltaNet | 56GB | Hybrid attention architecture |
| 35B-A3B | MoE | 256 experts (8+1 active) | 74GB | Only 3B active params per token |
| 122B-A10B | MoE | 10B active | - | Too large for GB10 |

**Key architecture features:**
- All models use Gated DeltaNet hybrid attention (linear + full attention)
- Native multimodal (text, images, video) from single weights
- 262K context length, extendable to ~1M with YaRN
- 201 languages supported
- Multi-token prediction

## Fine-Tuning Best Practices

### Framework Recommendations

1. **Unsloth** (recommended for our use case): 1.5x faster, 50% less VRAM than FA2. Full Blackwell/DGX Spark support confirmed.
2. **ms-swift 4.0+**: Qwen team's primary framework, supports Dense/MoE via transformers/Megatron backends
3. **TRL (SFTTrainer)**: Standard HuggingFace approach, well-integrated with PEFT
4. **Axolotl**: Good community support, extensive config options

### Critical Settings

- **Precision:** BF16 (preferred over FP16 on Blackwell)
- **MoE models:** Use `FastModel` class in Unsloth, NOT `FastLanguageModel`
- **Dense models:** Standard `FastLanguageModel` works fine
- **QLoRA:** Do NOT use 4-bit quantization with Qwen3.5 (known issues per Unsloth docs)

### LoRA Configuration

| Parameter | Recommended | Notes |
|-----------|-------------|-------|
| Rank (r) | 8-16 | 8 for memory-constrained, 16 for expressiveness |
| Alpha | Match rank (1:1) | alpha=8 for r=8, alpha=16 for r=16 |
| Dropout | 0.05 | Standard practice |
| Target modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj | All projection layers |
| Learning rate | 2e-4 to 5e-4 | Inversely correlates with rank |
| Bias | "none" | Standard practice |

### Training Hyperparameters

| Parameter | Classification | Generation |
|-----------|---------------|------------|
| Learning rate | 1e-5 to 5e-5 | 1e-5 to 2e-5 |
| Batch size | 8-16 | 4-8 |
| Epochs | 3-5 | 2-3 |
| Warmup steps | 100-500 | 200-500 |
| Max grad norm | 1.0 | 1.0 |
| Weight decay | 0.01 | 0.01 |

## Thinking Mode

Qwen3.5 has a hybrid thinking mode with seamless integration of reasoning and rapid response modes.

**For classification tasks:** DISABLE thinking mode
- Adds computational overhead and token generation for reasoning steps
- Classification benefits from direct prediction without intermediate reasoning
- Use `thinking_enabled=False` if available

**For reasoning tasks:** ENABLE thinking mode
- Chain-of-thought reasoning before responses
- Benefits math, medical, domain-specific reasoning

## Chat Template

Uses `<|im_start|>` and `<|im_end|>` tokens for message boundaries:

```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
Hi there!<|im_end|>
```

**Training data format (JSONL):**
```json
{"messages": [
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."},
  {"role": "assistant", "content": "..."}
]}
```

## Classification with Qwen3.5

Not yet natively supported via HuggingFace's `AutoModelForSequenceClassification` (GitHub issue open as of March 2026).

**Recommended approach:** SFT with structured JSON output:
```json
{"messages": [
  {"role": "system", "content": "You classify support tickets. Output JSON only."},
  {"role": "user", "content": "Classify this ticket:\n\n{ticket_text}"},
  {"role": "assistant", "content": "{\"category\": \"network\", \"priority\": \"high\"}"}
]}
```

**Key finding:** Fine-tuned Qwen3-4B matched or exceeded GPT-OSS-120B (30x larger) on 7 of 8 benchmarks for classification tasks.

## Small Model Benchmarks (0.8B)

- MathVista: 62.2
- OCRBench: 74.5
- VideoMME: 63.8 (with subtitles)

## Memory Budget on GB10 (128GB Unified)

| Component | 35B-A3B | 27B | 4B | 2B | 0.8B |
|-----------|---------|-----|-----|-----|------|
| Model weights (bf16) | ~67GB | ~52GB | ~8GB | ~4GB | ~2GB |
| LoRA + Optimizer | ~0.4GB | ~0.3GB | ~0.06GB | ~0.03GB | ~0.01GB |
| Activations (bs=2) | ~4GB | ~3GB | ~1GB | ~0.5GB | ~0.3GB |
| OS + headroom | ~8GB | ~8GB | ~8GB | ~8GB | ~8GB |
| **Total** | **~80GB** | **~63GB** | **~17GB** | **~13GB** | **~10GB** |

All sizes fit comfortably on the GB10.

## Data Requirements

- **Classification:** 500-2000 high-quality labeled examples minimum
- **Generation:** 1000-5000 examples recommended
- **Quality > Quantity:** 500 high-quality examples often beat 10K mediocre ones
- **Multilingual:** All 201 languages supported from the base model
