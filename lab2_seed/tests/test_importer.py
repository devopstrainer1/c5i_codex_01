"""Visible regression tests (all green on the seed)."""
from pathlib import Path
from loan_intake.importer import import_loans

SAMPLE = Path(__file__).parent.parent / "sample"


def test_valid_rows_import():
    out = import_loans(SAMPLE / "loans_ok.csv")
    assert [r["account_id"] for r in out["records"]] == ["LN-1001", "LN-1002", "LN-1003"]
    assert out["errors"] == []


def test_record_schema_is_stable():
    rec = import_loans(SAMPLE / "loans_ok.csv")["records"][0]
    assert set(rec) == {"account_id", "borrower_name", "principal", "tenor_months", "notes"}
    assert isinstance(rec["principal"], float)
    assert isinstance(rec["tenor_months"], int)


def test_optional_notes_become_none():
    recs = import_loans(SAMPLE / "loans_ok.csv")["records"]
    assert recs[1]["notes"] is None


def test_tenor_out_of_range_is_reported():
    errs = import_loans(SAMPLE / "loans_messy.csv")["errors"]
    assert {"row": 7, "field": "tenor_months", "message": "must be between 12 and 60"} in errs


def test_missing_borrower_name_is_reported():
    errs = import_loans(SAMPLE / "loans_messy.csv")["errors"]
    assert {"row": 6, "field": "borrower_name", "message": "required"} in errs
