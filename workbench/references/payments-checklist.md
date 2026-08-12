# Payments Red-Team Review Checklist

Used by `red-team-review` skill and `pr-reviewer` subagent.

## PAN and Sensitive Data
- [ ] No PAN in logs, outputs, or journey files
- [ ] Track 1/2 data not persisted or logged
- [ ] PIN block never logged or transmitted unencrypted

## Authorization
- [ ] Authorization sequence matches spec exactly
- [ ] Partial auth handled explicitly
- [ ] Decline path returns correct ISO response code
- [ ] Timeout path does not silently approve

## Contracts
- [ ] No undocumented breaking changes to downstream APIs
- [ ] ISO field types match the field map
- [ ] Mandatory ISO fields are present in all message paths

## Audit
- [ ] Every gate decision is journaled
- [ ] Override reasons are recorded
- [ ] Journey file is append-only

## General Security
- [ ] No credentials in code or config
- [ ] No hardcoded URLs pointing to production
- [ ] No debug flags left enabled
