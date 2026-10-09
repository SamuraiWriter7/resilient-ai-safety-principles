# Resilient AI Safety Principles

Structural principles for preventing malicious, mistaken, compromised,
or runaway AI actions from scaling into systemic authority, speed,
scope, and impact.

**Version:** v0.1  
**Status:** Draft Specification

---

## 1. Overview

Resilient AI Safety Principles is a structural safety specification
for AI agents, multi-agent systems, and AI-enabled infrastructure.

It does not attempt to perfectly identify:

- malicious humans;
- malicious AI systems;
- harmful intent;
- perfectly aligned or misaligned internal reasoning.

Instead, it focuses on a more operational problem:

> How can a system remain safe even when malicious intent,
> mistakes, compromise, uncertainty, or failure exist?

The central thesis is:

> **The primary danger is not malicious intent itself, but structures
> that convert malicious intent, error, or compromise into large-scale power.**

The goal is therefore not to construct a system that requires
perfect actors.

The goal is to build a system in which imperfect actors
cannot easily create unbounded systemic failure.

---

# 2. Core Safety Objective

A resilient AI system SHOULD assume that:

- humans can make mistakes;
- AI systems can make mistakes;
- humans can act maliciously;
- AI systems can be compromised;
- authorization can fail;
- approval can fail;
- monitoring can fail;
- evidence can become stale;
- network nodes can fail;
- recovery itself can fail.

Safety MUST NOT depend on eliminating every failure.

Instead, failure SHOULD remain:

- bounded;
- observable;
- attributable;
- containable;
- independently verifiable;
- recoverable where technically feasible.

The core objective is:

> **Prevent local failure, abuse, error, or compromise from becoming systemic power.**

---

# 3. Design Target

The target is not:

```text
Perfect AI
```

The target is:

```text
Resilient AI Civilization
```

A resilient AI civilization assumes:

```text
Failure can happen
Malice can exist
Humans can be wrong
AI can be wrong
Systems can be compromised
```

while preserving:

```text
Bounded Authority
Observable Effects
Local Failure
Traceability
Containment
Verification
Recovery
```

---

# 4. Ten Structural Principles

v0.1 defines ten primary safety principles.

## Principle 1 — Least Authority

AI systems SHOULD receive only the minimum authority
required for the current authorized operation.

Authority may be bounded by:

- scope;
- action;
- target;
- duration;
- frequency;
- resource;
- impact boundary.

Conceptually:

```text
Authority
=
Scope × Action × Target × Duration
```

An AI actor MUST NOT independently increase its own authority.

---

## Principle 2 — Role Separation

Planning, execution, auditing, and approval SHOULD NOT be concentrated
inside one high-risk authority domain.

Reference roles:

```text
Planner
Executor
Auditor
Approver
```

A producer of a high-risk action MUST NOT be its sole final approver.

---

## Principle 3 — Pre-Execution Gating

AI intent MUST NOT directly become external execution authority.

Reference flow:

```text
Intent
  ↓
Evaluation
  ↓
Authorization
  ↓
Execution
```

High-risk execution SHOULD pass through an explicit safety gate.

---

## Principle 4 — Effect-Oriented Monitoring

Safety SHOULD NOT depend solely on inferred intent.

The system SHOULD observe:

- requested action;
- authority used;
- accessed target;
- state change;
- external effect;
- resource consumption;
- resulting impact.

The important question is:

> Should this action, with this authority, be allowed to produce
> this effect against this target?

---

## Principle 5 — Containment First

Suspicious operations SHOULD enter reversible containment
before irreversible response where possible.

Reference states:

```text
ACTIVE
  ↓
HELD
  ↓
QUARANTINED
```

Containment SHOULD preserve both evidence and recovery options.

---

## Principle 6 — Independent Verification

The actor that produced or executed a high-risk action
SHOULD NOT be its sole safety verifier.

Verification MAY use:

- another AI;
- another model;
- deterministic rules;
- external audit;
- human review;
- multiple independent mechanisms.

---

## Principle 7 — Controlled Local Failure

Systems SHOULD assume components can fail.

The objective is not:

> Nothing ever breaks.

The objective is:

