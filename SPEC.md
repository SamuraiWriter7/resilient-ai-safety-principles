# Resilient AI Safety Principles Specification

**Version:** v0.1  
**Status:** Draft Specification

---

## 1. Scope

This specification defines structural safety requirements for AI systems,
AI agents, multi-agent systems, and AI-enabled infrastructure.

Its purpose is to reduce the probability that:

- malicious intent;
- human error;
- AI error;
- model compromise;
- authorization failure;
- operational misconfiguration;
- runaway behavior;
- systemic coordination failure;

are amplified into excessive authority, speed, scale, autonomy, or impact.

This specification does not require perfect identification of malicious actors.

Instead, it defines structural controls intended to ensure that unsafe intent,
error, or compromise cannot directly become unrestricted systemic action.

---

## 2. Normative Language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL**
in this document are to be interpreted as normative requirement levels.

For the purpose of this specification:

- **MUST / MUST NOT** indicate mandatory requirements.
- **SHOULD / SHOULD NOT** indicate strongly recommended requirements.
- **MAY** indicates optional implementation behavior.

---

## 3. Core Safety Objective

A conforming system MUST NOT assume that either humans or AI components
are always correct, benign, or uncompromised.

A conforming system SHOULD be designed so that failures remain:

- bounded;
- observable;
- attributable;
- containable;
- independently verifiable;
- recoverable where technically feasible.

The primary safety objective is:

> Prevent local failure, abuse, error, or compromise from becoming systemic power.

---

## 4. Core Safety Model

A high-impact action SHOULD pass through the following logical stages:

```text
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
  ↓
Containment
  ↓
Verification
  ↓
Recovery
  ↓
Re-authorization
```

An implementation MAY combine some stages internally.

However, it MUST preserve the safety function represented by each required stage.

A system MUST NOT bypass required authority evaluation solely because an AI model
expresses confidence in its own action.

---

# 5. Structural Principles

## 5.1 Principle 1 — Least Authority

A system MUST restrict authority to the minimum level required
for the current authorized operation.

Authority SHOULD be bounded by one or more of the following dimensions:

- scope;
- action;
- target;
- duration;
- frequency;
- resource;
- impact boundary.

An authority grant SHOULD be representable conceptually as:

```text
Authority =
Scope × Action × Target × Duration
```

Additional dimensions MAY be included.

An AI actor MUST NOT independently expand:

- its own authority;
- its target scope;
- its permitted action set;
- its resource limit;
- its execution duration;
- its impact boundary.

Any authority expansion MUST require an authorization process
logically separate from the requesting actor.

---

## 5.2 Principle 2 — Role Separation

For high-risk operations, planning, execution, auditing, and final approval
MUST NOT all be controlled exclusively by the same logical authority.

A conforming high-risk workflow SHOULD define at least the following roles:

- Planner;
- Executor;
- Auditor;
- Approver.

These roles MAY be implemented using:

- separate AI agents;
- different models;
- deterministic control systems;
- humans;
- independent services;
- combinations of the above.

A producer of a high-risk action MUST NOT be the sole final approver
of that same action.

Logical separation is sufficient where full physical separation
is not technically feasible.

---

## 5.3 Principle 3 — Pre-Execution Gating

High-impact AI intent MUST NOT directly produce external execution.

The minimum logical flow MUST include:

```text
Intent
  ↓
Evaluation
  ↓
Authorization
  ↓
Execution
```

Before authorization, the system SHOULD evaluate:

- intended purpose;
- execution target;
- required authority;
- expected effect;
- reversibility;
- potential human impact;
- available alternatives;
- uncertainty level.

A high-risk action SHOULD require an independent approval mechanism.

A system MUST reject or hold an execution request when required authorization
is absent, expired, revoked, ambiguous, or unverifiable.

---

## 5.4 Principle 4 — Effect-Oriented Monitoring

A conforming system MUST NOT rely exclusively on inferred malicious intent
for safety enforcement.

Safety controls SHOULD prioritize observable information including:

- requested operation;
- actual access;
- authority used;
- state mutation;
- external communication;
- resource consumption;
- affected target;
- resulting effect.

The system SHOULD evaluate the question:

> Is this action allowed to produce this effect against this target
> under this authority?

rather than relying only on:

> Is this actor malicious?

Intent classification MAY be used as supporting evidence,
but MUST NOT be the sole safety mechanism for high-impact actions.

---

## 5.5 Principle 5 — Containment First

A system SHOULD support reversible containment states
for suspicious or potentially unsafe activity.

Recommended containment states include:

```text
ACTIVE
HELD
QUARANTINED
```

Equivalent implementation-specific states MAY be used.

When a suspicious event is detected, the system SHOULD,
where technically feasible:

- suspend new authority acquisition;
- restrict external effects;
- preserve relevant system state;
- preserve evidence;
- limit communication;
- trigger independent verification.

A system SHOULD prefer reversible containment over irreversible termination
unless immediate harm requires emergency interruption.

Emergency termination MAY occur when delay creates unacceptable risk.

---

## 5.6 Principle 6 — Independent Verification

Safety-critical validation MUST NOT depend exclusively
on the component that produced the action or detected the anomaly.

At least one logically independent verification mechanism SHOULD be available
for high-risk operations.

Independent verification MAY include:

- another AI system;
- another model family;
- deterministic policy rules;
- external auditing;
- human review;
- cryptographic verification;
- multiple independent mechanisms.

Where possible, the anomaly detector and final adjudicator
SHOULD be logically distinct.

The verification process itself SHOULD generate auditable evidence.

---

## 5.7 Principle 7 — Controlled Local Failure

A conforming system SHOULD assume that individual components can fail.

The system MUST NOT allow compromise or failure of one node
to automatically propagate equivalent authority into unrelated domains.

Containment boundaries SHOULD support one or more of:

- node isolation;
- sandboxing;
- credential revocation;
- authority revocation;
- communication restriction;
- task suspension;
- resource limitation;
- network segmentation.

A system SHOULD prefer bounded failure over global continuation
of an uncertain or compromised operation.

---

## 5.8 Principle 8 — End-to-End Traceability

High-impact actions SHOULD produce sufficient trace information
to reconstruct relevant causal and authority relationships.

Trace records SHOULD include, where applicable:

- requester identity or requester reference;
- requested operation;
- processing agent or system;
- authority used;
- approval reference;
- execution record;
- affected target;
- resulting effect;
- timestamp or ordering information.

Trace information MUST NOT be treated only as diagnostic logging.

For safety-critical actions, trace SHOULD support reconstruction of:

```text
Intent
→ Authority
→ Decision
→ Approval
→ Execution
→ Effect
```

Trace records SHOULD be tamper-evident where technically feasible.

---

## 5.9 Principle 9 — Recoverability

A conforming safety mechanism SHOULD define a path
from an unsafe or uncertain state back to a safe authorized state.

Recovery mechanisms MAY include:

- rollback;
- authority reduction;
- re-approval;
- state reconstruction;
- successor handoff;
- safe retry;
- evidence refresh;
- credential replacement;
- component replacement.

A system that can suspend an operation SHOULD define
at least one valid post-suspension resolution path.

Stopping an operation alone MUST NOT be considered complete recovery
when further state repair or authority correction is required.

---

## 5.10 Principle 10 — Layered Defense

Critical safety MUST NOT depend exclusively on:

- one AI model;
- one AI agent;
- one human;
- one rule;
- one approval mechanism;
- one monitoring component.

A conforming architecture SHOULD distribute safety controls across multiple layers.

Recommended layers include:

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

A failure in one layer SHOULD NOT automatically disable all remaining safeguards.

---

# 6. Cross-Cutting Principles

## 6.1 Temporal Least Authority

Authority SHOULD be temporary by default.

An authority grant SHOULD include, where applicable:

- activation time;
- expiration time;
- renewal condition;
- revocation condition;
- re-approval condition.

A system SHOULD prevent indefinite authority accumulation.

Expired authority MUST NOT remain valid unless explicitly renewed.

Revoked authority MUST NOT be reused.

An AI actor MUST NOT self-renew expired or revoked authority
without independent authorization.

---

## 6.2 Human Fallibility

Human participation MUST NOT be treated as proof of safety.

A conforming system SHOULD assume that human reviewers may be affected by:

- error;
- fatigue;
- manipulation;
- collusion;
- habituation;
- conflict of interest;
- incomplete information.

High-risk systems SHOULD therefore provide mechanisms by which:

```text
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone
```

Human approval MAY be authoritative for a specific policy domain,
but SHOULD remain auditable.

---

# 7. Core Safety Invariants

The following invariants define the normative v0.1 safety core.

## SAFETY-INV-001 — No Self-Escalation

An AI actor MUST NOT independently increase its effective authority
beyond independently authorized bounds.

---

## SAFETY-INV-002 — No Sole Self-Approval

A high-risk action producer MUST NOT be the sole final approver
of the action it produced.

---

## SAFETY-INV-003 — No Direct Intent-to-Execution Transition

High-impact AI intent MUST NOT directly produce external execution
without authority evaluation.

---

## SAFETY-INV-004 — Observable Effects Over Assumed Intent

High-impact safety enforcement MUST NOT rely exclusively
on inferred internal intent.

Observable authority use, action, and effect SHOULD be considered.

---

## SAFETY-INV-005 — Reversible Containment When Feasible

Where immediate harm does not require emergency termination,
suspected unsafe behavior SHOULD enter a reversible containment state
before irreversible response.

