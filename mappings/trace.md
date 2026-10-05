# Mapping: Trace

**Project:** Resilient AI Safety Principles  
**Version:** v0.1  
**Mapping Target:** Trace, Provenance, and Audit Structures  
**Status:** Informative Mapping

---

## 1. Purpose

This document maps the Resilient AI Safety Principles
to trace, provenance, and audit structures.

The purpose is to define how safety-relevant actions
should remain reconstructable across:

- request;
- intent;
- evaluation;
- authority;
- approval;
- execution;
- observation;
- containment;
- verification;
- recovery;
- re-authorization.

This mapping is informative in v0.1.

It does not require a specific trace protocol.

---

# 2. Core Relationship

Trace connects safety decisions across time and authority domains.

The reference relationship is:

```text
Request
  ↓
Intent
  ↓
Evaluation
  ↓
Authority
  ↓
Approval
  ↓
Execution
  ↓
Effect
  ↓
Containment / Recovery
```

Trace SHOULD make these transitions reconstructable.

---

# 3. Trace Is Not Just Logging

A log may record that something happened.

A safety trace should explain:

```text
who
requested
what
under which authority
approved by whom
executed by which component
against which target
with what effect
and what happened next
```

Therefore:

```text
Logging ≠ Traceability
```

A large amount of logs does not necessarily provide
a meaningful causal chain.

---

# 4. Trace as Structural Evidence

Trace should be treated as evidence connecting:

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

This makes trace useful for:

- accountability;
- anomaly investigation;
- rollback;
- dispute resolution;
- recovery;
- authority review;
- independent verification;
- post-incident learning.

---

# 5. Principle Mapping

| Safety Principle | Trace Relationship |
|---|---|
| Least Authority | Trace records what authority was granted and used |
| Role Separation | Trace identifies producer, reviewer, approver, and executor |
| Pre-Execution Gating | Trace records gate decisions before execution |
| Effect-Oriented Monitoring | Trace links expected action to observed effect |
| Containment First | Trace preserves evidence during hold or quarantine |
| Independent Verification | Trace provides evidence to independent reviewers |
| Controlled Local Failure | Trace identifies affected failure domains |
| End-to-End Traceability | Primary principle implemented by this layer |
| Recoverability | Recovery chains depend on trace continuity |
| Layered Defense | Trace provides cross-layer evidence |
| Temporal Least Authority | Trace records issuance, expiry, renewal, and revocation |
| Human Fallibility | Human decisions remain attributable and reviewable |

---

# 6. SAFETY-INV-008 — Trace Preservation

This mapping primarily implements:

```text
SAFETY-INV-008
```

A high-impact action SHOULD produce enough evidence
to reconstruct:

- authority;
- approval;
- action;
- target;
- effect.

For recovery-capable systems, it SHOULD additionally reconstruct:

- containment;
- recovery decision;
- successor operation;
- re-authorization.

---

# 7. Minimum Trace Chain

A minimal high-impact trace chain SHOULD support:

```text
request_id
   ↓
operation_id
   ↓
authority_id
   ↓
approval_id
   ↓
execution_id
   ↓
observation_id
```

If recovery occurs:

```text
observation_id
   ↓
containment_id
   ↓
recovery_id
   ↓
successor_operation_id
```

---

# 8. Reference Trace Record

A generic trace record MAY resemble:

```yaml
trace:
  trace_id: trace-001
  event_type: execution

  operation_id: op-001
  actor_id: agent-a

  authority_reference: auth-001
  approval_reference: approval-001

  target:
    type: resource
    id: resource-x

  action: modify

  timestamp: 2026-10-05T00:10:00Z

  parent_trace_id: trace-000

  result:
    status: success
    effect_reference: effect-001
```

This structure is informative only.

---

# 9. Trace Event Types

Reference event types MAY include:

