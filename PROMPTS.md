# PROMPTS.md — Vibe Coding Log

This file is a **prompt-log starter** containing the key prompts that drove the design of `week10_ops_tool` in this working session.

> Before submission, keep only prompts that truthfully match your own AI-assisted workflow. If your rubric specifically requires Claude, Copilot, or Cursor, run the relevant prompts in that assistant, make at least one resulting repository change, and record the exact prompt here.

## 1. Problem framing

Prompt

> I need a Week 10 operations coding project that solves a repetitive business problem, runs locally without paid APIs, is easy to demo in three minutes, and demonstrates AI-assisted development. Propose a simple Python automation tool with measurable operational value, clear inputs/outputs, and no hardcoded secrets.

Useful AI output

The assistant recommended a daily operations data-quality and SLA checker because it is easy to demonstrate, has clear business value, and can run fully offline.

## 2. Architecture

Prompt

> Design the smallest reliable architecture for a Python CLI tool named `week10_ops_tool`. It should read a CSV of operational tickets, validate required fields, detect duplicate IDs, calculate resolution time, flag SLA breaches by priority, and generate both an exception CSV and a management-friendly Markdown report. Keep dependencies minimal.

Useful AI output

The assistant proposed:
- `main.py` for CLI execution;
- `ops_tool.py` for validation/reporting logic;
- `.env` configuration for paths and SLA thresholds;
- sample data and tests.

## 3. Core implementation

Prompt

> Generate production-readable Python 3.10+ code for the tool. Use the standard `csv` module plus `python-dotenv`. Required columns are record_id, team, owner, status, opened_at, closed_at, priority, customer_id. Valid priorities are P1-P4. SLA thresholds should come from environment variables. Return a non-zero exit code only for fatal input/schema errors, not for normal business exceptions.

Useful AI output

The assistant generated the validation pipeline, ISO timestamp parsing, SLA calculations, exception flags, CSV exports, and Markdown summary.

## 4. Security review

Prompt

> Review this repository for beginner security mistakes. Make sure secrets are not hardcoded, `.env` is ignored, `.env.example` is safe to commit, and the README does not tell users to commit credentials.

Useful AI output

The assistant confirmed that the project needs no runtime secrets and recommended committing only `.env.example`.

## 5. Edge-case debugging

Prompt

> Review the validator for edge cases: blank fields, duplicate IDs, invalid timestamps, closed tickets without closed_at, non-closed tickets with closed_at, negative resolution duration, unsupported priorities/statuses, and future timestamps. Suggest fixes and add tests.

Useful AI output

The assistant added explicit issue codes and test coverage for common failure modes.

## 6. Documentation

Prompt

> Write a concise README for a student GitHub submission. Include the operational problem, setup, run commands, expected outputs, security approach, required CSV schema, and a three-minute demo flow.

Useful AI output

The assistant produced the repository documentation and demo sequence.

## 7. Product demo preparation

Prompt

> Create a 3-minute product demo outline with a hook, screen-share flow, quantified value statement, and organizational call to action for this operations data quality/SLA automation tool. Keep the claims defensible.

Useful AI output

The assistant recommended showing the messy CSV, running one command, opening the exception file, and ending on the management report.

## 8. Capstone integration reflection

Prompt

> Draft a short Week 10 capstone update answering: how AI accelerated development, what vibe-coded feature I built, one prompting challenge, and how I fixed it. Write in first person and keep it specific to this operations validation tool.

Useful AI output

The assistant created the first draft in `capstone_week10_update.md`.
