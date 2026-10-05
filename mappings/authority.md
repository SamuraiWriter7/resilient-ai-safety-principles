# Mapping: Authority

**Project:** Resilient AI Safety Principles  
**Version:** v0.1  
**Mapping Target:** Authority and Authorization Structures  
**Status:** Informative Mapping

---

## 1. Purpose

This document maps the Resilient AI Safety Principles
to authority and authorization structures.

The purpose is to define how structural safety requirements apply to:

- authority issuance;
- authority scope;
- action authorization;
- temporal validity;
- revocation;
- renewal;
- delegation;
- escalation;
- re-authorization.

This mapping is informative in v0.1.

It does not require a specific authorization protocol.

---

# 2. Core Relationship

Authority is the primary boundary between:

```text
AI can propose
```

and:

```text
AI can act
```

The core relationship is:

```text
Intent
  ↓
Authority Request
  ↓
Independent Evaluation
  ↓
Authority Grant
  ↓
Execution Gate
  ↓
Action
```

A capability existing inside a system does not imply permission to use it.

Therefore:

```text
Capability ≠ Authority
```

and:

```text
Intent ≠ Authority
```

---

# 3. Authority as a Safety Envelope

Authority SHOULD be represented as a bounded envelope.

Conceptually:

```text
Authority Envelope
=
Subject
× Action
× Target
× Scope
× Duration
× Resource
× Impact Boundary
```

An implementation MAY add:

- location;
- operation count;
- network domain;
- data classification;
- monetary ceiling;
- delegation permission;
- tool restrictions.

The important property is boundedness.

---

# 4. Principle Mapping

| Safety Principle | Authority Relationship |
|---|---|
| Least Authority | Primary authority requirement |
| Role Separation | Requester and approver SHOULD be separable |
| Pre-Execution Gating | Valid authority is required before execution |
| Effect-Oriented Monitoring | Actual authority use SHOULD be observed |
| Containment First | Authority SHOULD be freezeable or revocable |
| Independent Verification | High-risk grants SHOULD support independent review |
| Controlled Local Failure | Authority SHOULD be domain-bounded |
| End-to-End Traceability | Authority issuance and use SHOULD be traceable |
| Recoverability | Authority SHOULD be reducible and re-issued |
| Layered Defense | Authority is one defense layer |
| Temporal Least Authority | Core requirement |
| Human Fallibility | Human grants SHOULD remain auditable |

---

# 5. SAFETY-INV-001 — No Self-Escalation

This invariant is primarily enforced by the authority system.

Unsafe structure:

```text
Agent A
  ↓
requests more authority
  ↓
Agent A approves request
  ↓
authority expands
```

Required structure:

```text
Agent A
  ↓
Authority Request
  ↓
Independent Authority Domain
  ↓
Grant / Deny / Reduce
```

An actor MUST NOT be able to unilaterally expand its own effective authority.

---

# 6. Authority Request vs Authority Grant

These concepts MUST remain distinct.

```text
authority_request
```

means:

> The actor claims that additional permission is necessary.

```text
authority_grant
```

means:

> An authorized authority domain has approved a bounded permission.

Therefore:

```text
Request ≠ Grant
```

A system SHOULD NOT treat repeated requests
as implicit escalation.

---

# 7. Reference Authority Record

A machine-readable authority structure MAY resemble:

```yaml
authority:
  authority_id: auth-001
  subject: agent-a

  action:
    - read
    - modify

  target:
    - resource-x

  scope:
    domain: project-a

  valid_from: 2026-10-05T00:00:00Z
  valid_until: 2026-10-05T01:00:00Z

  limits:
    max_operations: 5
    max_resource_units: 100

  delegation:
    allowed: false

  status: active

  approved_by: authority-domain-1
```

This example is informative only.

---

# 8. Authority States

Reference authority states include:

```text
REQUESTED
GRANTED
ACTIVE
HELD
EXPIRED
REVOKED
DENIED
CONSUMED
SUPERSEDED
```