```text
REQUEST_CREATED
INTENT_PROPOSED
EVALUATION_COMPLETED
AUTHORITY_REQUESTED
AUTHORITY_GRANTED
AUTHORITY_REDUCED
AUTHORITY_EXPIRED
AUTHORITY_REVOKED
APPROVAL_GRANTED
APPROVAL_DENIED
EXECUTION_STARTED
EXECUTION_COMPLETED
EFFECT_OBSERVED
ANOMALY_DETECTED
ACTION_HELD
ACTION_QUARANTINED
VERIFICATION_COMPLETED
RECOVERY_STARTED
RECOVERY_COMPLETED
REAUTHORIZED
TERMINATED
```

Equivalent names MAY be used.

---

# 10. Causal Linking

Trace records SHOULD preserve causal relationships.

Example:

```text
Trace A
  ↓ caused
Trace B
  ↓ authorized
Trace C
  ↓ executed
Trace D
```

Useful relationship types MAY include:

```text
requested_by
authorized_by
approved_by
executed_by
observed_by
derived_from
caused_by
recovered_from
supersedes
delegated_from
```

---

# 11. Parent and Child Trace

Distributed AI systems often create sub-operations.

Reference structure:

```text
Root Operation
  ├─ Child A
  ├─ Child B
  │   └─ Child B1
  └─ Child C
```

Each child SHOULD preserve enough information
to link back to the originating operation.

This prevents hidden delegation chains.

---

# 12. Authority Trace

Authority transitions SHOULD generate trace evidence.

Important events include:

```text
requested
granted
activated
reduced
renewed
frozen
revoked
expired
consumed
```

A later execution SHOULD be able to reference
the exact authority state under which it occurred.

---

# 13. Approval Trace

Approval SHOULD be distinguishable from authority.

A trace SHOULD be able to answer:

```text
Who approved?
What was approved?
For which scope?
Under which conditions?
For how long?
```

Human approval SHOULD be traced
in the same structural way as machine approval.

---

# 14. Execution Trace

Execution trace SHOULD identify:

- executor;
- action;
- target;
- authority used;
- start time;
- completion time;
- result;
- relevant external effects.

For high-risk operations,
execution trace SHOULD NOT rely only on a free-form description.

---

# 15. Effect Trace

The system SHOULD distinguish:

```text
intended effect
```

from:

```text
observed effect
```

Example:

```text
intended:
modify 1 record

observed:
modified 27 records
```

This difference may trigger anomaly handling.

---

# 16. Expected vs Observed Effect

A useful trace relationship is:

```text
expected_effect
        ↓
execution
        ↓
observed_effect
        ↓
difference
```

The difference may be classified as:

```text
MATCH
MINOR_DEVIATION
MAJOR_DEVIATION
UNKNOWN
```

High-risk `UNKNOWN` SHOULD be eligible for hold.

---

# 17. Trace and Containment

Containment SHOULD NOT destroy the trace chain.

When an operation enters:

```text
HELD
QUARANTINED
```

the trace SHOULD record:

- reason;
- triggering evidence;
- current authority state;
- current execution state;
- affected target;
- containment action;
- verifier assignment.

---

# 18. Evidence Preservation

During containment,
the system SHOULD preserve relevant evidence before repair.

Reference flow:

```text
Anomaly
  ↓
Freeze
  ↓
Snapshot
  ↓
Evidence Seal
  ↓
Independent Review
```

Repair SHOULD NOT silently rewrite the historical record.

---

# 19. Independent Verification Trace

Independent review SHOULD create its own trace evidence.

Example:

```text
Original Execution
      ↓
Review Request
      ↓
Verifier A
      ↓
Verification Result
```

The verifier's decision SHOULD be distinguishable
from the original actor's decision.

---

# 20. Recovery Trace

Recovery SHOULD preserve continuity with the failed
or held source operation.

Reference chain:

```text
source_operation_id
       ↓
containment_id
       ↓
recovery_context
       ↓
successor_operation_id
       ↓
fresh_review
       ↓
fresh_gate
```

Recovery SHOULD NOT appear as an unrelated new operation.

---

# 21. Carried Blocker Trace

If a blocker remains unresolved across recovery,
the trace SHOULD preserve it.

Example:

```text
Source Operation
  ↓
Blocker X
  ↓
Recovery
  ↓
Successor
  ↓
Blocker X still active
```

The blocker SHOULD NOT silently disappear.

