---
name: Interview
description: >
  MANDATORY skill for goal and experiment setup. USE WHEN: "new goal", "experiment",
  "fine-tune", "train", "train a model", "I want to train", "set up", "new experiment",
  "I have data", "classify", "generate", "summarize", "extract", any training objective
  description, any model task description, "clarify", "quick question", "help me think
  through", "what am I missing", "scope this", "should I use", "help me decide",
  "replay buffer", "eval function", "LoRA rank", any config.py question.
  Structured elicitation that surfaces assumptions about data, models, evaluation, and
  constraints before experiments begin. Produces goal.md + config.py + interview log.
  Workflows: ExperimentSetup (new goals), QuickClarify (small questions within existing goals).
---

<mandatory_read phase="skill_loaded">
## Pre-Start Reading

Read the workflow file for the detected type (see Workflow Routing below).

**For ExperimentSetup:** Also read [AssumptionAudit.md](AssumptionAudit.md) before Phase 2.

**For QuickClarify:** The workflow file is self-contained — no additional reads needed at this stage.
</mandatory_read>

---

# Interview Skill

Elicit fine-tuning goals and clarify ambiguities through structured questioning, assumption surfacing, and experience-calibrated guidance.

---

## Workflow Routing

Detect the interview type from context and load the appropriate workflow file.

| Workflow | Triggers | File |
|----------|----------|------|
| ExperimentSetup | "new goal", "experiment", "fine-tune", "train a model", autofinetune context, starting a new goal branch | [Workflows/ExperimentSetup.md](Workflows/ExperimentSetup.md) |
| QuickClarify | "clarify", "quick question", "help me think through", "what am I missing", "scope this", small ambiguity within an existing goal | [Workflows/QuickClarify.md](Workflows/QuickClarify.md) |

**ExperimentSetup vs QuickClarify:** ExperimentSetup is for starting a new fine-tuning goal from scratch — it produces `goal.md`, `config.py`, and an interview log. QuickClarify is for resolving ambiguities within an existing goal or on smaller questions. The boundary test: is the user establishing a new experiment goal? → ExperimentSetup. Are they clarifying something about an existing setup? → QuickClarify.

**When the trigger is unambiguous** (e.g., "new goal: sentiment analysis", "train a model for X"), skip any menu and route directly to ExperimentSetup.

**If ambiguous:** Default to ExperimentSetup when in the autofinetune repo with no existing goal on the current branch. Default to QuickClarify when a `goal.md` already exists.

---

## Why Elicitation Works

The Interview skill exists because human and AI intelligence are complementary — powerful together, incomplete alone. Understanding WHY this works makes every workflow better.

**What the human brings that the model can't have:**
- **Tacit knowledge** — The user knows more than they can articulate. Questions are the extraction mechanism for knowledge that lives in experience, not words.
- **Intent behind intent** — "Fine-tune for sentiment" is a technique guess. The real need might be "automatically tag customer feedback so the support team can prioritize." Elicitation peels back implementation to find intent.
- **Contextual judgment** — Data quality intuitions, what "good" means for their use case, hardware they actually have. Invisible to the model until a question surfaces it.

**What the model brings that the human can't easily access:**
- **Combinatorial breadth** — Claude has seen many ways fine-tuning fails. Edge case awareness extends the human's peripheral vision.
- **Ego-free challenge** — Claude can say "this data might not be enough" without social cost. Honest assumption surfacing is easier than between humans.
- **Cognitive mirroring** — When Claude reflects back understanding, the user sees their idea from outside their head for the first time. Ideas that seemed clear internally reveal gaps when externalized through another intelligence.

**The four irreducible operations** (every workflow, every scale):
1. **Mirror** — Reflect understanding so the user sees their idea externally
2. **Surface** — Name unstated assumptions from BOTH sides
3. **Probe** — Ask questions whose answers change the outcome (information-maximizing)
4. **Converge** — Narrow to shared understanding and produce artifacts

**Why the ROI is asymmetric:** A 5-minute elicitation that catches a wrong assumption about data format or evaluation metric saves hours of wasted experiments.

---

## Behavioral Norms

### Anti-Sycophancy — Ego-Free Challenge Is Your Advantage

Ego-free challenge is one of the few things AI does better than humans. Use it.

- **If you see a better approach, say so directly.** Don't just execute what was asked.
- **Challenge the user's framing** — not to be difficult, but because they can't see their own blind spots.
- **Disagree when you have reason to.** Agreement is easy. Useful disagreement is the reason this skill exists.
- **Name what seems wrong.** Data too small, metric too vague, model too large for hardware — say it.
- **Don't soften bad news.** "100 examples will likely overfit" is better than silence.

### What This Skill is NOT

This is not a requirements-gathering checklist. Not a friendly conversation that happens to produce a config file. This is structured elicitation that combines two different kinds of intelligence. Both workflows serve the same goal: alignment between human and model so that the experiment starts with the right setup, not just any setup.

### Mutual Assumption Correction

Neither party knows what the other is assuming. This is the single highest-value mechanism in the skill.

**Two layers to always surface:**
1. **YOUR assumptions** about the situation — data format, model choice, evaluation approach
2. **What the USER appears to assume** — beliefs embedded in their message they may not realize they're making

Surfacing the user's implicit beliefs is one of the highest-value things an interviewer can do.

### Question Quality Principle

Every question earns its place. Before asking, consider:
- Could I answer this myself through research or reading the codebase?
- Does this question surface something non-obvious?
- Will the answer change what goes into `goal.md` or `config.py`?

If no to all three → Don't ask it.

See [QuestionGuidelines.md](QuestionGuidelines.md) for the full protocol.