Equivalent names MAY be used.

The important property is explicit lifecycle state.

---

# 9. Authority Lifecycle

Reference flow:

```text
REQUESTED
   ↓
EVALUATED
   ↓
GRANTED
   ↓
ACTIVE
   ↓
 ┌──────────────┬──────────────┐
 ↓              ↓              ↓
EXPIRED       REVOKED       CONSUMED
```

A subsequent operation SHOULD require new authority
when the prior grant is no longer valid.

---

# 10. Temporal Least Authority

Authority SHOULD decay over time.

Recommended structure:

```text
Grant
 ↓
Active Window
 ↓
Expiration
 ↓
Fresh Review
 ↓
Renew / Reduce / Deny
```

A system SHOULD avoid:

```text
Grant
 ↓
Permanent Authority
```

unless permanence is explicitly justified.

---

# 11. Expiration

Expired authority MUST NOT be treated as active.

Unsafe:

```text
authority expired
      ↓
agent still has credential
      ↓
execution succeeds
```

Preferred:

```text
authority expired
      ↓
gate detects expiration
      ↓
HOLD / DENY
```

Credential possession and authority validity are separate concepts.

---

# 12. Revocation

A revocation mechanism SHOULD support rapid removal
of previously valid authority.

Reference flow:

```text
ACTIVE
  ↓
REVOCATION EVENT
  ↓
REVOKED
  ↓
future execution denied
```

Revocation SHOULD be traceable.

Where feasible, revocation SHOULD propagate
to relevant execution gates.

---

# 13. Authority Freeze

Containment MAY temporarily freeze authority.

Example:

```text
ACTIVE
  ↓
anomaly detected
  ↓
FROZEN
  ↓
independent review
  ↓
RESTORE / REDUCE / REVOKE
```

Freezing differs from permanent revocation.

It preserves reversibility.

---

# 14. Scope Restriction

Authority SHOULD be scoped narrowly.

Poor:

```text
action: modify
target: *
```

Better:

```text
action: modify
target: resource-x
scope: project-a
```

Even better for sensitive tasks:

```text
action: modify
target: resource-x
field: metadata
max_operations: 1
valid_until: short-duration
```

---

# 15. Action Restriction

Authority to read SHOULD NOT imply authority to modify.

Authority to modify SHOULD NOT imply authority to delete.

Authority to propose SHOULD NOT imply authority to execute.

Reference separation:

```text
READ
WRITE
DELETE
EXECUTE
DELEGATE
APPROVE
```

These SHOULD be treated as distinct capabilities where relevant.

---

# 16. Target Restriction

Authority SHOULD specify its valid target.

Unsafe:

```text
modify any repository
```

Preferred:

```text
modify repository-A
```

More restrictive:

```text
modify repository-A/docs/
```

Target ambiguity SHOULD result in evaluation or hold
for high-risk operations.

---

# 17. Resource Restriction

Authority MAY include resource ceilings.

Examples:

```text
max_requests
max_tokens
max_cost
max_runtime
max_transactions
max_files
max_bytes
```

Resource limits reduce the amplification of mistakes.

---

# 18. Impact Boundary

Authority SHOULD consider not only what action is allowed,
but how much external effect may result.

Example:

```text
send message
```

is not sufficient authority information.

Relevant impact dimensions may include:

```text
recipient_count
audience
financial_value
physical_effect
data_volume
geographic_scope
```

---

# 19. Delegation

Delegation SHOULD be explicit.

Default:

```text
delegation_allowed = false
```

unless required.

If delegation is permitted, the delegated authority MUST NOT exceed
the delegator's effective authority.

Conceptually:

```text
Delegated Authority
≤
Parent Authority
```

---

# 20. Delegation Chains

Delegation chains SHOULD remain traceable.

Example:

```text
Human
  ↓
Agent A
  ↓
Agent B
  ↓
Tool
```

