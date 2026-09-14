from __future__ import annotations

import csv
import os
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv


REQUIRED_COLUMNS = [
    "record_id",
    "team",
    "owner",
    "status",
    "opened_at",
    "closed_at",
    "priority",
    "customer_id",
]

VALID_STATUSES = {"Open", "In Progress", "Closed"}
VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}


@dataclass
class Config:
    input_csv: Path
    output_dir: Path
    sla_hours: Dict[str, float]


def parse_iso(value: str) -> Optional[datetime]:
    """Parse an ISO-8601 timestamp. Empty values return None."""
    value = (value or "").strip()
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_config(input_override: Optional[str] = None, output_override: Optional[str] = None) -> Config:
    load_dotenv()

    input_csv = Path(input_override or os.getenv("INPUT_CSV", "data/sample_ops.csv"))
    output_dir = Path(output_override or os.getenv("OUTPUT_DIR", "output"))
    sla_hours = {
        "P1": float(os.getenv("SLA_P1_HOURS", "4")),
        "P2": float(os.getenv("SLA_P2_HOURS", "8")),
        "P3": float(os.getenv("SLA_P3_HOURS", "24")),
        "P4": float(os.getenv("SLA_P4_HOURS", "48")),
    }
    return Config(input_csv=input_csv, output_dir=output_dir, sla_hours=sla_hours)


