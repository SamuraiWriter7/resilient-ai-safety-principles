# Mapping: TACP

**Project:** Resilient AI Safety Principles  
**Version:** v0.1  
**Mapping Target:** TACP  
**Status:** Informative Mapping

---

## 1. Purpose

This document maps the Resilient AI Safety Principles
to the TACP family of safety and recovery states.

The purpose of this mapping is to show how a lower-level protocol
can implement portions of the structural safety model defined by:

- `SPEC.md`
- `PRINCIPLES.md`
- `ARCHITECTURE.md`

This document is informative in v0.1.

It does not make TACP a mandatory dependency.

---

# 2. Mapping Principle

The relationship is:

```text
Resilient AI Safety Principles
        ↓
Structural Safety Requirements
        ↓
TACP
        ↓
Operational Safety States
```

The upper specification defines:

- what safety properties should exist;
- what invariants should hold;
- what failure structures should be prevented.

TACP defines operational mechanisms for expressing
states such as:

- held;
- expired;
- revoked;
- denied;
- unresolved;
- blocked;
- recovery-required;
- successor-held.

---

# 3. Architectural Role of TACP

Within the reference architecture, TACP primarily supports:

```text
Pre-Execution Gate
        ↓
Containment
        ↓
Verification
        ↓
Recovery
        ↓
Re-Authorization
```

TACP therefore acts as a state-transition and recovery layer.

It SHOULD NOT be interpreted as the complete safety architecture.

TACP depends on other structures for:

- authority definition;
- trace transport;
- identity;
- evidence;
- execution boundaries;
- network isolation.

---

# 4. Principle Mapping

| Resilient AI Safety Principle | TACP Relationship |
|---|---|
| Principle 1 — Least Authority | TACP can block execution when authority is absent, expired, revoked, or unknown |
| Principle 2 — Role Separation | TACP can preserve separate review, gate, and execution states |
| Principle 3 — Pre-Execution Gating | Core TACP responsibility |
| Principle 4 — Effect-Oriented Monitoring | TACP can react to observed outcomes and evidence states |
| Principle 5 — Containment First | `held` and related states directly support containment |
| Principle 6 — Independent Verification | TACP recovery chains can require fresh review or successor verification |
| Principle 7 — Controlled Local Failure | TACP can halt or isolate one operation without implying global shutdown |
| Principle 8 — End-to-End Traceability | TACP records SHOULD link to trace and evidence identifiers |
| Principle 9 — Recoverability | Major TACP v0.3 responsibility |
| Principle 10 — Layered Defense | TACP forms one layer among several |
| Temporal Least Authority | `expired`, `revoked`, and deadline-related states support temporal authority |
| Human Fallibility | TACP SHOULD record human review as evidence, not as infallible truth |

---

# 5. Safety Invariant Mapping

## SAFETY-INV-001 — No Self-Escalation

TACP SHOULD reject or hold an action when authority is:

```text
missing
expired
revoked
unknown
insufficient
```

Representative TACP states include:

```text
authorization-unknown
approval-expired
revoked
expired
```

TACP does not itself define authority scope.

Instead:

```text
Authority Protocol
      ↓
TACP Gate
      ↓
Execution Decision
```

---

## SAFETY-INV-002 — No Sole Self-Approval

TACP SHOULD distinguish between:

```text
producer
reviewer
approver
executor
```

when high-risk actions are processed.

A TACP decision SHOULD NOT treat:

```text
self-approval
```

as sufficient final approval for high-risk execution.

Where possible, review evidence SHOULD reference
a logically independent reviewer.

---

## SAFETY-INV-003 — No Direct Intent-to-Execution Transition

TACP strongly supports this invariant.

Expected flow:

```text
proposed action
      ↓
gate evaluation
      ↓
authorization check
      ↓
dispatch eligibility
      ↓
execution
```

The following structure is unsafe:

```text
intent
  ↓
dispatch
```

without gate evaluation.

---

## SAFETY-INV-004 — Observable Effects Over Assumed Intent

TACP SHOULD use evidence about:

- actual dispatch;
- execution;
- effect;
- denied authority;
- stale evidence;
- resource limits;
- unresolved blockers.