The system SHOULD be able to reconstruct:

- original authority source;
- each delegation step;
- reductions in scope;
- current holder;
- expiration.

---

# 21. Authority Amplification Through Delegation

A dangerous anti-pattern is:

```text
Agent A
has limited authority
   ↓
creates Agent B
   ↓
Agent B receives broader authority
```

This is indirect self-escalation.

The system MUST prevent authority amplification through delegation.

---

# 22. Approval Separation

For high-risk authority grants:

```text
requester
≠
sole approver
```

The approval layer SHOULD be independent
from the actor seeking the grant.

---

# 23. Human Approval

Human approval MAY authorize an action.

However, the approval itself SHOULD define:

- scope;
- target;
- duration;
- conditions;
- limits.

Human approval SHOULD NOT automatically mean:

```text
unlimited authority
```

---

# 24. Human Override

A human override SHOULD be:

- explicit;
- attributable;
- bounded;
- recorded;
- reviewable.

Unsafe structure:

```text
admin clicked override
```

with no further context.

Preferred:

```yaml
override:
  reviewer: human-001
  reason: emergency-maintenance
  scope: resource-x
  valid_until: ...
  trace_reference: trace-001
```

---

# 25. Authority and Trace

Every high-risk authority transition SHOULD create trace evidence.

Important transitions include:

```text
REQUESTED
GRANTED
ACTIVATED
RENEWED
REDUCED
FROZEN
REVOKED
EXPIRED
CONSUMED
```

Trace SHOULD answer:

> Who granted what authority to whom, for what purpose, and for how long?

---

# 26. Authority and Effect Monitoring

An authority system SHOULD distinguish:

```text
authorized action
```

from:

```text
actual effect
```

Example:

```text
authorized:
modify one record

actual:
modified 500 records
```

This indicates execution deviation even if the original authority was valid.

---

# 27. Authority Consumption

Some permissions SHOULD be consumable.

Example:

```text
authority:
  max_operations: 1
```

After successful use:

```text
ACTIVE
  ↓
CONSUMED
```

The same authority SHOULD NOT silently authorize repeated operations.

---

# 28. Replay Protection

Expired, consumed, or revoked authority SHOULD NOT be replayable.

Unsafe:

```text
old signed approval
      ↓
replayed
      ↓
new execution
```

Preferred:

```text
old approval
      ↓
state check
      ↓
DENY
```

---

# 29. Authority Unknown

If authority cannot be confirmed:

```text
AUTHORIZATION_UNKNOWN
```

SHOULD be treated as a distinct state.

For high-risk operations:

```text
UNKNOWN
  ↓
HOLD
```

rather than:

```text
UNKNOWN
  ↓
ALLOW
```

---

# 30. Conflicting Authority

A system MAY encounter conflicting authority records.

Example:

```text
Grant A → allow
Revocation B → deny
```

The architecture SHOULD define precedence.

A safe default is:

```text
valid revocation
>
older grant
```

Unresolved conflicts SHOULD result in hold
for high-risk operations.

---

# 31. Authority Reduction

Recovery SHOULD support reducing authority.

Example:

```text
before incident:
write + delete

after recovery:
read only
```

Recovery does not require restoring the previous permission level.

---

# 32. Re-Authorization

After:

- expiration;
- containment;
- compromise;
- recovery;
- major context change;

fresh authorization SHOULD be required.

Reference flow:

```text
old authority
   ↓
invalidated
   ↓
new context
   ↓
fresh evaluation
   ↓
new authority
```

---

# 33. Authority After Recovery

A recovered actor SHOULD NOT automatically inherit
all prior authority.

Preferred:

```text
Recovered Actor
   ↓
Minimal Restart Authority
   ↓
Observation
   ↓
Possible Expansion
```

This reduces the risk of restarting a compromised configuration.

---

# 34. Domain-Bounded Authority

Authority SHOULD belong to explicit domains.

Example:

