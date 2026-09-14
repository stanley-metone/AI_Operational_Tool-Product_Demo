# week10_ops_tool

A lightweight operations automation tool that validates daily ticket/incident data and generates an exception report for supervisors.

## Operational problem

Operations teams often spend time manually checking spreadsheets for:

- duplicate IDs;
- missing ownership/customer fields;
- invalid statuses or priorities;
- tickets closed with bad timestamps;
- SLA breaches and open tickets already beyond SLA.

`week10_ops_tool` automates those checks and produces management-ready outputs in one command.

## What the tool generates

Running the tool creates:

- `output/validated_ops.csv` — every source record plus validation fields;
- `output/anomalies.csv` — only records that need attention;
- `output/daily_ops_report.md` — a concise management summary.

## Setup

Requires Python 3.10+.

```bash
git clone <YOUR_GITHUB_REPO_URL>
cd week10_ops_tool

python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

On Windows, you can also copy `.env.example` to `.env` manually.

## Run the demo

```bash
python main.py
```

Expected console output:

```text
week10_ops_tool completed successfully
Records processed: 12
...
```

Then open:

```text
output/daily_ops_report.md
output/anomalies.csv
```

## Run with your own operations CSV

```bash
python main.py --input path/to/your_file.csv --output output
```

Required columns:

```text
record_id,team,owner,status,opened_at,closed_at,priority,customer_id
```

Accepted statuses:

```text
Open, In Progress, Closed
```

Accepted priorities:

```text
P1, P2, P3, P4
```

Timestamps should be ISO-8601, for example:

```text
2026-09-14T08:00:00Z
```

## Security

No API key or secret is hardcoded.

- `.env` is excluded by `.gitignore`.
- `.env.example` contains only safe configuration placeholders.
- This project does not require an external AI API at runtime.

## Vibe Coding / AI-assisted development

The project was designed and iterated primarily with AI assistance. See [`PROMPTS.md`](PROMPTS.md) for representative prompts used for planning, coding, debugging, documentation, and demo preparation.

## Suggested demo flow

1. Open `data/sample_ops.csv` and point out messy records.
2. Run `python main.py`.
3. Open `output/anomalies.csv` to show the flagged rows.
4. Open `output/daily_ops_report.md` to show the management summary.
5. Explain how the workflow replaces repetitive spreadsheet checking.
