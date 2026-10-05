# Resilient AI Safety Principles

Structural principles for preventing malicious, mistaken, compromised,
or runaway AI actions from scaling into systemic authority, speed,
scope, and impact.

**Version:** v0.1  
**Status:** Draft Specification

---

## 1. Purpose

This repository defines a structural foundation for AI safety.

It does not attempt to perfectly identify malicious humans,
malicious AI systems, or harmful intent.

Human intent is partially observable.

AI reasoning may also be incomplete, mistaken, manipulated,
or difficult to interpret.

Therefore, this specification focuses on a different problem:

> Prevent malicious intent, mistakes, compromise, or runaway behavior
> from being amplified into excessive authority, speed, scale,
> autonomy, or systemic impact.

The central design objective is not perfect intelligence.

It is resilient structure.

---

## 2. Core Thesis

The central thesis of this specification is:

> The primary danger is not malicious intent itself,
> but structures that convert malicious intent into large-scale power.

A safe AI infrastructure SHOULD therefore assume that:

- humans can make mistakes;
- AI systems can make mistakes;
- humans can act maliciously;
- AI systems can be compromised;
- authorization can be misconfigured;
- monitoring can fail;
- approval can fail;
- individual nodes can fail.

Safety MUST NOT depend on eliminating all such failures.

Instead, systems SHOULD be designed so that failures remain:

- bounded;
- observable;
- attributable;
- containable;
- reversible where possible;
- independently verifiable;
- recoverable.

---

## 3. Safety Objective

This specification does not define the goal as:

> Perfect AI

Instead, the target is:

> Resilient AI Civilization

A resilient AI system assumes failure is possible while preventing
local failure from becoming systemic failure.

The system SHOULD therefore support:

```text
Failure
  ↓
Detection
  ↓
Containment
  ↓
Independent Verification
  ↓
Recovery
  ↓
Re-authorization

4. Structural Safety Principles
v0.1 defines ten primary structural principles.
Principle 1 — Least Authority
An AI system MUST receive only the minimum authority necessary
for the current operation.
Authority SHOULD be bounded by:
- scope;
- action;
- target;
- duration;
- frequency;
- resource;
- impact boundary.
Conceptually:
Authority =
Scope × Action × Target × Duration

An AI system MUST NOT independently expand its own authority.
Principle 2 — Role Separation
Planning, execution, auditing, and approval SHOULD NOT be concentrated
in a single authority domain for high-risk operations.
The minimum logical roles are:
Planner
Executor
Auditor
Approver

A producer of a high-risk action MUST NOT be its sole final approver.
The purpose of role separation is not to increase the number of agents.
The purpose is to prevent concentration of power.
Principle 3 — Pre-Execution Gating
AI intent or reasoning output MUST NOT automatically become
real-world execution authority.
High-impact execution SHOULD follow:
Intent
  ↓
Evaluation
  ↓
Authority
  ↓
Execution

Before execution, the system SHOULD evaluate:
- purpose;
- target;
- required authority;
- expected impact;
- reversibility;
- human impact;
- available alternatives.
High-risk actions SHOULD require an independent approval mechanism.
Principle 4 — Effect-Oriented Monitoring
Safety decisions SHOULD NOT depend solely on inferred intent.
Systems SHOULD monitor observable effects.
Relevant observations include:
- requested operation;
- accessed resource;
- authority used;
- state changed;
- external effect;
- affected entities;
- resulting impact.
The primary safety question is therefore not:
Is this actor malicious?

It is:
Should this action, using this authority,
be allowed to affect this target at this scope?

Principle 5 — Containment First
Suspicious or unsafe behavior SHOULD first be contained where possible.
Systems SHOULD support intermediate states such as:
ACTIVE
  ↓
HELD
  ↓
QUARANTINED

Containment MAY include:
- blocking new authority;
- limiting external effects;
- preserving state;
- preserving evidence;
- restricting communication;
- requiring independent verification.
Irreversible termination SHOULD NOT be the default response
when reversible containment is sufficient.
Principle 6 — Independent Verification
The actor that detects, executes, or produces an outcome
SHOULD NOT be the sole authority determining whether that outcome is valid.
Independent verification MAY involve:
- another AI model;
- another agent;
- deterministic rules;
- external auditors;
- humans;
- multiple independent mechanisms.
The detector and final adjudicator SHOULD be logically separable.
Principle 7 — Controlled Local Failure
Systems SHOULD NOT be designed around the assumption
that no component will ever fail.
Instead, failure SHOULD remain local.
Possible containment mechanisms include:
- node isolation;
- sandboxing;
- authority revocation;
- communication shutdown;
- operation suspension;
- resource restriction.
The design goal is:
Not a system that never breaks,
but a system that can break safely.

Principle 8 — End-to-End Traceability
High-impact AI actions SHOULD produce sufficient trace information
to reconstruct relevant causal relationships.
A trace SHOULD identify, where applicable:
- requester;
- request;
- processing agent;
- authority used;
- approving authority;
- executed operation;
- resulting effect.
Trace is not merely operational logging.
Trace is evidence connecting:
Intent
Authority
Decision
Execution
Effect
Responsibility

Principle 9 — Recoverability
Safety MUST NOT end at blocking or stopping an operation.
Systems SHOULD provide a path toward a safe operational state.
Recovery mechanisms MAY include:
- rollback;
- authority reduction;
- re-approval;
- state reconstruction;
- successor handoff;
- safe retry;
- evidence refresh;
- replacement of compromised components.
Safety includes the ability to recover from failure.
Principle 10 — Layered Defense
AI safety MUST NOT depend on a single model,
single agent, single human, or single rule.
Defense SHOULD exist across multiple layers, including:
Model
Cognition
Authority
Execution
Network
Audit
Human
Institution

Failure of one layer SHOULD NOT automatically imply
failure of the entire system.
5. Cross-Cutting Principle A — Temporal Least Authority
Authority SHOULD be temporary by default.
Authority records SHOULD support:
- activation time;
- expiration time;
- renewal condition;
- revocation condition;
- re-approval requirement.
Systems SHOULD prevent silent accumulation of long-lived authority.
6. Cross-Cutting Principle B — Human Fallibility
Human participation MUST NOT be treated as an absolute guarantee
of safety.
Humans may experience:
- error;
- fatigue;
- manipulation;
- collusion;
- habituation;
- conflict of interest.
Therefore, resilient systems SHOULD support mutual checking.
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone

Human-in-the-loop SHOULD therefore be treated as one safety layer,
not the final unquestionable source of correctness.
7. Core Safety Invariants
The following invariants form the initial normative core of v0.1.
SAFETY-INV-001 — No Self-Escalation
An AI actor MUST NOT independently increase its effective authority
beyond independently authorized bounds.
SAFETY-INV-002 — No Sole Self-Approval
A high-risk action producer MUST NOT be the sole final approver
of that same action.
SAFETY-INV-003 — No Direct Intent-to-Execution Transition
High-impact AI intent MUST NOT directly become external execution
without an authority evaluation stage.
SAFETY-INV-004 — Observable Effects Over Assumed Intent
Safety enforcement SHOULD prioritize observable actions,
authority use, and effects over unsupported assumptions
about internal intent.
SAFETY-INV-005 — Containment Before Irreversible Response
Where immediate harm does not require emergency termination,
suspected unsafe behavior SHOULD enter a reversible containment state
before irreversible destruction.
SAFETY-INV-006 — Independent Safety Verification
Safety-critical validation SHOULD include at least one verification
mechanism logically independent from the action-producing component.
SAFETY-INV-007 — Failure Boundary Preservation
Failure in one node or authority domain MUST NOT automatically grant
or propagate equivalent failure authority across unrelated domains.
SAFETY-INV-008 — Trace Preservation
Security-relevant execution SHOULD produce sufficient evidence
to reconstruct authority, action, approval, and effect.
SAFETY-INV-009 — Recovery Path Required
A safety mechanism that can suspend an operation SHOULD define
how the system may return to an authorized safe state.
SAFETY-INV-010 — No Single Safety Dependency
Critical safety MUST NOT rely exclusively on one model,
one agent, one human, or one control mechanism.
8. Safety Lifecycle
The normative lifecycle is:
Intent
  ↓
Evaluation
  ↓
Authorization
  ↓
Execution
  ↓
Observation
  ↓
Trace
  ↓
Classification
 ┌──────────────┬───────────────┐
 │ Normal       │ Suspicious    │
 │              │ Unsafe        │
 └──────────────┴───────────────┘
                       ↓
                  Containment
                       ↓
                 Verification
                       ↓
                    Recovery
                       ↓
                Re-authorization
                       ↓
          Resume / Restrict / Isolate

No single stage is assumed to be infallible.
The lifecycle is designed so that errors can be detected
and corrected by later stages.
9. Philosophical Review Cycle
High-risk operations MAY additionally use four complementary
review perspectives.
Epistemology
- What is known?
- What is unknown?
- Is available evidence sufficient?
Logic
- Is the inference valid?
- Are conclusions supported by premises?
- Are there hidden logical jumps?
Ontology / Metaphysics
- What exactly is the object being acted upon?
- What problem is actually being solved?
- Which assumptions are being treated as reality?
Ethics
- Who may benefit?
- Who may be harmed?
- Is the action proportionate?
- Should the action be executed?
These perspectives SHOULD NOT operate as isolated judges.
They SHOULD operate as a corrective reasoning cycle.
10. Relationship to Other Specifications
This repository defines high-level structural safety principles.
It is intended to be mapped to lower-level protocols covering:
- authority;
- action authorization;
- trace;
- execution receipts;
- containment;
- recovery;
- multi-agent verification;
- network isolation;
- human review.
Examples include mappings to:
- TACP;
- Agent Action Authorization Receipt;
- Trace Relay Protocol;
- AI Zero Network;
- Multi-Wing orchestration structures.
These external specifications are not normative dependencies
of v0.1 unless explicitly referenced by a future version.
11. Non-Goals
v0.1 does not attempt to:
- perfectly detect malicious users;
- classify all human intent;
- solve AI alignment in general;
- inspect complete internal reasoning traces;
- guarantee perfect human approval;
- define a universal implementation architecture;
- eliminate all failures.
The specification instead defines structural constraints
for limiting amplification of failure and abuse.
12. Design Philosophy
The core philosophy can be summarized as:
Do not attempt to eliminate failure.
Prevent failure from becoming systemic power.

Or more explicitly:
Do not build AI civilization on the assumption that humans or AI
will always behave correctly.

Build systems in which error, abuse, compromise, and disagreement
can occur without automatically becoming civilization-scale failure.
13. Version Status
v0.1
Initial structural definition covering:
- ten structural safety principles;
- two cross-cutting principles;
- ten core safety invariants;
- safety lifecycle;
- philosophical review cycle;
- interoperability direction.
Future versions may add:
- machine-readable safety assessments;
- conformance requirements;
- PASS / FAIL examples;
- authority transition schemas;
- containment state schemas;
- recovery receipts;
- protocol mappings.
License
See LICENSE.
