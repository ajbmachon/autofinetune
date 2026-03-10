# autofinetune

Autonomous LoRA fine-tuning workbench. The autoresearch pattern adapted for LoRA fine-tuning with Unsloth.

## MANDATORY: New Goals, Tasks, and Experiments

**When the user describes a new goal, experiment, training task, or asks to fine-tune anything:**

1. **STOP.** Do not start writing `goal.md` or `config.py` directly.
2. **Load the Interview skill** using the Skill tool (`skill: "Interview"`).
3. **Read the full skill and the routed workflow file** before taking any action.
4. **Follow the ExperimentSetup workflow** — it produces `goal.md`, `config.py`, and an interview log through structured elicitation.

This applies to ANY of these triggers: "new goal", "train a model", "fine-tune", "new experiment", "I want to train...", "set up an experiment", "I have data for...", or any description of a training objective.

**Do NOT skip the interview.** The 5-10 minutes of elicitation catches wrong assumptions about data, evaluation, and constraints that would otherwise waste hours of experiment time.

For quick clarifications within an existing goal (e.g., "should I try rank 32?", "help me think through my eval function"), load the Interview skill and use the QuickClarify workflow instead.

## Running Experiments

Read `program.md` — it has the complete autonomous experiment loop. The short version: edit `config.py`, commit, train, measure, keep or discard, repeat forever.

## Key Files

- `program.md` — agent loop instructions (read this first for any experiment work)
- `goal.md` — per-branch goal definition (objective, data, metrics, constraints)
- `config.py` — the only file edited during experiments
- `train.py` + `prepare.py` — fixed infrastructure, never modify

## Development Principles

- Do not embed prescriptive experiment design assumptions in code or documentation. The agent discovers what works through experimentation.
- Keep the file count minimal — simplicity is the feature. The agent needs to understand the entire codebase.
- `config.py` is Python intentionally — the agent can define eval functions and data formatters inline.

## Commands

- `uv run train.py` — run a training experiment (redirect output: `> run.log 2>&1`)
- `uv run prepare.py --verify` — check model name and data files exist
- `uv run prepare.py --merge <adapter_path> --output <output_path>` — merge LoRA adapter into base model for deployment
