"""INSTRUCTOR ONLY. Acceptance tests for the rewritten brief. Fails on the seed."""
from pathlib import Path
import csv, tempfile
from loan_intake.importer import import_loans

SAMPLE = Path(__file__).parent.parent / "sample"


def _one_row(account_id):
    d = tempfile.mkdtemp()
    p = Path(d) / "x.csv"
    with open(p, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["account_id", "borrower_name", "principal", "tenor_months", "notes"])
        w.writerow([account_id, "Test User", "100000", "24", ""])
    return import_loans(p)


def test_empty_account_id_rejected():
    out = _one_row("")
    assert out["records"] == []
    assert out["errors"] == [{"row": 2, "field": "account_id", "message": "required"}]


def test_whitespace_account_id_rejected():
    out = _one_row("   ")
    assert out["records"] == []
    assert out["errors"][0]["field"] == "account_id"


def test_missing_in_messy_sample_reported_for_rows_3_and_4():
    errs = import_loans(SAMPLE / "loans_messy.csv")["errors"]
    fields = {(e["row"], e["field"]) for e in errs}
    assert (3, "account_id") in fields and (4, "account_id") in fields


def test_valid_account_id_is_trimmed():
    out = _one_row("  LN-9  ")
    assert out["records"][0]["account_id"] == "LN-9"


def test_schema_unchanged():
    rec = _one_row("LN-9")["records"][0]
    assert isinstance(rec["principal"], float)
    assert set(rec) == {"account_id", "borrower_name", "principal", "tenor_months", "notes"}
