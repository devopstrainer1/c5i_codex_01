# Incident notes - September 2026

## INC-4821 - Duplicate EMI debit (resolved 9 September)
Symptom: customers reported two EMI debits on the same day. Root cause: the e-mandate gateway retried a timed-out debit request without an idempotency key, and the first request later succeeded. Fix: an idempotency key was added to all debit requests in release 4.18.2. Customer remedy: the duplicate debit is refunded within 5 working days of the customer's complaint.

## INC-4822 - Delayed SMS reminders (resolved 12 September)
Symptom: EMI due-date reminders arrived up to 6 hours late. Root cause: SMS vendor queue backlog after a certificate renewal. Fix: failover vendor enabled. Customer remedy: none required.

## INC-4830 - Statement PDF missing page footer (resolved 21 September)
Symptom: the monthly statement PDF dropped the regulatory footer on page 2. Root cause: template pagination change in release 4.18.1. Fix: footer moved to the master page. Customer remedy: none required.
