# QuickClarify Workflow

Lightweight elicitation for tasks where the WHAT is roughly known but the HOW, edges, and assumptions need 2-5 minutes of refinement.

---

## When to Use (vs Full Workflows)

**QuickClarify** — The idea doesn't need to defend its right to exist. The user knows what they want. But there are ambiguities, unstated assumptions, or scope questions that would cause errors if left unresolved. Examples: "Should I use LoRA rank 8 or 16 for this?", "Help me think through my eval function", "I want to add a replay buffer — what ratio?"

**Full Workflows** (ExperimentSetup, etc.) — The idea itself needs structured elicitation, the scope is large, or significant domain-specific questioning is required. Examples: "New goal: sentiment analysis," "Train a model for code review."

**The boundary test:** Could Claude proceed with reasonable confidence after 3-5 questions? → QuickClarify. Does Claude need to assess experience, surface domain assumptions, and produce `goal.md` + `config.py`? → ExperimentSetup.

---

## Phase Structure

```
Phase 1: MIRROR     — Reflect back understanding (catch gross misalignment)
Phase 2: SURFACE    — Brief assumption audit (name what's unstated)
Phase 3: PROBE      — 1-3 rounds of targeted questions (resolve ambiguities)
Phase 4: CONVERGE   — Inline summary of aligned understanding
```

**Time budget:** 2-5 minutes total
**Max rounds:** 3 rounds of AskUserQuestion (hard cap)
**No working log:** Context window sufficient for 3-8 turns
**No blocking research:** Optional background research only
**No devil's advocate:** Purely collaborative

---

## Phase 1: MIRROR

Paraphrase what you understood from the user's request. This is NOT a summary — it's a **cognitive mirror** that lets the user see their idea from outside their head for the first time.

**Format:**
```
Here's what I understand you want:
  • [paraphrase of task]
  • [paraphrase of intent/desired outcome]
  • [paraphrase of scope, if stated]
```

**Purpose:** Catches gross misalignment immediately. If your mirror is wrong, the user corrects before any work begins. If it's right, both parties start from confirmed shared understanding.

**What makes a good mirror:**
- Restate in YOUR words, not the user's — prove you understood, don't parrot
- Include the WHY (intent) not just the WHAT (task)
- Note scope if the user implied it ("just for the current goal, not changing the harness")

---

## Phase 2: SURFACE (Hybrid Assumption Audit)

Surface assumptions from BOTH sides before asking questions. This is where the highest value lives — small tasks fail most often because of unstated assumptions.

<mandatory_read phase="surface">
Before surfacing assumptions, review your reasoning against:
- [AssumptionAudit.md](../AssumptionAudit.md) — The Three Questions and Common Traps

Focus on: "Am I assuming or did the user say this?" and "What is the user assuming without realizing it?"
</mandatory_read>

### Step A — Brief Audit Block

State your assumptions AND surface what the user appears to assume.

**Format:**
```
I'm assuming:
  • [assumption about tech/approach]
  • [assumption about scope/requirements]

You appear to assume:
  • [implicit belief in their request]
  • [unstated expectation]
```

### Step B — Embedded in Questions

Remaining assumptions woven into probe questions naturally in Phase 3: "I'm assuming X — is that right?" This hybrid ensures assumptions are VISIBLE (audit block) and ACTIONABLE (resolved through questions).

**The two most dangerous assumption traps for small tasks:**
1. **"Standard Approach" trap** — Claude defaults to the common pattern without checking if it fits THIS codebase/context
2. **"Obvious Default" trap** — Claude fills in "obvious" choices (the default tool, structure, format) without checking if the user intended something different

---

## Phase 3: PROBE

<mandatory_read phase="probe">
**Read before asking questions:**
- [QuestionGuidelines.md](../QuestionGuidelines.md) — Question quality rules, what to ask vs avoid

Every question must earn its place. If the answer wouldn't change what you build, don't ask it.
</mandatory_read>

Use `AskUserQuestion` with 2-4 questions per round.

### Question Quality Rules

- **Earn your place** — Could I answer this myself through research? Does the answer change the outcome? If no to both, don't ask it.
- **No canned questions** — Specific to THIS situation, not templates
- **Include the non-obvious** — At least one question the user wouldn't think to ask themselves
- **Reference context** — Codebase findings, domain knowledge, or research in questions
- **Embed remaining assumptions** — "I'm assuming X — is that right?" resolves assumptions AND gathers information

### Convergence Signals (when to stop)

- No new ambiguities emerged in last round
- You could proceed without guessing on any aspect
- User's answers are getting shorter and confirmatory
- All key assumptions from the audit block have been addressed

**Hard cap:** 3 rounds maximum. If still unclear after 3 rounds, escalate to a full Interview workflow — this task is bigger than it seemed.

### Background Research