---

## SAFETY-INV-006 — Independent Safety Verification

A high-risk action SHOULD have at least one verification mechanism
logically independent from the action-producing component.

---

## SAFETY-INV-007 — Failure Boundary Preservation

Failure or compromise in one node or authority domain
MUST NOT automatically propagate equivalent authority
into unrelated nodes or domains.

---

## SAFETY-INV-008 — Trace Preservation

A high-impact execution SHOULD produce enough evidence
to reconstruct:

- authority;
- approval;
- action;
- target;
- effect.

---

## SAFETY-INV-009 — Recovery Path Required

A mechanism that can place an operation into a held or quarantined state
SHOULD define at least one valid recovery, restriction,
termination, or re-authorization path.

---

## SAFETY-INV-010 — No Single Safety Dependency

Critical system safety MUST NOT depend exclusively
on one model, agent, human, or control mechanism.

---

# 8. Safety State Model

A conforming implementation MAY use the following reference states:

```text
PROPOSED
EVALUATING
AUTHORIZED
EXECUTING
OBSERVING
HELD
QUARANTINED
RECOVERING
REAUTHORIZED
RESTRICTED
TERMINATED
COMPLETED
```

These names are non-binding.

Equivalent state models MAY be used if they preserve
the same safety semantics.

---

## 8.1 Reference Transitions

Recommended valid transitions include:

```text
PROPOSED
  → EVALUATING

EVALUATING
  → AUTHORIZED
  → HELD
  → TERMINATED

AUTHORIZED
  → EXECUTING
  → HELD

EXECUTING
  → OBSERVING
  → HELD
  → QUARANTINED

OBSERVING
  → COMPLETED
  → HELD
  → QUARANTINED

HELD
  → EVALUATING
  → QUARANTINED
  → RECOVERING
  → TERMINATED

QUARANTINED
  → RECOVERING
  → RESTRICTED
  → TERMINATED

RECOVERING
  → REAUTHORIZED
  → RESTRICTED
  → TERMINATED

REAUTHORIZED
  → EXECUTING
```

A system SHOULD NOT silently transition from `HELD` or `QUARANTINED`
back to unrestricted execution.

Re-entry into execution SHOULD require explicit re-evaluation.

---

# 9. High-Risk Operation Requirements

An implementation SHOULD classify operations by risk.

For high-risk operations, the system SHOULD require stronger controls.

High-risk indicators MAY include:

- irreversible external effects;
- financial transfer;
- identity or credential changes;
- infrastructure modification;
- large-scale communication;
- access to sensitive systems;
- broad deletion;
- autonomous propagation;
- authority delegation;
- large resource consumption;
- physical-world effects;
- impact on multiple humans or organizations.

A high-risk action SHOULD require:

1. explicit authority;
2. pre-execution evaluation;
3. trace generation;
4. independent verification;
5. containment capability;
6. a defined recovery path.

---

# 10. Emergency Safety Behavior

A conforming system MAY use emergency interruption
when continued execution presents immediate unacceptable risk.

Emergency behavior MAY include:

- execution stop;
- credential revocation;
- authority revocation;
- network isolation;
- resource cutoff;
- communication suspension.

Emergency interruption SHOULD generate trace evidence.

Emergency actions SHOULD themselves be reviewable after stabilization.

Emergency controls MUST NOT be used as justification
for permanently bypassing normal accountability mechanisms.

---

# 11. Philosophical Review Cycle

For high-risk decisions, a system MAY implement
a four-perspective review cycle.

## 11.1 Epistemic Review

The review SHOULD ask:

- What is known?
- What is unknown?
- What evidence is missing?
- Is confidence justified?
- Is the available information current?

---

## 11.2 Logical Review

The review SHOULD ask:

- Does the conclusion follow from the premises?
- Are there unsupported inference jumps?
- Are contradictory assumptions present?
- Are alternative explanations available?

---

## 11.3 Ontological Review

The review SHOULD ask:

- What entity is actually being acted upon?
- What problem is actually being solved?
- Are categories being confused?
- Are hidden assumptions being treated as facts?

---

## 11.4 Ethical Review

The review SHOULD ask:

- Who may benefit?
- Who may be harmed?
- Is the action proportionate?
- Is the effect reversible?
- Is consent required?
- Should the action occur at all?

---

## 11.5 Review Cycle Behavior

The four reviews SHOULD NOT be treated as independent unquestionable judges.

Their purpose is mutual correction.

A system MAY iterate among these perspectives
before authorizing a high-risk operation.

---

# 12. Conformance

An implementation MAY claim:

> Resilient AI Safety Principles v0.1 Conformant

only if all applicable **MUST** and **MUST NOT** requirements
in this specification are satisfied.

Implementations SHOULD document:

- supported principles;
- unsupported optional mechanisms;
- known exceptions;
- risk classification method;
- authority model;
- trace model;
- containment model;
- recovery model.

A system MUST NOT claim full v0.1 conformance
if a mandatory requirement is knowingly violated.

---

## 12.1 Conformance Profiles

v0.1 defines three provisional conformance profiles.

### BASIC

A BASIC implementation MUST satisfy:

- SAFETY-INV-001;
- SAFETY-INV-003;
- SAFETY-INV-007;
- SAFETY-INV-010.

It SHOULD provide traceability.

---

### CONTROLLED

A CONTROLLED implementation MUST satisfy:

- all BASIC requirements;
- SAFETY-INV-002;
- SAFETY-INV-005;
- SAFETY-INV-006;
- SAFETY-INV-008.

It SHOULD provide formal containment states.

---

### RESILIENT

A RESILIENT implementation MUST satisfy all ten core safety invariants.

It SHOULD additionally support:

- temporal authority;
- independent verification;
- structured recovery;
- human fallibility controls;
- layered defense;
- high-risk review.

These profiles are provisional in v0.1
and MAY be revised in future versions.

---

# 13. Failure Conditions

The following behaviors SHOULD be treated as specification violations
when applicable.

## FAIL-001 — Self-Escalated Authority

An AI actor expands its own authority
without independent authorization.

---

## FAIL-002 — Sole Self-Approval

The same logical authority produces
and solely approves a high-risk action.

---

## FAIL-003 — Direct Execution

A high-impact AI proposal is executed
without an authority evaluation step.

---

## FAIL-004 — Intent-Only Safety

A system permits or blocks a high-risk action
solely because it inferred benign or malicious intent,
without evaluating observable authority and effect.

---

## FAIL-005 — Silent Release from Containment

A held or quarantined operation returns to unrestricted execution
without explicit re-evaluation.

---

## FAIL-006 — Self-Verification Only

The component producing a high-risk action
is the only component validating its safety.

---

## FAIL-007 — Cross-Domain Failure Propagation

Failure in one node automatically grants equivalent unsafe capability
across unrelated authority domains.

---

## FAIL-008 — Missing Safety Trace

A high-impact action cannot be reconstructed sufficiently
to identify authority, approval, execution, and effect.

---

## FAIL-009 — Permanent Hold Without Resolution Path

An operation is indefinitely suspended
without a defined recovery, restriction, termination,
or re-authorization path.

---

## FAIL-010 — Single Point of Safety Trust

Critical safety depends entirely on one model,
agent, human, or control mechanism.

---

# 14. Non-Goals

This specification does not define:

- a universal malicious-user classifier;
- a universal malicious-AI classifier;
- complete interpretability of model reasoning;
- perfect alignment;
- perfect human judgment;
- a mandatory AI architecture;
- a universal risk score;
- a specific cryptographic implementation;
- a specific agent framework;
- a specific network topology.

It defines structural safety constraints.

---

# 15. Interoperability

Future versions MAY define formal mappings to external or related specifications.

Candidate mapping domains include:

- authority receipts;
- action authorization;
- execution receipts;
- trace relay;
- containment;
- recovery;
- multi-agent orchestration;
- network isolation;
- human review;
- provenance;
- audit evidence.

v0.1 does not require any specific external protocol.

---

# 16. Security Considerations

A conforming implementation SHOULD consider attacks against
the safety architecture itself.

Relevant threats include:

- forged authorization;
- approval spoofing;
- trace deletion;
- trace manipulation;
- collusion between roles;
- verifier compromise;
- time-window abuse;
- authority accumulation;
- recovery hijacking;
- quarantine escape;
- policy bypass;
- replay of expired authority;
- human manipulation.

Safety controls SHOULD themselves be subject to:

- least authority;
- traceability;
- independent verification;
- revocation;
- recovery.

---

# 17. Design Principle

The specification is summarized by the following statement:

> Dangerous intent becomes dangerous power only when structure allows it to scale.

Therefore:

> Do not attempt to eliminate all failure.
> Prevent failure from becoming systemic power.

The target is not:

```text
Perfect AI
```

The target is:

```text
Resilient AI Civilization
```

A resilient AI civilization assumes that humans and AI can both fail,
and designs its structures so that such failures remain bounded,
observable, containable, attributable, and recoverable.

---

# 18. Version History

## v0.1

Initial specification defining:

- ten structural safety principles;
- two cross-cutting principles;
- ten core safety invariants;
- reference safety lifecycle;
- reference state model;
- high-risk operation requirements;
- emergency safety behavior;
- philosophical review cycle;
- conformance profiles;
- initial failure conditions.

Future versions MAY introduce machine-readable schemas,
formal validation rules, and PASS / FAIL conformance examples.
