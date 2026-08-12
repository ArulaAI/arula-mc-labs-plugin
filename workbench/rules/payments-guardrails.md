# Payments Guardrails

## PAN Handling
- PAN must never appear in logs, console output, journey files, or PR descriptions
- Use `secret_scan.py:scan_for_pan()` before any write operation on data that may contain PAN
- Mask format: first 6 + last 4 digits visible, remainder as `*`

## ISO Field Constraints
- Field 2 (PAN): always masked
- Field 35 (Track 2): always redacted entirely
- Field 45 (Track 1): always redacted entirely
- Field 52 (PIN block): always redacted entirely
- All other fields: log only field number and length, not value, in audit contexts

## Authorization Flow
- Authorization requests must follow the spec's sequence diagram exactly
- Any deviation from the sequence is a Failure Mode 1 (spec drift) finding
- Holds and partial authorizations must be handled explicitly — no silent fallthrough

## Downstream Contracts
- Any change to a downstream API contract must be flagged as Failure Mode 4
- Contract changes require explicit sign-off in the PR description
