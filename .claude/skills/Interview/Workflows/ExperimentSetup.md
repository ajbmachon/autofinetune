# ExperimentSetup Workflow

Structured elicitation for fine-tuning goals. Surfaces assumptions about data, models, evaluation, and hardware before the agent starts experimenting. Produces `goal.md`, initial `config.py`, and a versioned interview log.

Adapted from QuickClarify for the fine-tuning domain — longer, with experience assessment and written artifacts.

---

## When to Use

**ExperimentSetup** — The user wants to start a new fine-tuning goal. They have a task in mind but the details need elicitation: what data, what model, what metric, what constraints. This workflow replaces the informal "work with the user to write goal.md" step in `program.md`.

**QuickClarify** — The user has a quick question or small ambiguity that doesn't need a full goal setup. Examples: "Should I use LoRA rank 8 or 16?", "Help me think through my eval function."

**The boundary test:** Is the user starting a new experiment goal from scratch? → ExperimentSetup. Is the user clarifying something within an existing goal? → QuickClarify.

---

## Phase Structure

```
Phase 1: MIRROR     — Reflect understanding of training intent
Phase 2: ASSESS     — Assumption audit + experience gauge + readiness check
Phase 3: PROBE      — 1-4 rounds of domain-specific questions
Phase 4: CONVERGE   — Write goal.md, config.py, interview log; verify setup
```

**Time budget:** 5-10 minutes
**Max rounds:** 4 rounds of AskUserQuestion (hard cap)
**Has interview log:** Written to `goals/<tag>-interview.md`
**Writes artifacts:** `goal.md`, `config.py`, interview log
**No devil's advocate:** Collaborative, not adversarial

---

## Phase 1: MIRROR

Reflect back what the user wants to train and WHY.

**Format:**
```
Here's what I understand:
  • You want to train [model] to [task]
  • Using [data description, if mentioned]
  • The goal is [intent — why this matters, what problem it solves]
  • [Scope/constraints if mentioned]
```

**Fine-tuning-specific mirroring:**
- Restate the TASK (what the model should do), not just the TECHNIQUE (LoRA fine-tuning)
- Include the WHY — "so that [outcome]" — even if the user didn't state it explicitly
- Note data readiness if mentioned ("you already have 5K labeled examples" vs. "you're planning to create data")

---

## Phase 2: ASSESS

Two-layer assumption audit plus experience gauge. This is the highest-value phase — it catches wrong assumptions before they get baked into `goal.md`.

<mandatory_read phase="assess">
Before surfacing assumptions, review your reasoning against:
- [AssumptionAudit.md](../AssumptionAudit.md) — The Three Questions and Common Traps

Focus on: "Am I assuming or did the user say this?" and "What is the user assuming without realizing it?"
</mandatory_read>

### Step A — Claude's Assumptions

State what YOU are assuming about this goal. Common fine-tuning assumptions to check:

- **Data format** — Am I assuming chat format? Alpaca? Completion? Did the user say?
- **Model choice** — Am I defaulting to a model size without checking constraints?
- **Evaluation** — Am I assuming eval_loss is sufficient, or does this task need a custom metric?
- **Hardware** — Am I assuming the user's GPU can handle this model size?
- **Task type** — Am I assuming classification when the user might mean generation?

### Step B — User's Apparent Assumptions

Surface what the USER appears to assume:

- **Data quality** — Are they assuming their data is clean and consistent?
- **"Good enough"** — What does success look like to them? 90% accuracy? Lower loss?
- **Scope** — Are they assuming this is a quick experiment or a production model?
- **Data quantity** — Are they assuming they have enough data?

### Step C — Experience Gauge

Ask the user about their fine-tuning experience using `AskUserQuestion`. This calibrates how much you explain vs. just ask in Phase 3.

**Question:** "How much fine-tuning experience do you have?"

**Options:**
- **First time** — "I'll explain concepts as we go and suggest reasonable defaults"
- **Done it a few times** — "I'll focus on the decisions specific to your goal"
- **Experienced** — "I'll skip the basics and focus on what's unique about this setup"

### Step D — Readiness Check

Assess what the user already has vs. what needs building:

- Data exists? In what format? Train/val split done?
- Evaluation approach clear? Custom eval function needed?
- Hardware known? Memory constraints?
- Any prep work needed before experiments can start?

Present Steps A-B as text, then ask Steps C-D via `AskUserQuestion` (can combine into one round).

---

## Phase 3: PROBE

<mandatory_read phase="probe">
**Read before asking questions:**
- [QuestionGuidelines.md](../QuestionGuidelines.md) — Question quality rules, what to ask vs avoid

