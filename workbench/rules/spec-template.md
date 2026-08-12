# Spec Template

Every spec produced by `spec-craft` must contain all seven sections below.
A spec is NOT READY if any section is missing or if any acceptance criterion
is non-testable (i.e., cannot be verified by a test or a deterministic check).

---

## Context
_What problem are we solving and why now? Max 3 sentences._

## Scope
_What is explicitly in scope and out of scope for this change._

## Interfaces
_API contracts, ISO message types, downstream services touched.
List each interface as: name | direction (in/out) | format | owner._

## Data
_Data structures, field definitions, persistence requirements.
Reference ISO field numbers where applicable._

## Acceptance Criteria
_Numbered list. Each criterion must be independently testable._
_Format: AC-N: [Given/When/Then or assertion statement]_

## Non-Negotiables
_Constraints that cannot be traded off: compliance, security, SLA._

## Risks
_Known risks and mitigations. At minimum address: data integrity, downstream impact._