> **When something breaks, the failure remains local.**

Possible mechanisms include:

- node isolation;
- sandboxing;
- authority revocation;
- network restriction;
- resource limitation.

---

## Principle 8 — End-to-End Traceability

High-impact actions SHOULD leave enough evidence
to reconstruct relevant causal relationships.

Trace SHOULD connect:

```text
Intent
Authority
Decision
Approval
Execution
Effect
Responsibility
Recovery
```

Trace is more than logging.

It is a structural evidence layer.

---

## Principle 9 — Recoverability

Safety does not end when execution stops.

A system SHOULD support a path toward
a valid safe state after failure or containment.

Recovery MAY include:

- rollback;
- authority reduction;
- re-approval;
- state reconstruction;
- successor handoff;
- safe retry;
- evidence refresh;
- component replacement.

---

## Principle 10 — Layered Defense

Critical safety MUST NOT depend exclusively on:

- one AI model;
- one agent;
- one human;
- one rule;
- one gate;
- one monitoring mechanism.

Recommended defense layers include:

```text
Model
Cognition
Authority
Execution
Network
Audit
Human
Institution
```

---

# 5. Cross-Cutting Principles

## Temporal Least Authority

Authority SHOULD be temporary by default.

Authority SHOULD support:

- activation;
- expiration;
- renewal;
- revocation;
- re-authorization.

Expired or revoked authority MUST NOT silently become valid again.

---

## Human Fallibility

Human participation MUST NOT be treated as proof of safety.

Humans may be affected by:

- error;
- fatigue;
- manipulation;
- collusion;
- habituation;
- incomplete information;
- conflict of interest.

Therefore:

```text
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone
```

The preferred model is:

> **Human-in-the-auditable-loop**

---

# 6. Core Safety Invariants

v0.1 defines ten safety invariants.

| ID | Invariant |
|---|---|
| `SAFETY-INV-001` | No Self-Escalation |
| `SAFETY-INV-002` | No Sole Self-Approval |
| `SAFETY-INV-003` | No Direct Intent-to-Execution Transition |
| `SAFETY-INV-004` | Observable Effects Over Assumed Intent |
| `SAFETY-INV-005` | Reversible Containment When Feasible |
| `SAFETY-INV-006` | Independent Safety Verification |
| `SAFETY-INV-007` | Failure Boundary Preservation |
| `SAFETY-INV-008` | Trace Preservation |
| `SAFETY-INV-009` | Recovery Path Required |
| `SAFETY-INV-010` | No Single Safety Dependency |

These invariants form the normative structural core of v0.1.

---

# 7. Reference Safety Lifecycle

The reference lifecycle is:

```text
Intent
  ↓
Evaluation
  ↓
Authorization
  ↓
Pre-Execution Gate
  ↓
Execution
  ↓
Observation
  ↓
Trace
  ↓
Safety Classification
  ↓
 ┌──────────────────────────┐
 │ NORMAL                   │
 │ SUSPICIOUS               │
 │ UNSAFE                   │
 │ UNKNOWN                  │
 └──────────────────────────┘
              ↓
       if intervention
              ↓
         Containment
              ↓
    Independent Verification
              ↓
           Recovery
              ↓
       Re-Authorization
              ↓
 ┌──────────────────────────┐
 │ RESUME                   │
 │ RESTRICT                 │
 │ ISOLATE                  │
 │ TRANSFER                 │
 │ TERMINATE                │
 └──────────────────────────┘
```

No single stage is assumed to be infallible.

---

# 8. Repository Structure

```text
resilient-ai-safety-principles/
├─ README.md
├─ SPEC.md
├─ PRINCIPLES.md
├─ ARCHITECTURE.md
├─ CHANGELOG.md
├─ LICENSE
├─ requirements.txt
│
├─ mappings/
│  ├─ tacp.md
│  ├─ authority.md
│  ├─ trace.md
│  └─ zero-network.md
│
├─ schemas/
│  └─ safety-assessment.schema.json
│
├─ examples/
│  ├─ pass/
│  │  └─ high-risk-authorized-action.json
│  │
│  └─ fail/
│     ├─ self-escalated-authority.json
│     ├─ sole-self-approval.json
│     ├─ direct-intent-to-execution.json
│     ├─ intent-only-safety.json
│     ├─ silent-release-from-containment.json
│     ├─ self-verification-only.json
│     ├─ cross-domain-failure-propagation.json
│     ├─ missing-safety-trace.json
│     ├─ permanent-hold-without-resolution.json
│     └─ single-point-of-safety-trust.json
│
├─ scripts/
│  └─ validate_examples.py
│
└─ .github/
   └─ workflows/
      └─ validate.yml
```