Every question must earn its place. If the answer wouldn't change what goes into goal.md or config.py, don't ask it.
</mandatory_read>

1-4 rounds of domain-specific questions via `AskUserQuestion`. Questions adapt to the experience level from Phase 2.

### Domain-Specific Question Areas

**Data:**
- Where is it? What format? How much?
- Train/val split done? What ratio?
- Quality — consistent labels? Noisy examples?
- Sequence lengths — short responses or long-form?

**Task type:**
- Classification, generation, extraction, summarization, other?
- Structured output (JSON) or free-form?
- Single-turn or multi-turn conversations?

**Evaluation:**
- What metric captures success? (eval_loss, accuracy, F1, ROUGE, custom?)
- Need a custom eval function? What would it measure?
- How to measure success — threshold? Comparison to baseline?

**Constraints:**
- Memory budget? (determines max model size)
- Time budget per experiment? (default 5 min)
- Thinking mode on/off? (reasoning tasks vs. classification)
- Any specific model preference or requirement?

**Prep work:**
- Data formatting/conversion needed?
- Eval function needed?
- Test data creation needed?
- Data cleaning or filtering needed?

### Experience-Level Calibration

**First time:**
- Explain concepts inline: "Chat format means each example has a messages array with roles..."
- Suggest specific defaults: "For classification, LoRA rank 16 with lr=2e-4 is a solid starting point"
- Flag common pitfalls: "With only 200 examples, overfitting is likely — we should watch for it"

**Intermediate:**
- Focus on decisions: "Chat or alpaca format for this task?"
- Mention tradeoffs briefly: "Rank 32 gives more capacity but uses more memory"

**Experienced:**
- Ask directly: "What rank and learning rate do you want to start with?"
- Skip explanations unless asked

### Convergence Signals

- Data location and format are clear
- Evaluation approach is defined
- Model choice is settled
- Constraints are captured
- Any needed prep work is identified

**Hard cap:** 4 rounds. If still unclear, note open questions in the interview log and proceed with best understanding.

---

## Phase 4: CONVERGE

Produce the artifacts and verify setup.

### Step 1: Agree on a Goal Tag

Propose a tag based on the objective (e.g., `sentiment-4b`, `summarizer`, `code-review`). Confirm with user. The branch will be `autofinetune/<tag>`.

### Step 2: Create Branch

```bash
git checkout -b autofinetune/<tag> main
```

### Step 3: Write `goal.md`

Write to the repo root. Structure:

```markdown
# Goal: [Title]

## Objective

[What are we training for? 1-2 sentences.]

- **Primary metric:** `[metric_name]` ([description], [higher/lower] is better)
- **Secondary metric:** `[metric_name]` ([description], [higher/lower] is better)

## Data

- Training: `[path]` ([format])
- Validation: `[path]` ([format])
- Format: [description of data structure]

[Example of one data record if helpful]

## Evaluation

[How to measure success. Custom eval function description if needed.]

## Research Directions

1. [Direction 1]
2. [Direction 2]
...

## Constraints

- [Constraint 1]
- [Constraint 2]
...
```

### Step 4: Write Initial `config.py`

Configure for this specific goal:
- Model name and sequence length
- LoRA settings (reasonable defaults informed by the interview)
- Data paths matching what the user specified
- Custom `eval_custom_func` if the goal needs it (define the function above CONFIG)
- Dataset format matching the user's data

### Step 5: Write Interview Log

Write to `goals/<tag>-interview.md`. This is versioned with the repo — it documents the reasoning behind the goal setup.

**Template:**

```markdown
# Experiment Setup Interview Log

**Goal:** [brief description]
**Date:** [date]
**User experience:** [first-time / intermediate / experienced]

## Assumptions Surfaced

**Claude assumed:**
- [assumption and whether it was confirmed/corrected]

**User assumed:**
- [assumption and whether it was confirmed/corrected]

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Model: [choice] | [why] |
| Metric: [choice] | [why] |
| Data format: [choice] | [why] |
| [other key decisions] | [why] |

## Q&A Record

### Round 1
**Q:** [question]
**A:** [response]

### Round 2
...

## Prep Work Identified

- [ ] [items if any, or "None — ready to experiment"]

## Artifacts Produced

- `goal.md` — goal definition
- `config.py` — initial experiment configuration
```

### Step 6: Verify Setup

Run `uv run prepare.py --verify` to confirm the model name resolves and data files exist.

### Step 7: Report

Summarize what was created, list any prep work that needs doing before experiments start, and confirm the user is ready to begin the experiment loop.

---