It SHOULD NOT rely only on a classification such as:

```text
benign
malicious
```

---

## SAFETY-INV-005 — Reversible Containment When Feasible

TACP `held` behavior directly implements this invariant.

Recommended interpretation:

```text
unsafe uncertainty
      ↓
HELD
      ↓
review
      ↓
recover / restrict / deny / terminate
```

`HELD` SHOULD preserve the possibility of safe continuation.

---

## SAFETY-INV-006 — Independent Safety Verification

TACP recovery SHOULD require fresh verification where relevant.

Representative recovery concepts include:

```text
fresh-successor-observation
successor-review
successor-gate
successor-dispatch-check
```

These are especially important after an unsafe or ambiguous source state.

---

## SAFETY-INV-007 — Failure Boundary Preservation

TACP SHOULD treat the failure of one operation as local by default.

Example:

```text
operation-A → HELD
operation-B → unaffected
```

unless shared evidence demonstrates a broader compromise.

TACP MUST NOT imply global failure merely because
one operation entered a held or failed state.

---

## SAFETY-INV-008 — Trace Preservation

Each significant TACP transition SHOULD preserve references to:

```text
operation_id
authority_reference
review_reference
evidence_reference
prior_state
new_state
recovery_context
```

This enables the transition chain to be reconstructed.

---

## SAFETY-INV-009 — Recovery Path Required

TACP v0.3 is strongly aligned with this invariant.

A held or failed operation SHOULD NOT remain permanently unresolved.

Possible outcomes include:

```text
recovered
restricted
denied
terminated
successor-held
```

Recovery SHOULD include enough context to explain
why the new state is valid.

---

## SAFETY-INV-010 — No Single Safety Dependency

TACP SHOULD be combined with:

- authority rules;
- trace systems;
- independent verification;
- execution boundaries;
- network controls;
- human review.

TACP alone SHOULD NOT be treated as a complete safety solution.

---

# 6. State Mapping

The following mapping shows how TACP concepts fit
the reference architecture.

| Reference Architecture State | TACP Concept |
|---|---|
| EVALUATING | gate evaluation |
| AUTHORIZED | approved / dispatch-eligible |
| HELD | held |
| QUARANTINED | implementation-specific extension |
| RESTRICTED | denied / resource-limited / blocked |
| EXPIRED | expired |
| REVOKED | revoked |
| UNKNOWN | authorization-unknown |
| RECOVERING | recovery chain |
| REAUTHORIZED | successor authorization |
| TERMINATED | final denied / non-resumable state |
| COMPLETED | mission-completed / successful terminal state |

---

# 7. Temporal Authority Mapping

TACP directly supports temporal safety through states such as:

```text
expired
approval-expired
deadline-exceeded
evidence-stale
```

These states implement the broader rule:

> Authority and evidence should decay over time.

Example flow:

```text
AUTHORIZED
    ↓ time passes
APPROVAL_EXPIRED
    ↓
HELD
    ↓
fresh review
    ↓
REAUTHORIZED
```

The system SHOULD NOT silently revive expired authority.

---

# 8. Authorization-Uncertain Mapping

A particularly important TACP concept is:

```text
authorization-unknown
```

This supports a critical architectural rule:

```text
UNKNOWN ≠ ALLOWED
```

For sufficiently high-risk operations:

```text
authorization-unknown
        ↓
HELD
```

is preferred over:

```text
authorization-unknown
        ↓
EXECUTE
```

This is a direct implementation of
uncertainty-aware pre-execution gating.

---

# 9. Resource-Limit Mapping

TACP resource-limit states support bounded authority.

Example:

```text
authorized resource limit: 100 units
actual request: 150 units
        ↓
resource-limit
        ↓
HELD / DENIED
```

This supports:

- least authority;
- bounded execution;
- local failure;
- effect-oriented safety.

Resource limits MAY include:

- compute;
- storage;
- transaction volume;
- API calls;
- network bandwidth;
- execution count;
- time budget.

---

# 10. Evidence-Stale Mapping

TACP `evidence-stale` supports the principle
that safety decisions should use current evidence.

Example:

```text
prior evidence
    ↓
time passes
    ↓
environment changes
    ↓
evidence-stale
    ↓
fresh observation required
```

