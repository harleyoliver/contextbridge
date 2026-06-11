"""
Mock enterprise HTTP data sources.
Simulates the REST API responses from CRM, ticketing, and HR systems.
"""
from datetime import datetime, timezone, timedelta
import random
from typing import Any

# Seeded so results are deterministic — same data every run
_rng = random.Random(42)


def _ts(days_ago: int = 0) -> str:
    dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return dt.isoformat()


# ── CRM ──────────────────────────────────────────────────────────────────────

_FIRST = ["Liam","Olivia","Noah","Emma","James","Ava","William","Sophia","Benjamin","Isabella"]
_LAST  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Wilson","Moore"]
_ORGS  = ["Acme Corp","Globex","Initech","Umbrella Ltd","Stark Industries","Wayne Enterprises"]
_PLANS = ["starter", "growth", "enterprise"]

def get_crm_contacts(limit: int = 30) -> list[dict[str, Any]]:
    """Simulates GET /api/contacts from a CRM system."""
    contacts = []
    for i in range(1, limit + 1):
        first = _rng.choice(_FIRST)
        last  = _rng.choice(_LAST)
        contacts.append({
            "id": f"crm_{i:04d}",
            "first_name": first,
            "last_name": last,
            "email": f"{first.lower()}.{last.lower()}@{_rng.choice(_ORGS).lower().replace(' ', '')}.com",
            "organisation": _rng.choice(_ORGS),
            "plan": _rng.choice(_PLANS),
            "mrr_aud": _rng.randint(0, 5000),
            "created_at": _ts(_rng.randint(30, 730)),
            "last_activity": _ts(_rng.randint(0, 30)),
        })
    return contacts


# ── Ticketing ────────────────────────────────────────────────────────────────

_SUBJECTS = [
    "Cannot log in after password reset",
    "API rate limit hit unexpectedly",
    "Export to CSV not working",
    "Dashboard loads slowly with large datasets",
    "Webhook not firing on update events",
    "SSO integration broken after Azure AD change",
    "Billing invoice shows incorrect amount",
    "Mobile app crashes on iOS 17",
]
_STATUSES  = ["open", "in_progress", "resolved", "closed"]
_PRIORITIES = ["low", "medium", "high", "critical"]

def get_support_tickets(limit: int = 40) -> list[dict[str, Any]]:
    """Simulates GET /api/tickets from a support ticketing system."""
    tickets = []
    for i in range(1, limit + 1):
        status = _rng.choice(_STATUSES)
        tickets.append({
            "id": f"tkt_{i:04d}",
            "subject": _rng.choice(_SUBJECTS),
            "status": status,
            "priority": _rng.choice(_PRIORITIES),
            "assignee": f"{_rng.choice(_FIRST)} {_rng.choice(_LAST)}",
            "customer_id": f"crm_{_rng.randint(1, 30):04d}",
            "created_at": _ts(_rng.randint(0, 90)),
            "resolved_at": _ts(_rng.randint(0, 5)) if status == "resolved" else None,
            "sla_breached": _rng.random() < 0.15,
        })
    return tickets


# ── HR ───────────────────────────────────────────────────────────────────────

_DEPARTMENTS = ["Engineering", "Product", "Design", "Sales", "Customer Success", "Finance", "People & Culture"]
_LEVELS      = ["IC1", "IC2", "IC3", "IC4", "Staff", "Principal", "Director"]

def get_hr_employees(limit: int = 25) -> list[dict[str, Any]]:
    """Simulates GET /api/employees from an HR system."""
    employees = []
    for i in range(1, limit + 1):
        dept = _rng.choice(_DEPARTMENTS)
        employees.append({
            "id": f"emp_{i:04d}",
            "first_name": _rng.choice(_FIRST),
            "last_name": _rng.choice(_LAST),
            "department": dept,
            "level": _rng.choice(_LEVELS),
            "location": _rng.choice(["Melbourne", "Sydney", "Remote", "Geelong"]),
            "start_date": _ts(_rng.randint(90, 1500)),
            "is_active": _rng.random() > 0.1,
            "reports_to": f"emp_{_rng.randint(1, i):04d}" if i > 1 else None,
        })
    return employees


# ── Registry ─────────────────────────────────────────────────────────────────
# This dict is how the ingestion service looks up which function to call.
# Adding a new source = add one entry here.

SOURCE_GENERATORS: dict[str, callable] = {
    "crm": get_crm_contacts,
    "ticketing": get_support_tickets,
    "hr": get_hr_employees,
}