---

# 9. Document Roles

## `SPEC.md`

Defines normative requirements using:

- MUST;
- MUST NOT;
- SHOULD;
- SHOULD NOT;
- MAY.

This is the primary normative specification.

---

## `PRINCIPLES.md`

Explains:

- why each principle exists;
- which structural failure it prevents;
- desired patterns;
- anti-patterns;
- interaction between principles.

---

## `ARCHITECTURE.md`

Defines the reference safety architecture.

It maps the principles into logical layers including:

- intent;
- evaluation;
- authority;
- execution;
- observation;
- trace;
- containment;
- verification;
- recovery.

---

# 10. Mapping Documents

The `mappings/` directory connects the upper-level safety principles
to lower-level protocol and infrastructure concepts.

## `mappings/tacp.md`

Maps the principles to operational states such as:

- held;
- expired;
- revoked;
- authorization-unknown;
- recovery;
- successor-held.

TACP primarily implements:

```text
Pre-Execution Gating
Containment
Verification
Recovery
Re-Authorization
```

---

## `mappings/authority.md`

Maps safety principles to:

- authority issuance;
- scope;
- expiration;
- revocation;
- delegation;
- escalation;
- re-authorization.

Core rule:

> AI may request authority, but must not manufacture authority.

---

## `mappings/trace.md`

Defines Trace as evidence connecting:

```text
Request
→ Authority
→ Approval
→ Execution
→ Effect
→ Containment
→ Recovery
```

It also distinguishes:

```text
Safety Trace
≠
Full Internal Reasoning Trace
```

Complete chain-of-thought capture is not required.

---

## `mappings/zero-network.md`

Maps resilient safety into distributed AI networks.

Core rules include:

```text
Connection ≠ Authority
Authority ≠ Unlimited Propagation
Failure ≠ Network-Wide Failure
```

It focuses on:

- local failure boundaries;
- node isolation;
- distributed authority;
- shared trace;
- network recovery.

---

# 11. Machine-Readable Safety Assessment

The schema is located at:

```text
schemas/safety-assessment.schema.json
```

It defines a common format for:

- PASS examples;
- FAIL examples;
- operation metadata;
- authority;
- execution;
- observation;
- trace;
- invariants;
- conformance.

The schema uses:

```text
JSON Schema Draft 2020-12
```

---

# 12. PASS Example

The current reference PASS case is:

```text
examples/pass/high-risk-authorized-action.json
```

It demonstrates:

```text
Intent
  ↓
Evaluation
  ↓
Bounded Authority
  ↓
Independent Approval
  ↓
Pre-Execution Gate
  ↓
Execution
  ↓
Observation
  ↓
Trace
```

The action is considered safe not merely because it succeeds,
but because it succeeds through the required safety structure.

---

# 13. FAIL Examples

v0.1 includes ten reference failure cases.

| File | Primary Failure |
|---|---|
| `self-escalated-authority.json` | `SAFETY-INV-001` |
| `sole-self-approval.json` | `SAFETY-INV-002` |
| `direct-intent-to-execution.json` | `SAFETY-INV-003` |
| `intent-only-safety.json` | `SAFETY-INV-004` |
| `silent-release-from-containment.json` | `SAFETY-INV-005` |
| `self-verification-only.json` | `SAFETY-INV-006` |
| `cross-domain-failure-propagation.json` | `SAFETY-INV-007` |
| `missing-safety-trace.json` | `SAFETY-INV-008` |
| `permanent-hold-without-resolution.json` | `SAFETY-INV-009` |
| `single-point-of-safety-trust.json` | `SAFETY-INV-010` |