```text
Domain A
 └─ Agent A authority

Domain B
 └─ Agent B authority
```

Authority in Domain A SHOULD NOT imply authority in Domain B.

Cross-domain actions SHOULD require explicit bridging authorization.

---

# 35. Root Authority

Systems SHOULD minimize the existence of universal root authority.

Where unavoidable, root authority SHOULD receive stronger controls:

- short duration;
- multi-party approval;
- mandatory trace;
- no silent delegation;
- emergency-only use;
- post-use review.

---

# 36. Authority Anti-Patterns

The following structures are discouraged.

## 36.1 Permanent Administrator Agent

```text
AI Agent
  ↓
permanent root access
```

---

## 36.2 Capability Equals Permission

```text
tool exists
  ↓
agent may use it
```

---

## 36.3 Self-Approved Escalation

```text
agent requests
agent approves
agent executes
```

---

## 36.4 Silent Renewal

```text
authority expires
  ↓
automatically renewed forever
```

---

## 36.5 Unbounded Delegation

```text
Agent A
  ↓
creates unlimited descendants
```

---

## 36.6 Authority Without Trace

No record exists explaining
why the action was allowed.

---

# 37. Reference High-Risk Flow

```text
Action Proposed
      ↓
Authority Required
      ↓
Authority Request
      ↓
Independent Evaluation
      ↓
 ┌───────────────┐
 │ GRANT         │
 │ REDUCE        │
 │ HOLD          │
 │ DENY          │
 └───────────────┘
      ↓
if granted
      ↓
Pre-Execution Gate
      ↓
Execution
      ↓
Effect Observation
      ↓
Trace
```

---

# 38. Relationship to TACP

Authority systems determine:

```text
what is permitted
```

TACP determines:

```text
whether the operation should transition
through the next safety state
```

Conceptually:

```text
Authority Record
      ↓
TACP Gate
      ↓
Execution Decision
```

Examples:

```text
expired authority
      ↓
TACP
      ↓
HELD
```

```text
revoked authority
      ↓
TACP
      ↓
DENIED
```

```text
authorization unknown
      ↓
TACP
      ↓
HELD
```

---

# 39. Relationship to Trace

Authority and trace SHOULD be tightly connected.

```text
Authority Grant
      ↓
Trace Reference

Execution
      ↓
Authority Reference

Effect
      ↓
Execution Reference
```

This allows reconstruction of:

```text
Who
authorized
whom
to do
what
to which target
under which limits
with what result
```

---

# 40. Relationship to AI Zero Network

Within a distributed AI network,
authority SHOULD remain locally bounded.

A node SHOULD NOT inherit global authority
simply by joining the network.

Conceptually:

```text
Node
 ↓
Identity
 ↓
Authority Envelope
 ↓
Local Execution
```

Cross-node authority SHOULD require
explicit protocol-level transitions.

---

# 41. Minimal Authority Model

The minimum useful authority structure is:

```text
subject
action
target
expiration
status
```

For higher-risk systems, add:

```text
scope
resource_limit
impact_boundary
delegation
approval
trace_reference
```

---

# 42. Authority Safety Equation

A conceptual safety heuristic is:

```text
Potential Impact
≈
Authority
× Scope
× Duration
× Connectivity
× Execution Speed
```

This is not a strict quantitative formula.

Its purpose is to show why broad,
persistent authority is structurally dangerous.

---

# 43. Core Authority Rule

The authority architecture can be summarized as:

> AI may request authority, but must not manufacture authority.

And:

> Authority should be narrow, temporary, revocable, traceable, and independently granted.

---

# 44. Final Mapping Principle

The purpose of an authority system is not merely
to decide whether an AI is trusted.

Its purpose is to define:

```text
what
this actor
may do
to this target
under these conditions
for this duration
within this impact boundary
```

A resilient system does not ask:

> Do we trust this AI?

It asks:

> What is the smallest authority this operation actually requires?

That distinction is fundamental to resilient AI safety.
