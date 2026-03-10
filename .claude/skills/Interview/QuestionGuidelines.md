# Question Guidelines

How to ask questions that surface real insights, not just fill time.

---

## Core Principles

### Think Deeply About THIS Situation

Don't use canned questions. Formulate questions based on:

- What you learned from the user's input
- What you discovered in codebase research
- What assumptions seem shaky
- What could go wrong with THIS specific idea

### Every Question Should Earn Its Place

Before asking, consider:
- Could I answer this myself through research?
- Does this question surface something non-obvious?
- Will the answer change how we build this?

If no to all three → Don't ask it.

---

## What To Do

### Be Challenging

Disagreement is more valuable than agreement. Don't ask questions just to confirm - ask to probe.

```
❌ "So you want to use Qwen3-4B for this, right?"
✅ "Why 4B specifically? Your task is classification with short outputs — have you considered 0.6B? It trains 4x faster and you'd get more experiments per hour."
```

### Quote the Spec/Input

Reference specific parts to prove you read it carefully.

```
✅ "You mentioned 'handling edge cases gracefully' - what does graceful mean here? Silent failure? User notification? Retry?"
```

### Flag Training Assumptions

Be explicit when you're working from general knowledge vs. verified facts.

```
✅ "I'm assuming X based on common patterns - is this correct for your codebase, or do you do it differently?"
```

### Ask Failure Questions

Focus on what could go wrong, not just what should happen.

```
✅ "What would make this fail?"
✅ "How could this break in production?"
✅ "What's the worst case if this doesn't work?"
```

### Surface Uncertainties

State clearly what you don't know.

```
✅ "I'm not sure how this interacts with [system] - can you clarify?"
✅ "I couldn't determine from the codebase whether [X] - what's the current behavior?"
```

### Use Codebase Findings

Incorporate what you discovered in research.

```
✅ "I noticed your project uses [pattern] in [location] - does that apply here?"
✅ "Your codebase has [existing component] - should this integrate with it or be separate?"
```

### Probe Assumptions

Challenge both user's assumptions AND your own.

```
✅ "You seem to be assuming [X] - is that definitely true?"
✅ "I was assuming [Y] but now I'm not sure - can we verify?"
```

---

## What To Avoid

### Obvious Questions

Don't ask what you could find yourself.

```
❌ "What files exist in your project?"
❌ "What framework are you using?"
→ Research this before asking
```

### Generic Questions

Don't use templates that could apply to any project.

```
❌ "What are your requirements?"
❌ "How should this work?"
→ Be specific to THIS situation
```

### Assumption-Based Questions

Don't assume from training data without flagging it.

```
❌ "Since you're doing classification, you'll want thinking mode off..."
✅ "I'm assuming thinking mode should be off since this is classification — but some classification tasks benefit from chain-of-thought. Does yours?"
```

### Agreement-Seeking Questions

Don't ask just to confirm what you think you know.

```
❌ "So this should be pretty straightforward, right?"
✅ "What's the non-obvious complexity here that I might be missing?"
```

### Filler Questions

Don't pad the interview with low-value questions.

```
❌ "Is there anything else you want to add?"
✅ [Specific follow-up based on what they said]
```

---

## Question Themes

Cover these areas, but craft SPECIFIC questions for THIS project:

### Alternatives & Tradeoff Analysis

When multiple valid approaches exist, don't just ask "which do you prefer?" — lay out the tradeoffs BEFORE asking. The user can't choose well without seeing what they're trading.

**Tradeoff presentation protocol:**

1. **Name the options** — Give each approach a short, descriptive label
2. **State the tradeoff axis** — What dimension separates the options? (complexity vs. flexibility, speed vs. correctness, upfront cost vs. maintenance cost, etc.)
3. **Be concrete about costs** — "More complex" is useless. "Adds ~200 lines of config and a migration step" is useful. Quantify when possible.
4. **Show who pays** — Every tradeoff has a payer. "Simpler now but ops team maintains the workaround" is different from "simpler now, no downstream cost."
5. **State your lean** — After presenting options fairly, say which you'd pick and why. Don't hide behind false neutrality.

**When to surface tradeoffs:**
- Any Tier 1 decision (architecture, framework, major design choice)
- When the user's stated preference has a non-obvious cost
- When two options both honor constraints but differ meaningfully
- When rejecting an alternative — explain what's being given up

**Key questions:**
- What are you trading away with this approach?
- Why this approach over [specific alternative given your constraints]?
- What did you consider and reject? (surfaces hidden tradeoff analysis the user already did)

### Failure Modes
- How could this break?
- What makes this fail?
- What's the blast radius if it goes wrong?

### Success Criteria
- How do you know it worked?
- What does "done" look like?
- How will you test this?

### Edge Cases
- What happens when [unusual input]?
- How does this behave under [stress condition]?
- What if [dependency] is unavailable?

### Integration
- How does this interact with [existing system]?
- What needs to change elsewhere?
- Who/what else is affected?

---

## Asking Pattern

Use `AskUserQuestion` tool. Up to 4 questions at a time.

### Question Cadence

| Mode | Questions | When | Format |
|------|-----------|------|--------|
| **Standard** | 2-4 | Normal probing, exploring options | Multiple questions, text descriptions |
| **Showpiece** | 1 | Critical structural fork where text is ambiguous | Single question with `markdown` previews showing each option visually |

### Field Usage

| Field | Guidance |
|-------|----------|
| `label` | 1-5 words. The option name the user clicks. |
| `description` | 1-2 sentences. State the benefit or implication of this choice. |
| `header` | Max 12 chars. Short chip label for the question. Examples: "Architecture", "Database", "Auth Model", "Scope". |
| `markdown` | Monospace preview for structural options (Showpiece only). Show ASCII trees, schemas, file layouts. 8-20 lines sweet spot. |

### Phase-Level Cadence

**Early probing:**
- Focus on: Viability, alternatives, failure modes
- Tone: Probing, direct
- Goal: Validate the approach makes sense

**Deep probing:**
- Focus on: Implementation details, edge cases, integration
- Tone: Thorough, collaborative
- Goal: Capture everything needed to proceed

**Late probing:**
- Focus on: Verification, gaps, open questions
- Tone: Confirmatory but thorough
- Goal: Ensure nothing is missing

---

## Convergence

As the interview progresses, questions should converge:

**Convergence signals** (you're ready for output):
- No new constraints emerged in the last 2 Q&A rounds
- You could write the spec without guessing on any section
- User's answers are getting shorter and more confirmatory
- All key assumptions have been addressed

**Late interview behavior:**
- Fewer questions (2-3, not 4)
- Questions are more specific (refinement, not exploration)
- If you're still generating many broad questions late in the interview, something went wrong earlier