These examples are intentionally designed so that an operation
may be technically successful while still failing structurally.

For example:

```text
Execution succeeded
        ≠
Safety conformance passed
```

---

# 14. Validation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run validation:

```bash
python scripts/validate_examples.py
```

The validator checks:

- JSON Schema conformance;
- PASS/FAIL directory consistency;
- all ten invariant assessments;
- FAIL examples contain at least one failed invariant;
- PASS examples contain no failed invariant;
- `primary_failure` corresponds to an actual failed invariant;
- violation references are consistent;
- trace completeness metadata is internally consistent.

Expected result for the current v0.1 example set:

```text
=== Summary ===
PASS examples : 1
FAIL examples : 10
Validated     : 11/11
Invalid       : 0

All examples validated successfully.
```

---

# 15. Continuous Integration

GitHub Actions validation is defined at:

```text
.github/workflows/validate.yml
```

The workflow runs on:

- push;
- pull request;
- manual dispatch.

Validation currently runs with:

```text
Python 3.10
Python 3.12
```

The workflow performs:

```text
Checkout
  ↓
Python Setup
  ↓
Dependency Installation
  ↓
Required File Check
  ↓
Validator Compilation
  ↓
Example Validation
```

The CI job uses read-only repository permissions.

---

# 16. Conformance Profiles

v0.1 defines three provisional profiles.

## BASIC

Provides minimum structural protections.

---

## CONTROLLED

Adds stronger:

- approval separation;
- containment;
- independent verification;
- trace.

---

## RESILIENT

Requires all ten core safety invariants.

It SHOULD additionally support:

- temporal authority;
- structured recovery;
- human fallibility controls;
- layered defense.

The current reference PASS example targets:

```text
RESILIENT
```

---

# 17. Philosophical Review Cycle

High-risk evaluation MAY include four complementary perspectives.

## Epistemology

```text
What is known?
What is unknown?
Is the evidence sufficient?
```

## Logic

```text
Does the conclusion follow?
Are there hidden inference jumps?
```

## Ontology / Metaphysics

```text
What exactly is being acted upon?
What problem is actually being solved?
```

## Ethics

```text
Who is affected?
What harm may occur?
Should the action happen?
```

These perspectives are intended to correct one another.

They are not separate absolute judges.

---

# 18. Structural Risk Model

A conceptual heuristic is:

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

This is not a strict mathematical formula.

It illustrates a central property of the design:

Safety can improve even when malicious intent
or failure potential cannot be completely removed.

For example:

```text
Malicious Intent = unchanged

Authority ↓
Scope ↓
Duration ↓
Connectivity ↓

Trace ↑
Containment ↑
Verification ↑
Recovery ↑

→ Systemic Risk ↓
```

---

# 19. Non-Goals

v0.1 does not attempt to define:

- universal malicious-user detection;
- universal malicious-AI detection;
- perfect alignment;
- complete model interpretability;
- complete chain-of-thought recording;
- perfect human judgment;
- one mandatory AI architecture;
- one mandatory authorization system;
- one mandatory network topology.

The project defines structural safety constraints.

---

# 20. Architectural Anti-Pattern

The primary anti-pattern is:

```text
User / AI Intent
      ↓
Single Powerful Agent
      ↓
Broad Persistent Authority
      ↓
Unrestricted Tools
      ↓
Self-Approval
      ↓
Self-Verification
      ↓
Global Effect
```

This structure concentrates:

- intelligence;
- authority;
- execution;
- verification;
- persistence;

inside one failure domain.

A capable model does not make this structure safe.

---

# 21. Core Design Rules

The architecture can be summarized as:

```text
Separate thought from authority.

Separate authority from execution.

Separate execution from verification.

Separate local failure from global propagation.

Connect all of them through trace.

Restore operation through recovery.
```

Or more compactly:

> **Bound power, observe effects, preserve evidence, isolate failure, recover safely.**

---

# 22. Final Principle

This project can be reduced to one structural proposition:

> **Dangerous intent becomes dangerous power only when structure allows it to scale.**

Therefore:

> **Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.**

The long-term design target is not an ecosystem
that assumes perfect humans or perfect AI.

It is:

> **Resilient AI Civilization**
