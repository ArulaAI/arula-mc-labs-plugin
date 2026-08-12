# Spec Template — Annotated Example

This is a worked example of a correctly completed spec.
`spec_check.py` uses the section headers below as the required-section list.

---

## Context
We need to add partial authorisation support to the AU acquiring gateway.
Currently, a transaction is either fully approved or fully declined.
Mastercard mandates partial auth support by Q4.

## Scope
In scope: partial auth flag in ISO field 56, response code 10, amount field update.
Out of scope: cardholder notification, statement rendering, settlement changes.

## Interfaces
| Name | Direction | Format | Owner |
|---|---|---|---|
| Acquiring gateway | out | ISO 8583 | Platform team |
| Core banking | in | ISO 8583 | Core team |

## Data
- Field 56 (Additional Data): bit 0 = partial auth supported (1) / not supported (0)
- Field 4 (Amount): updated to approved amount in partial auth response
- Response code 10: partial approval

## Acceptance Criteria
- AC-1: Given a transaction request with field 56 bit 0 = 1, when the issuer partially approves, then the response carries code 10 and field 4 equals the approved amount.
- AC-2: Given a transaction request with field 56 bit 0 = 0, when the issuer partially approves, then the response carries code 05 (decline) and field 4 is unchanged.
- AC-3: Given any transaction, when field 56 is absent, then partial auth is treated as not supported.

## Non-Negotiables
- PAN must not appear in any log entry related to partial auth processing.
- Response code 10 must only be used for partial approvals — never for full approvals.

## Risks
- Risk: Core banking may not handle field 56 — mitigation: integration test with emulator.
- Risk: Existing decline logic may suppress code 10 — mitigation: regression test suite.