def read_rows(path: Path) -> Tuple[List[dict], List[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        missing = [c for c in REQUIRED_COLUMNS if c not in fieldnames]
        if missing:
            raise ValueError("Missing required columns: " + ", ".join(missing))
        return list(reader), fieldnames


def validate_rows(rows: List[dict], sla_hours: Dict[str, float], now: Optional[datetime] = None) -> List[dict]:
    now = now or datetime.now(timezone.utc)
    id_counts = Counter((r.get("record_id") or "").strip() for r in rows if (r.get("record_id") or "").strip())

    results = []
    for row in rows:
        result = dict(row)
        issues: List[str] = []

        record_id = (row.get("record_id") or "").strip()
        status = (row.get("status") or "").strip()
        priority = (row.get("priority") or "").strip()

        # Required-field checks.
        for col in ["record_id", "team", "owner", "status", "opened_at", "priority", "customer_id"]:
            if not (row.get(col) or "").strip():
                issues.append(f"missing_{col}")

        if record_id and id_counts[record_id] > 1:
            issues.append("duplicate_record_id")

        if status and status not in VALID_STATUSES:
            issues.append("invalid_status")

        if priority and priority not in VALID_PRIORITIES:
            issues.append("invalid_priority")

        opened_at = None
        closed_at = None
        try:
            opened_at = parse_iso(row.get("opened_at", ""))
        except ValueError:
            issues.append("invalid_opened_at")

        try:
            closed_at = parse_iso(row.get("closed_at", ""))
        except ValueError:
            issues.append("invalid_closed_at")

        if status == "Closed" and not closed_at:
            issues.append("closed_ticket_missing_closed_at")

        if status != "Closed" and closed_at:
            issues.append("nonclosed_ticket_has_closed_at")

        resolution_hours = ""
        ticket_age_hours = ""
        sla_threshold = sla_hours.get(priority)
        sla_breach = False

        if opened_at and closed_at:
            delta = (closed_at - opened_at).total_seconds() / 3600
            resolution_hours = round(delta, 2)
            if delta < 0:
                issues.append("closed_before_opened")
            elif sla_threshold is not None and delta > sla_threshold:
                sla_breach = True
                issues.append("sla_breach")

        elif opened_at and status != "Closed":
            delta = (now - opened_at).total_seconds() / 3600
            ticket_age_hours = round(delta, 2)
            if delta < 0:
                issues.append("opened_at_in_future")
            elif sla_threshold is not None and delta > sla_threshold:
                sla_breach = True
                issues.append("open_ticket_over_sla")

        result["resolution_hours"] = resolution_hours
        result["ticket_age_hours"] = ticket_age_hours
        result["sla_hours"] = sla_threshold if sla_threshold is not None else ""
        result["sla_breach"] = "YES" if sla_breach else "NO"
        result["issue_count"] = len(issues)
        result["issues"] = ";".join(issues)
        result["validation_status"] = "FAIL" if issues else "PASS"
        results.append(result)

    return results


def write_csv(path: Path, rows: List[dict], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_report(rows: List[dict], input_name: str, generated_at: datetime) -> str:
    total = len(rows)
    failed = [r for r in rows if r["validation_status"] == "FAIL"]
    passed = total - len(failed)
    sla_breaches = [r for r in rows if r["sla_breach"] == "YES"]

    status_counts = Counter((r.get("status") or "Blank").strip() or "Blank" for r in rows)
    priority_counts = Counter((r.get("priority") or "Blank").strip() or "Blank" for r in rows)
    team_counts = Counter((r.get("team") or "Blank").strip() or "Blank" for r in rows)

    issue_counter = Counter()
    for r in failed:
        for issue in (r.get("issues") or "").split(";"):
            if issue:
                issue_counter[issue] += 1

    lines = [
        "# Daily Operations Quality Report",
        "",
        f"**Generated:** {generated_at.astimezone(timezone.utc).isoformat()}",
        f"**Source file:** `{input_name}`",
        "",
        "## Executive Summary",
        "",
        f"- Records processed: **{total}**",
        f"- Validation passed: **{passed}**",
        f"- Records needing attention: **{len(failed)}**",
        f"- SLA breaches / overdue items: **{len(sla_breaches)}**",
        "",
        "## Status Breakdown",
        "",
    ]
    for key, value in sorted(status_counts.items()):
        lines.append(f"- {key}: {value}")

    lines += ["", "## Priority Breakdown", ""]
    for key, value in sorted(priority_counts.items()):
        lines.append(f"- {key}: {value}")

    lines += ["", "## Team Workload", ""]
    for key, value in sorted(team_counts.items()):
        lines.append(f"- {key}: {value}")

    lines += ["", "## Most Common Data / Process Issues", ""]
    if issue_counter:
        for issue, count in issue_counter.most_common():
            lines.append(f"- `{issue}`: {count}")
    else:
        lines.append("- No validation issues found.")

    lines += [
        "",
        "## Recommended Actions",
        "",
    ]
    if sla_breaches:
        lines.append("- Prioritize records flagged with `sla_breach` or `open_ticket_over_sla`.")
    if any("duplicate_record_id" in (r.get("issues") or "") for r in rows):
        lines.append("- Investigate duplicate record IDs before downstream reporting.")
    if any("missing_" in (r.get("issues") or "") for r in rows):
        lines.append("- Complete missing operational fields so ownership and customer impact remain traceable.")
    if not failed:
        lines.append("- No immediate data-quality actions required.")

    lines += [
        "",
        "_Generated automatically by `week10_ops_tool`._",
        "",
    ]
    return "\n".join(lines)


def run(input_path: Path, output_dir: Path, sla_hours: Dict[str, float]) -> dict:
    rows, original_fields = read_rows(input_path)
    processed = validate_rows(rows, sla_hours)

    output_dir.mkdir(parents=True, exist_ok=True)
    extra_fields = [
        "resolution_hours",
        "ticket_age_hours",
        "sla_hours",
        "sla_breach",
        "issue_count",
        "issues",
        "validation_status",
    ]
    all_fields = original_fields + [f for f in extra_fields if f not in original_fields]

    validated_path = output_dir / "validated_ops.csv"
    anomalies_path = output_dir / "anomalies.csv"
    report_path = output_dir / "daily_ops_report.md"

    write_csv(validated_path, processed, all_fields)
    write_csv(anomalies_path, [r for r in processed if r["validation_status"] == "FAIL"], all_fields)

    generated_at = datetime.now(timezone.utc)
    report = build_report(processed, input_path.name, generated_at)
    report_path.write_text(report, encoding="utf-8")

    return {
        "processed": len(processed),
        "failed": sum(1 for r in processed if r["validation_status"] == "FAIL"),
        "sla_breaches": sum(1 for r in processed if r["sla_breach"] == "YES"),
        "validated_path": str(validated_path),
        "anomalies_path": str(anomalies_path),
        "report_path": str(report_path),
    }
