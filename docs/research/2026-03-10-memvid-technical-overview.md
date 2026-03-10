# Memvid: Technical Overview

**Date:** 2026-03-10
**Purpose:** Research for autofinetune project — understanding memvid for training small models to search it reliably

---

## What is Memvid?

Memvid is a **single-file memory layer for AI agents** written in Rust that replaces complex vector database infrastructure with a portable, serverless alternative. It combines RAG (Retrieval-Augmented Generation) with persistent agent memory in one `.mv2` file.

- **GitHub:** https://github.com/memvid/memvid (13,300+ stars)
- **License:** Apache 2.0
- **Latest Release:** v2.0.138 (March 3, 2026)
- **Primary Language:** Rust (98.5%)

## How It Works

### Storage: Text to Video Frames

1. Text chunks are converted to QR code images
2. QR codes are encoded as video frames using H.264/H.265 compression
3. Everything stored in a single `.mv2` file: text chunks, embeddings, metadata, indexes, crash recovery
4. A lightweight sidecar JSON index accompanies the file

**Storage efficiency:** 10,000 PDFs -> 1.4GB video file (vs 8GB in traditional vector DB RAM)

### Search: Hybrid Retrieval

Two search modes:

1. **Semantic (Vector) Search:** FAISS-based similarity search using sentence-transformer embeddings
2. **Lexical (BM25):** Keyword/full-text matching for exact phrase searches

**Search flow:**
1. Query embedding computed using same embedding model
2. FAISS performs similarity search against stored embeddings
3. Matching frame ranges identified via index
4. Relevant video frames decoded from the MP4
5. Original text chunks extracted from QR codes

**Performance:** <5ms P50 on consumer hardware, +35% accuracy vs traditional memory systems (LoCoMo benchmark)

## API (Python SDK)

```python
from memvid import Memvid

# Create or open existing file
mem = Memvid('knowledge.mv2')

# Store text chunks
mem.put({
    'title': 'Team Info',
    'label': 'notes',
    'text': 'Alice works at Anthropic as a Senior Engineer.'
})

# Semantic search
results = mem.find('who works at AI companies', mode='semantic')

# State queries (entity extraction)
mem.state('Alice')  # Returns: { employer: 'Anthropic', role: 'Senior Engineer' }

# Chat interface (uses pluggable LLM)
response = mem.ask('What role does Alice have?')
```

**Key features:**
- Built-in entity extraction via `state()`
- Time-travel debugging (scrub timelines, replay any moment)
- Pluggable LLMs (OpenAI, Anthropic, local models)
- Live branching in milliseconds
- Deterministic retrieval (reproducible results)
- Offline-first, CPU-friendly

## How Small LLMs (0.8B-2B) Interact with Memvid

Memvid acts as a **context injection system**:

1. Embedding generation is handled by sentence-transformers (not the LLM)
2. Memvid retrieves relevant context via semantic/lexical search
3. Retrieved context injected into the small LLM's prompt
4. Small LLM generates response based on injected context

The architecture is **agnostic to LLM size** — memvid provides the "memory" while the LLM provides the reasoning.

## Training a Model for Memvid Search

Several viable approaches:

### Option A: Query Reformulation (Most Practical)
Train small LLM to rephrase user queries into optimal memvid search queries:
- Input: "What does our SLA say about response times?"
- Output: "SLA response time guarantee hours policy"
- Simple seq2seq SFT task, easy to collect training data

### Option B: Answer Synthesis / RAG Fine-Tuning
Given retrieved chunks from memvid, train the model to synthesize accurate answers:
- Input: [retrieved chunks] + [user question]
- Output: [synthesized answer]
- Standard RAG fine-tuning approach

### Option C: Reranking
Train small LLM to score/rank memvid search results by relevance:
- Memvid returns top-K results
- Small LLM picks the best ones
- Lightweight binary classification task

### Option D: Entity Extraction
Fine-tune small LLM to extract entities from retrieved results, improving the `state()` function's domain accuracy.

**Key insight:** Memvid's deterministic, reproducible retrieval makes it excellent for training data collection — same query always returns same results.

## Related Projects

- **claude-brain** (github.com/memvid/claude-brain): Give Claude Code photographic memory in one .mv2 file
- **maw** (github.com/memvid/maw): Website crawler outputting searchable .mv2 files
- **design-memory**: Extract design systems from websites into memvid

## V2 Improvements (January 2026)

- Deterministic memory (fixed non-reproducible retrieval from v1)
- Versioned storage with persistent, versioned memory in single file
- Crash recovery built-in
- `lex_enabled`/`vec_enabled` state persists after file re-opening
- `ask()` no longer crashes with "frame id out of range" errors
