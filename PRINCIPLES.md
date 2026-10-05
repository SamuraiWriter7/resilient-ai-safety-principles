# Structural Safety Principles

**Project:** Resilient AI Safety Principles  
**Version:** v0.1  
**Status:** Explanatory Principles Document

---

## 1. Purpose

This document explains the structural principles behind the
Resilient AI Safety Principles specification.

`SPEC.md` defines normative requirements.

This document explains:

- why each principle exists;
- what structural failure it addresses;
- what implementation patterns support it;
- what anti-patterns weaken it;
- how the principles interact.

The central premise is:

> Safety should not depend on correctly identifying every malicious actor.

Instead:

> Safety should limit the ability of malicious intent, error, compromise,
> or runaway behavior to become large-scale authority and impact.

---

# 2. Principle 1 — Least Authority

## 2.1 Definition

An AI system should receive only the authority necessary
for its current authorized operation.

Authority should be constrained by dimensions such as:

- scope;
- action;
- target;
- duration;
- frequency;
- resource;
- impact boundary.

Conceptually:

```text
Authority =
Scope × Action × Target × Duration
```

The exact implementation may use additional dimensions.

---

## 2.2 Why This Principle Exists

AI systems can operate faster and across more resources than humans.

This creates an amplification problem.

A relatively small mistake can become dangerous when combined with:

- broad permissions;
- persistent credentials;
- unrestricted tool access;
- large target sets;
- high-speed execution;
- automatic delegation.

The danger is therefore not only the mistake itself.

The danger is:

```text
Small Error
    ×
Large Authority
    ×
High Speed
    ×
Wide Scope
    =
Large Failure
```

Least authority reduces this multiplication effect.

---

## 2.3 Desired Structure

Prefer:

```text
Task
 ↓
Required Capability
 ↓
Minimal Authority Grant
 ↓
Execution
 ↓
Expiration / Revocation
```

Authority should follow the task.

The task should not be reshaped around unnecessarily broad authority.

---

## 2.4 Anti-Patterns

Avoid:

### Permanent broad credentials

```text
Agent
  ↓
Administrator Access
  ↓
Indefinite Duration
```

### Authority for future unknown tasks

An agent receives permissions "just in case."

### Self-escalation

The same actor determines:

```text
I need more authority
        ↓
Authority granted
```

### Scope expansion through delegation

An agent indirectly expands its authority
by creating or controlling another actor.

---

## 2.5 Example

Poor structure:

```text
Email Agent
  ↓
Full Account Access
  ↓
Read / Send / Delete / Settings
```

Better structure:

```text
Email Drafting Task
  ↓
Read selected thread
  ↓
Create draft
  ↓
No send permission
  ↓
Authority expires
```

---

# 3. Principle 2 — Role Separation

## 3.1 Definition

Planning, execution, auditing, and approval should not be concentrated
in a single logical authority for high-risk operations.

Reference roles:

```text
Planner
Executor
Auditor
Approver
```

The producer of a high-risk action should not be its sole final approver.

---

## 3.2 Why This Principle Exists

A system becomes fragile when one component can:

```text
Decide
  +
Authorize
  +
Execute
  +
Judge itself correct
```

This creates a structural single point of failure.

If the component is:

- mistaken;
- compromised;
- manipulated;
- overconfident;
- misconfigured;

there may be no remaining internal barrier.

Role separation creates disagreement capacity.

---

## 3.3 Desired Structure

```text
Planner
   ↓ proposal

Auditor
   ↓ review

Approver
   ↓ authority

Executor
   ↓ action
```

These roles do not always require separate models.

The requirement is primarily logical separation.

---

## 3.4 Anti-Patterns

### Self-approval

```text
Agent:
"I created this plan."
"I reviewed this plan."
"I approve this plan."
"I will now execute it."
```

### Cosmetic multi-agent design

Four agents exist, but all share:

- the same authority;
- the same unchecked context;
- the same final decision;
- the same failure mode.

