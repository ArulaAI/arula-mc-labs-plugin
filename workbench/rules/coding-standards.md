# Coding Standards

## General
- All functions must have a single clear responsibility
- No function longer than 50 lines
- All public functions must have a docstring (one line)
- Use snake_case for Python, kebab-case for file/directory names

## Payments-specific
- Never log, print, or write PAN (Primary Account Number) values — mask as `****-****-****-XXXX`
- Never log full ISO 8583 field 2 (PAN), field 35 (track 2), field 45 (track 1)
- All sensitive ISO fields must be redacted before writing to any log or journey file
- Authorization flows must match the spec's sequence diagram exactly

## Testing
- Every acceptance criterion in the spec must map to at least one test
- Tests must be deterministic — no random data, fixed seeds where randomness is needed
- Integration tests must use real filesystem / real subprocess — no mocking of OS calls

## Git
- One commit per logical change
- Commit messages: `type(scope): description` (feat, fix, docs, test, chore)
- No binary files in commits
- No secrets, PAN, or credentials in any commit