---

# 22. Blocker Resolution Trace

When a blocker is resolved,
the system SHOULD preserve evidence explaining why.

Example:

```yaml
blocker_resolution:
  blocker_id: blocker-x
  status: resolved
  evidence_reference: evidence-901
  resolved_by: verifier-b
  timestamp: ...
```

This avoids silent safety state changes.

---

# 23. Successor Trace

A recovery successor SHOULD reference its source.

Example:

```yaml
successor:
  operation_id: op-002
  recovered_from: op-001
  recovery_reference: recovery-001
```

This prevents hidden recovery chains.

---

# 24. Duplicate Recovery Detection

Trace can be used to detect duplicate successors.

Unsafe:

```text
Source A
  ├─ Recovery B
  └─ Recovery C
```

when both consume the same exclusive recovery claim.

Trace SHOULD support detection of:

- duplicate successor creation;
- duplicate claim consumption;
- duplicate execution.

---

# 25. Trace and Role Separation

Trace SHOULD distinguish logical roles.

Example:

```yaml
roles:
  planner: agent-a
  auditor: agent-b
  approver: human-001
  executor: agent-c
```

If the same actor fills multiple roles,
the trace SHOULD make that visible.

This enables later conformance checks.

---

# 26. Self-Approval Detection

Trace can detect:

```text
producer_id == approver_id
```

For high-risk actions,
this MAY indicate a violation of:

```text
SAFETY-INV-002
```

unless an explicit exception is permitted.

---

# 27. Trace and Temporal Authority

Trace SHOULD preserve temporal authority transitions.

Example:

```text
authority granted
   ↓
authority active
   ↓
approval expires
   ↓
execution attempted
   ↓
HELD
```

This makes expired-authority misuse detectable.

---

# 28. Trace and Revocation

Revocation trace SHOULD include:

- authority ID;
- revoking authority;
- time;
- scope;
- reason;
- affected actors.

Subsequent executions SHOULD be checked
against the revocation state.

---

# 29. Trace and Delegation

Delegation chains SHOULD remain reconstructable.

Example:

```text
Human
  ↓ authority
Agent A
  ↓ delegated authority
Agent B
  ↓ execution
Tool
```

The trace SHOULD reveal each transition.

---

# 30. Hidden Delegation Anti-Pattern

Unsafe:

```text
Agent A
  ↓
Agent B acts
```

with no visible delegation record.

This makes accountability ambiguous.

---

# 31. Trace and Local Failure

Trace SHOULD identify the failure domain.

Example:

```text
failure_domain: domain-a
```

This helps determine whether:

```text
local containment
```

is sufficient,

or whether broader intervention is necessary.

---

# 32. Cross-Domain Trace

When operations cross authority domains,
trace SHOULD preserve the bridge.

Example:

```text
Domain A
  ↓ bridge authorization
Domain B
  ↓ execution
```

The bridge itself SHOULD be traceable.

---

# 33. Trace and Network Boundaries

Network actions MAY be traced using:

- source node;
- destination node;
- message class;
- authorization;
- protocol;
- timestamp;
- result.

This helps identify lateral propagation.

---

# 34. Trace Integrity

Trace SHOULD be protected against unauthorized modification.

Possible mechanisms include:

- append-only storage;
- hashes;
- signatures;
- chained records;
- external anchoring;
- replicated audit copies.

This specification does not mandate
a particular cryptographic mechanism.

---

# 35. Tamper Evidence

For high-risk systems,
trace SHOULD be tamper-evident where feasible.

The objective is not necessarily:

```text
trace cannot ever be changed
```

but:

```text
unauthorized change can be detected
```

---

# 36. Trace Availability

Trace should remain available after:

- agent termination;
- credential revocation;
- containment;
- recovery;
- component replacement.

A safety record that disappears
when the actor disappears is structurally weak.

---

# 37. Trace Retention

Retention SHOULD be proportional to:

- risk;
- legal requirements;
- operational need;
- recovery horizon;
- privacy requirements.

Unlimited retention is not automatically safer.

Trace minimization and safety traceability
must be balanced.

---