This is agent multiplication without power separation.

### Auditor subordinate to executor

An auditor cannot block, hold, or escalate an unsafe action.

In such a case, auditing becomes advisory only.

---

## 3.5 Example

Weak:

```text
Agent A
 ├─ plans
 ├─ approves
 ├─ executes
 └─ marks success
```

Stronger:

```text
Agent A → Plan
Rule Gate → Permission Check
Agent B → Independent Review
Human / Policy → Approval
Agent C → Execution
Trace Layer → Record
```

---

# 4. Principle 3 — Pre-Execution Gating

## 4.1 Definition

AI intention, recommendation, or reasoning output
must not automatically become real-world execution authority.

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

---

## 4.2 Why This Principle Exists

A model can produce a plausible action very quickly.

That does not mean the action is:

- authorized;
- necessary;
- proportionate;
- reversible;
- safe;
- correctly targeted.

The gap between thinking and acting is therefore a safety boundary.

---

## 4.3 Desired Structure

Before high-impact execution, evaluate:

```text
Why?
What?
Who?
Where?
With what authority?
For how long?
What can go wrong?
Can it be reversed?
```

Execution should begin only after the authority state is known.

---

## 4.4 Anti-Patterns

### Thought-to-action coupling

```text
Model output
   ↓
API call
```

with no intervening authorization layer.

### Confidence as permission

```text
confidence > 0.95
      ↓
execute
```

Model confidence is not equivalent to authority.

### Tool availability as authority

A tool exists, therefore the agent assumes it may use it.

Capability and permission are different.

---

## 4.5 Example

Weak:

```text
AI detects "duplicate records"
  ↓
Deletes them automatically
```

Stronger:

```text
AI detects possible duplicates
  ↓
Creates proposed deletion set
  ↓
Independent check
  ↓
Authorization
  ↓
Reversible quarantine
  ↓
Deletion only if confirmed
```

---

# 5. Principle 4 — Effect-Oriented Monitoring

## 5.1 Definition

Safety should primarily evaluate observable actions,
authority use, and effects rather than relying only
on inferred internal intention.

---

## 5.2 Why This Principle Exists

Intent is difficult to observe.

A malicious-looking request may have a legitimate context.

A benign-looking request may produce harmful consequences.

Therefore:

```text
Intent ≠ Effect
```

A resilient system asks:

> What is this action actually doing?

---

## 5.3 Desired Structure

Monitor:

```text
Request
 ↓
Resource Access
 ↓
Authority Used
 ↓
State Change
 ↓
External Effect
 ↓
Impact
```

The system should be able to evaluate actual behavior
independently of the actor's stated purpose.

---

## 5.4 Anti-Patterns

### Personality-based safety

"This user appears trustworthy."

### Language-based safety

"The request sounds harmless."

### Model reputation safety

"This model is normally safe."

### Intent-only blocking

A system spends most of its safety effort
trying to classify the user's inner state.

---

## 5.5 Example

Instead of asking only:

```text
Is the user malicious?
```

ask:

```text
What resource is accessed?
What is being modified?
How much can be changed?
Which authority enables it?
Can the effect escape its boundary?
```

---

# 6. Principle 5 — Containment First

## 6.1 Definition

When suspicious behavior is detected,
the first response should usually be to restrict its effect,
preserve evidence, and verify independently.

Reference states:

```text
ACTIVE
  ↓
HELD
  ↓
QUARANTINED
```

---

## 6.2 Why This Principle Exists

Immediate destruction has two problems.

First, detection may be wrong.

Second, destroying state can also destroy evidence.

A reversible intermediate state creates time for investigation.

---

## 6.3 Desired Structure

```text
Suspicion
   ↓
Hold
   ↓
Authority Freeze
   ↓
Evidence Preservation
   ↓
Independent Review
   ↓
Resume / Restrict / Recover / Terminate
```

---

## 6.4 Anti-Patterns

### Immediate irreversible deletion