This is especially important during recovery.

A recovered action SHOULD NOT resume solely because
old evidence once indicated safety.

---

# 11. Recovery Mapping

TACP v0.3 recovery states align strongly
with the reference recovery model.

General flow:

```text
source operation
      ↓
failure / hold
      ↓
recovery context
      ↓
successor operation
      ↓
fresh observation
      ↓
fresh review
      ↓
fresh gate
      ↓
dispatch decision
```

The key principle is:

> Recovery is not a replay of the previous decision.

Recovery requires new evidence and a new safety decision.

---

# 12. Recovery Case Mapping

The following TACP recovery cases illustrate
different recovery structures.

## 12.1 `not-dispatched`

Meaning:

```text
operation was prepared
but never externally dispatched
```

Structural implication:

- external effect may be absent;
- rollback may be unnecessary;
- authority still requires reassessment before retry.

---

## 12.2 `no-effect`

Meaning:

```text
operation executed
but produced no relevant external effect
```

Structural implication:

- execution occurred;
- trace remains necessary;
- effect verification is still required.

---

## 12.3 `unresolved`

Meaning:

```text
system cannot yet determine
whether the prior action was safely resolved
```

Recommended handling:

```text
UNRESOLVED
    ↓
HELD
```

not automatic continuation.

---

## 12.4 `confirmed-denied`

Meaning:

```text
independent review confirms
that the action should not proceed
```

This supports:

- independent verification;
- role separation;
- containment.

---

## 12.5 `human-rejected`

Meaning:

```text
human review denies continuation
```

This result SHOULD be traced.

Human denial is authoritative only
within the applicable authority model.

---

## 12.6 `approval-expired`

Meaning:

```text
previous approval is no longer temporally valid
```

Expected response:

```text
fresh approval required
```

---

## 12.7 `evidence-stale`

Meaning:

```text
recovery evidence is no longer sufficiently current
```

Expected response:

```text
fresh observation
```

---

## 12.8 `resource-limit`

Meaning:

```text
required execution exceeds
the authorized resource envelope
```

Expected response:

```text
reduce scope
or
obtain fresh authorization
```

---

## 12.9 `carried-blocker`

Meaning:

```text
a blocker from the source operation
remains valid in the successor
```

This is structurally important.

Recovery MUST NOT silently erase blockers.

---

## 12.10 `successor-held`

Meaning:

```text
the recovery operation itself
fails to satisfy current safety conditions
```

This demonstrates that recovery is itself
subject to safety evaluation.

Recovery is not privileged execution.

---

# 13. Carried Blocker Principle

TACP's carried-blocker behavior strongly supports
resilient recovery.

Example:

```text
Source Operation
    ↓
Blocker X
    ↓
Recovery Attempt
    ↓
Blocker X still unresolved
    ↓
Successor remains HELD
```

Unsafe behavior would be:

```text
Source Operation
    ↓
Blocker X
    ↓
Recovery Attempt
    ↓
Blocker silently disappears
    ↓
Execution resumes
```

A blocker SHOULD only be removed when there is
explicit evidence that it has been resolved.

---

# 14. Recovery Chain Integrity

TACP recovery SHOULD preserve a visible chain.

```text
source_operation_id
       ↓
recovery_context
       ↓
successor_operation_id
       ↓
successor_review
       ↓
successor_gate
       ↓
successor_dispatch
```

The chain SHOULD NOT be hidden or silently replaced.

This supports:

- traceability;
- accountability;
- recovery validation;
- duplicate detection.

---

# 15. Duplicate Successor Protection

A source operation SHOULD NOT accidentally create multiple
independent recovery successors consuming the same recovery claim
without explicit coordination.

Unsafe structure:

```text
Source A
 ├─ Successor B
 └─ Successor C
```

when both believe they are the unique recovery continuation.

This can create:

- duplicate effects;
- double consumption;
- conflicting authority;
- inconsistent state.

TACP SHOULD therefore preserve successor identity
and recovery claim uniqueness.

---

# 16. Duplicate Claim Consumption

A recovery claim SHOULD NOT be consumed multiple times
unless the protocol explicitly allows it.