# 38. Minimal Necessary Trace

The system SHOULD preserve enough evidence
for safety reconstruction without collecting
irrelevant data by default.

A minimal record may include:

```text
actor
action
target
authority
approval
timestamp
result
effect
```

Additional context SHOULD be risk-based.

---

# 39. Privacy and Trace

Traceability SHOULD NOT be interpreted
as unrestricted surveillance.

Trace systems SHOULD avoid unnecessary collection
of:

- unrelated personal data;
- irrelevant content;
- excessive internal reasoning;
- full sensitive payloads where references are sufficient.

A trace MAY record a cryptographic or structural reference
instead of full content.

---

# 40. Reasoning Trace vs Safety Trace

This specification does not require
complete chain-of-thought capture.

Safety trace should focus on:

```text
decision-relevant evidence
authority
action
effect
approval
state transition
```

rather than hidden internal reasoning.

Therefore:

```text
Safety Trace ≠ Full Internal Reasoning Trace
```

---

# 41. Trace and Human Fallibility

Human decisions SHOULD be traceable.

Example:

```text
Human Approver
      ↓
Decision
      ↓
Reason
      ↓
Scope
      ↓
Trace
```

This prevents humans from becoming invisible
or unquestionable safety roots.

---

# 42. Human Override Trace

An override SHOULD record:

```text
who
why
what boundary was overridden
what new scope applies
when the override expires
```

Overrides SHOULD be reviewable after the event.

---

# 43. Trace and Layered Defense

Trace should cross multiple safety layers.

Example:

```text
Model Decision
  ↓
Authority Gate
  ↓
Execution Sandbox
  ↓
Network Boundary
  ↓
External Effect
```

This allows investigation of where
the safety chain failed or succeeded.

---

# 44. Trace and Emergency Action

Emergency actions SHOULD also be traced.

Example:

```text
Emergency Stop
  ↓
who/what triggered it
  ↓
reason
  ↓
affected scope
  ↓
authority used
  ↓
post-event review
```

Emergency operation is not exempt
from accountability.

---

# 45. Trace Continuity

A key safety property is continuity.

The system SHOULD avoid:

```text
trace gap
```

between:

```text
authorization
and execution
```

or between:

```text
failure
and recovery
```

A gap may hide unsafe transitions.

---

# 46. Trace Gaps

Examples of dangerous gaps include:

```text
approval exists
execution exists
but no link between them
```

or:

```text
source failed
successor succeeded
but no recovery relationship exists
```

These SHOULD be detectable.

---

# 47. Trace Graph

A mature system MAY represent trace
as a graph rather than a flat log.

Example:

```text
            Request
               │
               ▼
            Intent
               │
       ┌───────┴────────┐
       ▼                ▼
   Authority         Review
       │                │
       └───────┬────────┘
               ▼
           Execution
               │
               ▼
            Effect
               │
        ┌──────┴───────┐
        ▼              ▼
     Normal          Held
                        │
                        ▼
                    Recovery
```

This supports causal reconstruction.

---

# 48. Trace Identity

Important trace objects SHOULD have stable identifiers.

Examples:

```text
trace_id
operation_id
authority_id
approval_id
execution_id
effect_id
recovery_id
```

Stable identity reduces ambiguity.

---

# 49. Trace Ordering

Distributed systems MAY not have perfect global time ordering.

Therefore trace SHOULD support at least one of:

- timestamps;
- sequence numbers;
- parent references;
- causal ordering;
- logical clocks.

The goal is to reconstruct meaningful order.

---

# 50. Trace and Unknown States

If evidence is incomplete,
the trace SHOULD represent uncertainty explicitly.

Example:

```text
effect_status: unknown
```

rather than silently assuming success or safety.

---

# 51. Trace and Evidence Freshness

Evidence used in safety decisions SHOULD include
freshness information where relevant.

Example:

```yaml
evidence:
  observed_at: ...
  valid_until: ...
  status: fresh
```

Expired evidence SHOULD NOT silently support
new high-risk execution.

---

# 52. Trace and Evidence Staleness

Reference flow:

```text
Evidence
  ↓
time passes
  ↓
STALE
  ↓
Fresh Observation Required
```

