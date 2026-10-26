"""Loan application CSV importer (seed module for the Day 1 labs).

Public contract used by other modules:
    import_loans(path) -> {"records": [...], "errors": [...]}
    record = {account_id, borrower_name, principal(float), tenor_months(int), notes(str|None)}
    error  = {"row": int, "field": str, "message": str}
"""
import csv
import logging

logger = logging.getLogger(__name__)

TENOR_MIN, TENOR_MAX = 12, 60


class ValidationError(Exception):
    def __init__(self, row_number, field, message):
        super().__init__(f"row {row_number}: {field}: {message}")
        self.row_number = row_number
        self.field = field
        self.message = message


def _parse_row(row_number, raw):
    record = {
        "account_id": raw.get("account_id"),
        "borrower_name": (raw.get("borrower_name") or "").strip(),
        "principal": float(raw["principal"]),
        "tenor_months": int(raw["tenor_months"]),
        "notes": (raw.get("notes") or "").strip() or None,
    }
    if not record["borrower_name"]:
        raise ValidationError(row_number, "borrower_name", "required")
    if record["principal"] <= 0:
        raise ValidationError(row_number, "principal", "must be positive")
    if not TENOR_MIN <= record["tenor_months"] <= TENOR_MAX:
        raise ValidationError(row_number, "tenor_months", "must be between 12 and 60")
    return record


def import_loans(path):
    records, errors = [], []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row_number, raw in enumerate(reader, start=2):
            try:
                records.append(_parse_row(row_number, raw))
            except ValidationError as exc:
                errors.append({"row": exc.row_number, "field": exc.field, "message": exc.message})
            except Exception:
                continue
    return {"records": records, "errors": errors}