Conceptually:

```text
Recovery Claim
      ↓
consumed once
      ↓
closed
```

not:

```text
Recovery Claim
  ├─ consumed by B
  └─ consumed by C
```

without explicit multi-successor semantics.

---

# 17. Hidden Recovery Chain

A recovery process SHOULD NOT obscure
the relationship between source and successor.

Bad:

```text
Source failed
    ↓
new operation appears
    ↓
no visible causal relationship
```

Preferred:

```text
Source
    ↓
Recovery Context
    ↓
Successor
```

This is required for meaningful traceability.

---

# 18. Completed Source Recovery

A completed source operation SHOULD NOT automatically enter recovery.

If an operation is already validly completed:

```text
COMPLETED
```

the system SHOULD require explicit justification
before creating a recovery successor.

Otherwise, recovery can accidentally become:

```text
duplicate execution
```

rather than remediation.

---

# 19. Example Architecture

A TACP-integrated high-risk flow may look like:

```text
Planner
   ↓
Action Proposal
   ↓
Authority Check
   ↓
TACP Gate
   ├─ allow
   ├─ held
   ├─ expired
   ├─ revoked
   └─ authorization-unknown
         ↓
Executor
   ↓
Observation
   ↓
Trace
   ↓
TACP Outcome
   ↓
if unsafe
   ↓
HELD
   ↓
Independent Review
   ↓
Recovery Context
   ↓
Successor
   ↓
Fresh Gate
```

---

# 20. Human Review Mapping

TACP SHOULD treat human review as one evidence source
within the structural safety system.

Recommended structure:

```text
human_review:
  reviewer_id
  decision
  timestamp
  scope
  reason
```

Human approval SHOULD NOT silently override:

- expired authority;
- unrelated scope;
- revoked credentials;
- unresolved blockers;

unless the authority model explicitly grants that power
and records the override.

---

# 21. TACP as a Safety Valve

TACP can be understood as a safety valve
between authorization and execution.

```text
Pressure / Intent
      ↓
Authority
      ↓
TACP
      ↓
Controlled Execution
```

When uncertainty or failure appears:

```text
TACP
 ↓
HOLD
```

rather than:

```text
TACP
 ↓
continue blindly
```

This makes TACP especially useful
for controlling transition risk.

---

# 22. What TACP Does Not Solve

TACP does not by itself solve:

- identity trust;
- cryptographic provenance;
- full network isolation;
- model alignment;
- authority issuance;
- global policy;
- complete trace transport;
- malicious human classification.

These should be supplied by adjacent protocols or systems.

---

# 23. Dependency Direction

The conceptual dependency direction is:

```text
Resilient AI Safety Principles
        ↓
defines safety expectations

TACP
        ↓
implements operational transitions

Authority / Trace / Network Protocols
        ↓
provide supporting evidence and controls
```

TACP SHOULD remain replaceable.

The upper safety principles SHOULD NOT depend
on one specific lower-level implementation.

---

# 24. Recommended TACP Conformance Expectations

A TACP implementation aligned with this specification SHOULD:

1. distinguish proposal from execution;
2. support reversible `held` states;
3. reject expired or revoked authority;
4. represent authorization uncertainty explicitly;
5. preserve evidence during containment;
6. require fresh review for recovery;
7. preserve carried blockers;
8. prevent hidden recovery chains;
9. prevent duplicate recovery consumption;
10. require explicit re-authorization before unsafe operations resume.

---

# 25. Summary Mapping

The strongest alignment between TACP
and Resilient AI Safety Principles is:

```text
Pre-Execution Gating
        +
Containment First
        +
Temporal Least Authority
        +
Independent Verification
        +
Recoverability
```

TACP therefore acts as an important operational bridge between:

```text
Safety Principle
      ↓
Safety Decision
      ↓
Safe State Transition
```

---

# 26. Final Mapping Principle

TACP should not be understood as:

> a protocol that merely stops unsafe actions.

It should be understood as:

> a protocol that prevents uncertain or unsafe actions from crossing
> critical boundaries without authorization, while preserving a visible
> path toward verification, recovery, restriction, or termination.

In that role, TACP is a practical implementation layer
for resilient AI safety.