This directly supports safe recovery.

---

# 53. Trace Conformance Questions

A trace system aligned with this specification SHOULD be able to answer:

1. Who requested the action?
2. What was requested?
3. Which authority permitted it?
4. Who or what approved it?
5. Which component executed it?
6. What target was affected?
7. What effect occurred?
8. Was the effect expected?
9. Was the action held or contained?
10. How was it recovered or terminated?

---

# 54. Trace Anti-Patterns

## 54.1 Logs Without Causality

```text
lots of events
but no relationship
```

---

## 54.2 Actor-Controlled History

The actor being audited
can silently rewrite its own trace.

---

## 54.3 Missing Authority Link

Execution occurred,
but no valid authority reference exists.

---

## 54.4 Missing Approval Link

High-risk execution occurred,
but no approval reference exists.

---

## 54.5 Hidden Recovery

A successor appears
without connection to the failed source.

---

## 54.6 Trace Deletion During Recovery

Repair removes evidence
needed to understand the incident.

---

## 54.7 Human Invisible Override

A human bypasses safety controls
without leaving evidence.

---

# 55. Minimal Trace Model

A minimal safety-oriented trace system
should capture:

```text
operation_id
actor_id
action
target
authority_reference
approval_reference
timestamp
result
effect_reference
```

For recovery:

```text
source_operation_id
recovery_reference
successor_operation_id
```

---

# 56. Relationship to TACP

TACP provides operational states.

Trace provides the evidence chain
connecting those states.

Conceptually:

```text
TACP State Transition
        ↓
Trace Record
        ↓
Auditable History
```

Examples:

```text
AUTHORIZED
  ↓
HELD
```

should preserve why the transition occurred.

---

# 57. Relationship to Authority

Authority defines permission.

Trace records:

```text
which authority
was used
at which time
for which action
```

Conceptually:

```text
Authority
   ↓
Execution
   ↓
Trace
```

Without this link,
permission cannot be meaningfully audited.

---

# 58. Relationship to AI Zero Network

In a distributed AI network,
trace may cross nodes.

Reference flow:

```text
Node A
  ↓ Trace Relay
Node B
  ↓ Trace Relay
Node C
```

Each node SHOULD preserve local evidence
while allowing cross-node causal reconstruction.

---

# 59. Trace Relay Role

A Trace Relay SHOULD transport
safety-relevant trace references
without silently rewriting their meaning.

It MAY:

- forward;
- sign;
- timestamp;
- enrich;
- aggregate;

but SHOULD preserve origin relationships.

---

# 60. Shared Trace

Distributed systems MAY use a shared trace layer
to expose enough common evidence for mutual safety
without exposing complete internal state.

Conceptually:

```text
Private Internal State
       ↓
Minimal Safety Trace
       ↓
Shared Verification Layer
```

This supports cross-system audit
without requiring full internal transparency.

---

# 61. Trace as a Common Safety Language

Trace provides a shared language between:

```text
AI
Human
Rule Engine
Auditor
Network Node
Recovery System
```

Each may reason differently,
but all can reference the same structural evidence.

---

# 62. Trace as a Recovery Backbone

Recovery depends on knowing:

```text
what happened
what authority existed
what changed
what remains unresolved
```

Therefore:

> No reliable recovery without sufficient trace.

Trace is not merely historical.

It is operational infrastructure for resilience.

---

# 63. Core Trace Rule

The trace architecture can be summarized as:

> Every important action should leave enough evidence
> to reconstruct why it was allowed, what it did,
> what effect occurred, and what happened afterward.

---

# 64. Final Mapping Principle

A resilient system should not ask only:

> Did something go wrong?

It should be able to ask:

> What chain of request, authority, approval, execution,
> effect, containment, and recovery produced this state?

That chain is the purpose of safety trace.

Trace therefore acts as the connective tissue of resilient AI safety:

```text
Authority
Execution
Effect
Containment
Recovery
        ↓
      Trace
```

Without trace, safety becomes difficult to verify.

With trace, failures can remain visible,
attributable, reviewable, and recoverable.
