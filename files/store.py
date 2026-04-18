"""
Simple in-memory store for anonymous reports (session-scoped).
In production this would be a database.
"""

from datetime import datetime
from models import AnonymousReport
import threading

_lock = threading.Lock()
_reports: list[AnonymousReport] = []


def add_report(report: AnonymousReport) -> None:
    with _lock:
        _reports.insert(0, report)


def get_all_reports() -> list[AnonymousReport]:
    with _lock:
        return list(_reports)


def get_report_by_id(report_id: str) -> AnonymousReport | None:
    with _lock:
        return next((r for r in _reports if r.id == report_id), None)


def get_stats() -> dict:
    with _lock:
        reports = list(_reports)

    if not reports:
        return {"total": 0}

    from collections import Counter
    classified = [r for r in reports if r.classification]
    type_counts = Counter(r.classification.conflict_type.value for r in classified)
    urgency_counts = Counter(r.classification.urgency.value for r in classified)
    critical = sum(1 for r in classified if r.classification.requires_immediate_action)

    return {
        "total": len(reports),
        "classified": len(classified),
        "critical": critical,
        "by_type": dict(type_counts),
        "by_urgency": dict(urgency_counts),
        "recent": reports[:5],
    }