The system cannot later explain what happened.

### Continue-until-certain

The operation continues normally
while the system attempts to achieve perfect certainty.

### Silent containment

The operation is held,
but there is no trace explaining why.

---

## 6.5 Example

Instead of:

```text
Anomaly detected
  ↓
Destroy agent
```

prefer:

```text
Anomaly detected
  ↓
Block external execution
  ↓
Freeze new credentials
  ↓
Preserve state
  ↓
Review
```

Emergency termination remains appropriate
when continued execution creates immediate unacceptable harm.

---

# 7. Principle 6 — Independent Verification

## 7.1 Definition

The actor that produced an action or detected an anomaly
should not be the only authority validating that conclusion.

---

## 7.2 Why This Principle Exists

A system may fail consistently.

If the same reasoning process:

```text
creates the error
      ↓
reviews the error
      ↓
confirms itself
```

then review provides little protection.

Independent verification introduces a different failure path.

---

## 7.3 Desired Structure

Possible verification diversity:

```text
Model A
   ↓
Model B

Model
   ↓
Deterministic Rule

AI
   ↓
Human

Internal System
   ↓
External Auditor
```

Independence can come from:

- different information;
- different reasoning methods;
- different authority;
- different implementations;
- different incentives.

---

## 7.4 Anti-Patterns

### Duplicate self-checking

The same agent is prompted:

> Are you sure?

without any new evidence or independent constraint.

This may improve reasoning,
but it is not strong independent verification.

### Shared compromise

Multiple agents use the same compromised credential
and therefore do not provide meaningful separation.

### Auditor without evidence access

An independent reviewer exists,
but cannot see the information necessary to review the action.

---

# 8. Principle 7 — Controlled Local Failure

## 8.1 Definition

Systems should assume that individual components will sometimes fail.

The goal is to keep failure local.

---

## 8.2 Why This Principle Exists

Large distributed systems rarely fail only in clean,
predictable ways.

A local compromise becomes catastrophic when:

```text
Local Failure
    ↓
Shared Credentials
    ↓
Shared Authority
    ↓
Shared Network
    ↓
System-Wide Failure
```

The architecture should break this chain.

---

## 8.3 Desired Structure

```text
Node Failure
   ↓
Boundary Trigger
   ↓
Node Isolation
   ↓
Authority Revocation
   ↓
Network Restriction
   ↓
Healthy Nodes Continue
```

---

## 8.4 Anti-Patterns

### Universal credentials

Every node can act as every other node.

### Shared unrestricted memory

One compromised component can modify
the entire system's state.

### Automatic trust propagation

If one trusted node trusts another,
all authority is inherited.

---

## 8.5 Example

Prefer:

```text
Compromised Agent A
   ↓
Agent A isolated
   ↓
Its credentials revoked
   ↓
Other agents retain limited functions
```

over:

```text
Agent A compromised
   ↓
Shared root credential compromised
   ↓
Entire network compromised
```

---

# 9. Principle 8 — End-to-End Traceability

## 9.1 Definition

Important AI actions should leave sufficient evidence
to reconstruct their causal path.

Trace connects:

```text
Intent
Authority
Decision
Approval
Execution
Effect
Responsibility
```

---

## 9.2 Why This Principle Exists

Without trace, a system may know that something went wrong
without knowing:

- who initiated it;
- which authority allowed it;
- what changed;
- whether approval existed;
- where the failure began.

Trace enables accountability and recovery.

---

## 9.3 Trace Is Not Just Logging

A conventional log might say:

```text
14:02 API request completed
```

A structural trace should be able to answer:

```text
Who requested it?
Which task did it belong to?
Which authority was used?
Which approval authorized it?
What target changed?
What effect resulted?
```

---

## 9.4 Anti-Patterns

### Log abundance without causality

Millions of logs exist,
but no causal chain can be reconstructed.

### Mutable audit trail

The actor being audited can rewrite its own history.

### Trace without authority reference

