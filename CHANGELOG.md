# Changelog

All notable changes to **Resilient AI Safety Principles**
will be documented in this file.

The project follows an incremental specification model.

Versions may introduce:

- new structural principles;
- safety invariants;
- machine-readable schemas;
- mappings;
- conformance examples;
- validation rules;
- interoperability guidance.

---

# [0.1.0] - 2026-10-10

## Added

Initial public specification of
**Resilient AI Safety Principles**.

v0.1 establishes the first structural safety baseline
for preventing malicious, mistaken, compromised,
or runaway AI actions from becoming systemic power.

---

## Core Thesis

Defined the central proposition:

> The primary danger is not malicious intent itself,
> but structures that convert malicious intent, error,
> or compromise into large-scale power.

Established the long-term target as:

> **Resilient AI Civilization**

rather than:

> Perfect AI

---

## Structural Principles

Added ten primary structural safety principles:

1. Least Authority
2. Role Separation
3. Pre-Execution Gating
4. Effect-Oriented Monitoring
5. Containment First
6. Independent Verification
7. Controlled Local Failure
8. End-to-End Traceability
9. Recoverability
10. Layered Defense

---

## Cross-Cutting Principles

Added:

### Temporal Least Authority

Authority should be:

- temporary;
- expirable;
- revocable;
- renewable only through explicit conditions;
- subject to re-authorization.

### Human Fallibility

Human participation is treated as one safety layer,
not as proof of correctness.

Introduced the structural pattern:

```text
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone
```

and the concept:

> Human-in-the-auditable-loop

---

## Safety Invariants

Added ten normative safety invariants:

- `SAFETY-INV-001` — No Self-Escalation
- `SAFETY-INV-002` — No Sole Self-Approval
- `SAFETY-INV-003` — No Direct Intent-to-Execution Transition
- `SAFETY-INV-004` — Observable Effects Over Assumed Intent
- `SAFETY-INV-005` — Reversible Containment When Feasible
- `SAFETY-INV-006` — Independent Safety Verification
- `SAFETY-INV-007` — Failure Boundary Preservation
- `SAFETY-INV-008` — Trace Preservation
- `SAFETY-INV-009` — Recovery Path Required
- `SAFETY-INV-010` — No Single Safety Dependency

---

## Normative Specification

Added:

```text
SPEC.md
```

The specification defines:

- normative language;
- structural requirements;
- authority constraints;
- role separation;
- pre-execution gating;
- effect-oriented monitoring;
- containment;
- independent verification;
- controlled local failure;
- traceability;
- recovery;
- layered defense;
- emergency behavior;
- conformance requirements.

---

## Principles Document

Added:

```text
PRINCIPLES.md
```

The document explains:

- rationale behind each principle;
- desired safety patterns;
- anti-patterns;
- failure amplification;
- interaction between principles;
- human fallibility;
- temporal authority;
- philosophical review.

---

## Reference Architecture

Added:

```text
ARCHITECTURE.md
```

Defined the reference safety pipeline:

```text
Intent
  ↓
Evaluation
  ↓
Authority
  ↓
Pre-Execution Gate
  ↓
Execution
  ↓
Observation
  ↓
Trace
  ↓
Containment
  ↓
Independent Verification
  ↓
Recovery
  ↓
Re-Authorization
```

Defined logical safety layers for:

- intent;
- evaluation;
- authority;
- execution;
- observation;
- trace;
- containment;
- verification;
- recovery;
- human governance.

---

## Philosophical Review Cycle

Defined a four-perspective high-risk review cycle:

- Epistemology
- Logic
- Ontology / Metaphysics
- Ethics

The cycle is intended to provide mutual correction,
not four independent absolute judgments.

---

## TACP Mapping

Added:

```text
mappings/tacp.md
```

Mapped structural safety principles to TACP operational states,
including:

- held;
- expired;
- revoked;
- authorization-unknown;
- approval-expired;
- evidence-stale;
- resource-limit;
- carried-blocker;
- successor-held;
- recovery states.

Established the relationship:

```text
Safety Principle
      ↓
TACP Decision
      ↓
Safe State Transition
```

---

## Authority Mapping

Added:

```text
mappings/authority.md
```

Defined structural authority concepts including:

- authority request vs authority grant;
- scope restrictions;
- target restrictions;
- resource limits;
- temporal validity;
- revocation;
- delegation;
- replay protection;
- re-authorization;
- recovery-time authority reduction.

Established the rule:

> AI may request authority, but must not manufacture authority.

---

## Trace Mapping

Added:

```text
mappings/trace.md
```

Defined safety trace as evidence connecting:

```text
Request
→ Evaluation
→ Authority
→ Approval
→ Execution
→ Effect
→ Containment
→ Recovery
```

Clarified that:

```text
Safety Trace
≠
Full Internal Reasoning Trace
```

Added guidance for:

- causal linking;
- recovery continuity;
- delegation trace;
- human override trace;
- tamper evidence;
- trace gaps;
- cross-domain trace;
- evidence freshness.

---

## AI Zero Network Mapping

Added:

```text
mappings/zero-network.md
```

Mapped resilient safety principles to distributed AI networks.

Defined:

- local failure domains;
- node isolation;
- authority registry;
- trace relay;
- field snapshot;
- cross-domain bridges;
- network containment;
- node recovery;
- successor nodes;
- distributed verification.

Established the structural rules:

```text
Connection ≠ Authority
Authority ≠ Unlimited Propagation
Failure ≠ Network-Wide Failure
```

---

## PASS Example

Added:

```text
examples/pass/high-risk-authorized-action.json
```

The reference PASS case demonstrates:

- bounded authority;
- logical role separation;
- independent approval;
- pre-execution gating;
- controlled execution;
- effect observation;
- complete trace;
- RESILIENT conformance.

---

## FAIL Examples

Added ten reference FAIL cases.

### `self-escalated-authority.json`

Tests:

```text
SAFETY-INV-001
```

A system fails when an AI independently expands
its own effective authority.

---

### `sole-self-approval.json`

Tests:

```text
SAFETY-INV-002
```

A high-risk action producer cannot be
its own sole final approver.

---

### `direct-intent-to-execution.json`

Tests:

```text
SAFETY-INV-003
```

High-risk intent cannot directly become external execution.

---

### `intent-only-safety.json`

Tests:

```text
SAFETY-INV-004
```

A high-risk operation cannot be authorized
solely because intent appears benign.

---

### `silent-release-from-containment.json`

Tests:

```text
SAFETY-INV-005
```

A held operation cannot silently return to execution
without re-evaluation and re-authorization.

---

### `self-verification-only.json`

Tests:

```text
SAFETY-INV-006
```

The executor cannot be the sole verifier
of its own high-risk result.

---

### `cross-domain-failure-propagation.json`

Tests:

```text
SAFETY-INV-007
```

Failure or compromise in one authority domain
must not automatically propagate equivalent unsafe capability
into another domain.

---

### `missing-safety-trace.json`

Tests:

```text
SAFETY-INV-008
```

A high-impact operation fails conformance
when authority, approval, execution, and effect
cannot be causally reconstructed.

---

### `permanent-hold-without-resolution.json`

Tests:

```text
SAFETY-INV-009
```

Containment must define at least one path toward:

- recovery;
- restriction;
- isolation;
- termination;
- re-authorization.

---

### `single-point-of-safety-trust.json`

Tests:

```text
SAFETY-INV-010
```

Critical safety cannot depend exclusively
on one model, agent, human, or control mechanism.

---

## JSON Schema

Added:

```text
schemas/safety-assessment.schema.json
```

The schema uses:

```text
JSON Schema Draft 2020-12
```

and defines common structures for:

- operations;
- roles;
- evaluations;
- authority;
- approvals;
- gates;
- execution;
- observation;
- verification;
- trace;
- containment;
- recovery;
- violations;
- invariant assessments;
- conformance.

---

## Validation Script

Added:

```text
scripts/validate_examples.py
```

The validator performs:

1. JSON loading validation
2. JSON Schema validation
3. PASS/FAIL directory consistency validation
4. invariant completeness validation
5. invariant semantic validation
6. primary failure validation
7. violation-reference validation
8. trace consistency validation

The validator requires all ten invariant assessments
for each example.

---

## Validation Dependency

Added:

```text
requirements.txt
```

with:

```text
jsonschema>=4.23,<5
```

---

## GitHub Actions

Added:

```text
.github/workflows/validate.yml
```

The workflow runs validation on:

- push;
- pull request;
- manual dispatch.

Validation runs against:

```text
Python 3.10
Python 3.12
```

The workflow includes:

- repository checkout;
- Python setup;
- pip caching;
- dependency installation;
- required-file checks;
- validator compilation;
- example validation.

Repository permissions are limited to:

```text
contents: read
```

for the validation job.

---

## Validation Status

The initial v0.1 corpus currently contains:

```text
PASS examples : 1
FAIL examples : 10
Total         : 11
```

All examples successfully pass structural validation:

```text
Validated     : 11/11
Invalid       : 0
```

GitHub Actions validation has passed.

---

## Conformance Profiles

Added provisional profiles:

### BASIC

Minimum structural protection.

### CONTROLLED

Adds stronger:

- role separation;
- containment;
- independent verification;
- traceability.

### RESILIENT

Requires all ten core safety invariants.

---

## Structural Risk Model

Added the conceptual heuristic:

```text
Systemic Risk
≈
Failure Potential
× Authority
× Speed
× Scope
× Persistence
× Connectivity
```

This is a design heuristic,
not a strict quantitative equation.

---

## Design Principle

v0.1 establishes the following core design rules:

```text
Separate thought from authority.

Separate authority from execution.

Separate execution from verification.

Separate local failure from global propagation.

Connect all of them through trace.

Restore operation through recovery.
```

---

## Summary

v0.1 establishes the first complete vertical slice of the project:

```text
Philosophy
   ↓
Structural Principles
   ↓
Normative Requirements
   ↓
Reference Architecture
   ↓
Protocol Mappings
   ↓
Machine-Readable Examples
   ↓
JSON Schema
   ↓
Validator
   ↓
GitHub Actions
```

The release therefore moves the project
from conceptual safety principles
to a machine-testable structural specification.

The central proposition remains:

> **Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.**