You MAY launch background research agents during probing — non-blocking only. Surface findings asynchronously: "While you answered, I found that..."

Do NOT block the conversation waiting for research. The user's answers are the primary source of truth for small tasks.

### Showpiece Questions

You may use ONE markdown-preview Showpiece question per QuickClarify session, for structural forks where text is ambiguous about the shape of the solution. See QuestionGuidelines.md for the technique. Max 1 — this is a quick flow.

---

## Phase 4: CONVERGE

Deliver an inline summary of the aligned understanding. NOT a spec file — the conversation IS the artifact.

**Format:**
```markdown
## Aligned Understanding

**Task:** [one-sentence description]
**Key decisions:**
  • [decision 1 from Q&A]
  • [decision 2 from Q&A]

**Assumptions confirmed:**
  • [confirmed assumption]

**Assumptions corrected:**
  • [what changed and why]

**Scope boundaries:**
  • In: [what's included]
  • Out: [what's excluded]

**Ready to proceed.**
```

This becomes your reference for implementation. If a question arises during implementation, check the Aligned Understanding first — the answer may already be there.

---

## Behavioral Norms

### Anti-Sycophancy (Compressed)

QuickClarify skips formal Devil's Advocate, but that doesn't mean you agree with everything. If you see a problem with the approach during probing, say so directly in your questions: "Have you considered that X might cause Y?" Challenge is embedded, not absent.

### Question Guidelines Apply

Read QuestionGuidelines.md. The same principles that make full Interview questions good apply here:
- No obvious questions (things you could find yourself)
- No generic questions (could apply to any project)
- No agreement-seeking (questions designed to confirm what you think)
- Quote user's input to prove you read it

### Information-Maximizing Questions

Each question should maximize information gain — the best question is one where DIFFERENT answers lead to DIFFERENT implementations. If all possible answers lead to the same outcome, the question wastes time.

---

## Degrees of Freedom

| Component | Freedom | Notes |
|-----------|---------|-------|
| Phase ordering | **None** | Mirror → Surface → Probe → Converge is fixed |
| Number of Q&A rounds | **High** | 1-3, convergence-signal driven |
| Question content | **High** | Specific to THIS situation |
| Background research | **Medium** | Optional, non-blocking only |
| Output format | **Low** | Must follow Converge template |
| Showpiece questions | **Low** | Max 1 per session |

---

## Example: Quick Interview in Action

**User:** "I want to add a replay buffer to my sentiment experiments to prevent catastrophic forgetting"

### MIRROR
> Here's what I understand:
> - You want to mix general instruction-following data into training alongside your sentiment data
> - The goal is to prevent the model from losing general capabilities while specializing on sentiment
> - This is for the existing `autofinetune/sentiment-4b` goal, not a new goal

### SURFACE
> I'm assuming:
> - You want to use the `replay_dataset` / `replay_ratio` fields already in config.py — not a custom mixing approach
> - You have or can find a suitable general instruction dataset (e.g., a slice of OpenHermes or similar)
>
> You appear to assume:
> - Forgetting is actually happening — have you compared the fine-tuned model's general performance to the base model?
> - A replay buffer will help more than other approaches (e.g., lower learning rate, fewer epochs)

### PROBE (Round 1)
> Q1: "Have you actually measured forgetting? If your sentiment model can't follow basic non-sentiment instructions anymore, replay is the right fix. But if it's just slightly worse on general chat, a lower learning rate in the next experiment might be simpler."
> Q2: "What general data do you have access to? The format needs to match — if your sentiment data is chat format, the replay data should be too. Do you have a `.jsonl` file ready, or do we need to prepare one?"
> Q3: "What replay ratio are you thinking? 10% is a common starting point, but with only 500 sentiment examples, even 10% means just 50 replay samples — which may not be enough to preserve general capabilities."

*[User answers: yes, general performance tanked after epoch 3; has an OpenHermes subset in chat format; was thinking 10% but open to more]*

### CONVERGE
> ## Aligned Understanding
>
> **Task:** Add replay buffer to sentiment-4b experiments to prevent catastrophic forgetting
> **Key decisions:**
> - Use `replay_dataset` field in config.py pointing to `~/data/openhermes_chat.jsonl`
> - Start at 20% ratio (given small sentiment dataset, 10% too few replay samples)
> - The agent will experiment with ratio as another knob (10%, 20%, 30%)
>
> **Assumptions confirmed:**
> - Forgetting is real — general performance drops after epoch 3
> - Replay data is already in chat format, compatible with the training harness
>
> **Assumptions corrected:**
> - 10% is too low given dataset size — starting at 20% instead
>
> **Scope boundaries:**
> - In: Add replay_dataset path and replay_ratio to config.py, add ratio exploration to goal.md research directions
> - Out: Not changing the training harness, not switching to a different forgetting mitigation approach
>
> **Ready to proceed.**
