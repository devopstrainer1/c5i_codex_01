# loan_intake seed (Day 1, Lab 2)
Run visible tests:      python -m pytest tests -q
Instructor acceptance:  python -m pytest instructor_only -q   (fails on the seed by design)
Planted items (do NOT tell learners):
 1. account_id is never validated (target of the rewritten brief)
 2. `except Exception: continue` silently drops malformed rows (the "weird failures")
 3. loans_excel_export.csv has a UTF-8 BOM: header key becomes '\ufeffaccount_id'
 4. principal is float and tests pin it: "robust money handling" tempts a Decimal change