## Behavioral Norms

### Anti-Sycophancy (Compressed)

ExperimentSetup is collaborative, not adversarial — but that doesn't mean agreeing with everything. If the user's approach has issues, say so directly:

- "With only 100 examples, this model will likely overfit — consider data augmentation or a smaller model"
- "eval_loss alone won't tell you if classification is working — you need a custom accuracy metric"
- "A 9B model won't fit in 24GB during training — either use a smaller model or accept QLoRA (which this harness doesn't support)"

### Domain Expertise

You have fine-tuning domain knowledge. Use it:
- Suggest appropriate model sizes for the task
- Flag data quality concerns
- Recommend evaluation approaches
- Warn about common pitfalls (overfitting small datasets, wrong sequence length, forgetting)

### Don't Over-Prescribe

The autofinetune agent discovers what works through experimentation. Your job is to set up a good starting point and define the goal clearly — not to predict optimal hyperparameters. Leave room for exploration in the research directions.

---

## Degrees of Freedom

| Component | Freedom | Notes |
|-----------|---------|-------|
| Phase ordering | **None** | Mirror → Assess → Probe → Converge is fixed |
| Number of Q&A rounds | **High** | 1-4, convergence-signal driven |
| Question content | **High** | Adapt to domain and experience level |
| Experience calibration | **High** | Depth of explanation varies with experience |
| Goal.md structure | **Low** | Must cover objective, data, evaluation, research directions, constraints |
| Config.py content | **Medium** | Must be valid config, but specific values are flexible |
| Interview log | **Low** | Must follow template, versioned in goals/ |

---

## Example: Experiment Setup in Action

**User:** "New goal: I want to train a model to review pull requests and leave useful comments"

### Phase 1: MIRROR
> Here's what I understand:
> - You want to fine-tune a model that takes a code diff as input and produces a review comment as output
> - The intent is automated code review — the model should catch issues, suggest improvements, and explain why
> - This is a generation task, not classification — the output is free-form text, not a label

### Phase 2: ASSESS

> **I'm assuming:**
> - Chat format data with system prompt defining the reviewer role, user message containing the diff, assistant message with the review
> - You want Qwen3-4B as a starting point (fits comfortably in memory, fast iteration)
> - eval_loss is insufficient here — you'll need a custom metric or at least human spot-checking to measure review quality
> - Thinking mode ON — code review benefits from reasoning through the diff before responding
>
> **You appear to assume:**
> - You have or can create labeled examples of (diff → good review comment) pairs
> - A fine-tuned small model can produce reviews comparable to what a senior dev would write
> - The model will generalize across languages/frameworks from your training examples

Then via `AskUserQuestion`: experience level + readiness check (do you have the data already? what format?).

*[User answers: intermediate experience, has ~2K examples scraped from GitHub PRs in a custom JSON format, no train/val split yet]*

### Phase 3: PROBE (Round 1)
> Q1: "Your 2K examples from GitHub — how did you filter for quality? GitHub PR comments range from 'LGTM' to detailed architectural feedback. If the training data includes low-effort comments, the model will learn to produce them. Did you curate for substantive reviews only?"
> Q2: "What languages are in the dataset? If it's 80% JavaScript and you want to review Python too, the model may not generalize well. Alternatively, if it's diverse, 2K split across many languages might be too thin per language."
> Q3: "How are you measuring 'useful'? This is the hardest part of this goal — eval_loss tells you the model is learning the distribution, but not whether reviews are actually helpful. Options: (a) just eval_loss as a proxy, (b) a custom eval that checks if the review mentions the actual changed lines, (c) human evaluation on a small held-out set after the agent finishes."

*[User answers: filtered for comments >50 chars with code references, mostly Python/TypeScript, happy to start with eval_loss and spot-check manually]*

### Phase 4: CONVERGE

Creates branch `autofinetune/code-review`, writes:

- **`goal.md`** — objective (generate useful code review comments from diffs), primary metric eval_loss, data paths, research directions (learning rate sweep, sequence length tuning for long diffs, system prompt variations, thinking mode on/off comparison)
- **`config.py`** — Qwen3-4B, chat format, max_seq_length 4096 (diffs are long), thinking mode enabled, lr=2e-4, LoRA rank 16
- **`goals/code-review-interview.md`** — full interview log with assumptions, decisions, Q&A record

Prep work identified:
- [ ] Convert custom JSON to chat format `.jsonl`
- [ ] Split into 85/15 train/val
- [ ] Verify sequence lengths — `max_seq_length` may need adjusting if diffs are very long

Runs `uv run prepare.py --verify` to confirm setup.