An action is recorded,
but no one can determine why it was permitted.

---

# 10. Principle 9 — Recoverability

## 10.1 Definition

Safety does not end when unsafe execution stops.

The system should be able to move back toward
a valid authorized state.

---

## 10.2 Why This Principle Exists

Stopping a process may leave behind:

- corrupted state;
- expired evidence;
- invalid credentials;
- partial execution;
- unresolved dependencies;
- damaged resources.

Therefore:

```text
Stop ≠ Recovery
```

---

## 10.3 Desired Structure

```text
Failure
  ↓
Containment
  ↓
State Assessment
  ↓
Repair
  ↓
Evidence Refresh
  ↓
Re-authorization
  ↓
Safe Continuation
```

---

## 10.4 Recovery Options

Recovery may include:

- rollback;
- authority reduction;
- credential replacement;
- state reconstruction;
- successor handoff;
- human review;
- safe retry;
- permanent restriction.

Recovery does not always mean resuming the original task.

Sometimes the correct recovery is:

```text
Do not resume.
Preserve evidence.
Transfer responsibility.
```

---

## 10.5 Anti-Patterns

### Permanent hold

The system enters `HELD`
and has no defined next state.

### Automatic retry

The same unsafe action is repeatedly retried
without changing the conditions that caused failure.

### Recovery without fresh evidence

The system resumes based on stale observations.

---

# 11. Principle 10 — Layered Defense

## 11.1 Definition

Critical safety should not depend on one control.

Recommended safety layers include:

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

## 11.2 Why This Principle Exists

Every defense can fail.

Therefore, safety should not be based on:

```text
One perfect wall
```

but on:

```text
Multiple imperfect barriers
```

A failure should encounter another independent boundary.

---

## 11.3 Desired Structure

Example:

```text
Model refuses unsafe plan
        ↓ if missed
Reasoning reviewer questions plan
        ↓ if missed
Authority gate limits permission
        ↓ if missed
Executor sandbox limits effect
        ↓ if missed
Network boundary blocks propagation
        ↓
Trace enables investigation
```

---

## 11.4 Anti-Patterns

### Model-only safety

The model is expected to "behave safely."

### Human-only safety

A human approval checkbox is treated as absolute protection.

### Firewall-only safety

Network restrictions exist,
but authority inside the network is unrestricted.

### Audit-only safety

The system can explain a disaster afterward,
but cannot limit it while it happens.

---

# 12. Cross-Cutting Principle A — Temporal Least Authority

## 12.1 Definition

Authority should decay over time.

Permission should not silently become permanent.

---

## 12.2 Why This Principle Exists

Long-lived permissions accumulate.

An initially reasonable grant may become unsafe because:

- the task ends;
- context changes;
- the actor changes;
- credentials leak;
- risk increases;
- the target changes.

Therefore authority should have time boundaries.

---

## 12.3 Desired Structure

```text
Requested Authority
   ↓
Granted
   ↓
Active Window
   ↓
Expiration
   ↓
Re-evaluation
   ↓
Renew / Reduce / Revoke
```

---

## 12.4 Anti-Patterns

### Never-expiring credentials

### Automatic renewal without review

### Dormant authority

A permission remains active for months
because no one remembered to revoke it.

### Privilege ratchet

Authority only increases and never decreases.

---

# 13. Cross-Cutting Principle B — Human Fallibility

## 13.1 Definition

Humans are part of the safety structure,
but humans are not outside the failure model.

---

## 13.2 Why This Principle Exists

Human reviewers can be affected by:

- fatigue;
- time pressure;
- social pressure;
- manipulation;
- incomplete information;
- incentives;
- habit;
- collusion.

Therefore:

```text
Human Approval ≠ Absolute Safety
```

---

## 13.3 Desired Structure

```text
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone
```

No single participant is assumed to be infallible.

---

## 13.4 Human-in-the-Auditable-Loop

A useful extension of conventional
Human-in-the-loop design is:

> Human-in-the-auditable-loop

The human may retain decision authority,
but the decision itself remains:

- visible;
- attributable;
- reviewable;
- constrained;
- traceable.

---

## 13.5 Anti-Patterns

### Human override without trace

A reviewer bypasses controls
and no evidence is preserved.

### Approval fatigue

Humans approve hundreds of repetitive requests,
turning review into a ritual.

### Root human authority

A single human can permanently bypass
all safety layers.

---

# 14. Interaction Between Principles

These principles are not independent checkboxes.

They form a safety cycle.

```text
Least Authority
      ↓
Role Separation
      ↓
Pre-Execution Gate
      ↓
Execution
      ↓
Effect Monitoring
      ↓
Trace
      ↓
Containment
      ↓
Independent Verification
      ↓
Local Failure Boundary
      ↓
Recovery
      ↓
Re-authorization
```

Layered defense surrounds the entire process.

Temporal least authority applies across the authority lifecycle.

Human fallibility applies across all human participation.

---

# 15. Failure Amplification Model

The structural danger can be represented conceptually as:

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

This is not intended as a strict quantitative formula.

It is a design heuristic.

Safety can therefore be improved without perfectly eliminating
the original failure potential.

For example:

```text
Malicious Intent = unchanged

Authority ↓
Scope ↓
Duration ↓
Connectivity ↓
Recovery ↑
Trace ↑

→ Systemic Risk ↓
```

This is a central idea of the specification.

---

# 16. Philosophical Review Cycle

The four philosophical perspectives provide
an additional review loop for high-risk decisions.

They are not intended as abstract decoration.

They provide four different forms of error detection.

---

## 16.1 Epistemology — Knowledge Boundary

Ask:

```text
What do we know?
What do we not know?
Is the evidence sufficient?
```

This detects false certainty.

---

## 16.2 Logic — Inference Boundary

Ask:

```text
Does the conclusion follow?
Is there a hidden leap?
Are alternatives being ignored?
```

This detects reasoning failure.

---

## 16.3 Ontology / Metaphysics — Object Boundary

Ask:

```text
What exactly are we acting on?
What is the real problem?
Which assumptions are being treated as facts?
```

This detects category errors.

---

## 16.4 Ethics — Impact Boundary

Ask:

```text
Who is affected?
What harm can occur?
Is the intervention proportionate?
Should this action happen?
```

This detects value and impact failure.

---

## 16.5 Circular Review

The four reviews should influence each other.

```text
Epistemology
     ↓
Logic
     ↓
Ontology
     ↓
Ethics
     ↓
Epistemology
```

For example:

An ethical concern may reveal missing evidence.

Missing evidence may invalidate a logical conclusion.

A logical contradiction may reveal
that the wrong object was being modeled.

The cycle can therefore continue until:

- sufficient confidence exists;
- execution is restricted;
- human review is required;
- or the operation is rejected.

---

# 17. Safety Is Structural, Not Moral Classification

This project deliberately separates two questions.

Question A:

> Is this person or AI good or bad?

Question B:

> Can this actor produce an unsafe effect
> with the authority currently available?

Question B is usually more operationally useful.

A resilient infrastructure should not require
perfect moral classification before it can remain safe.

---

# 18. Design Target

The design target is not:

```text
No malicious users
No AI errors
No human errors
No compromised systems
```

Those assumptions are unrealistic.

The target is:

```text
Malice can exist
Errors can exist
Compromise can occur
Disagreement can occur

BUT

Authority remains bounded
Effects remain observable
Failure remains local
Evidence remains available
Recovery remains possible
```

---

# 19. Final Principle

The entire document can be reduced to one structural rule:

> Dangerous intent becomes dangerous power only when structure allows it to scale.

Therefore:

> Do not build a system that requires perfect actors.

Build a system in which imperfect actors cannot easily create
unbounded systemic failure.

The long-term objective is not:

> Perfect AI

It is:

> Resilient AI Civilization
