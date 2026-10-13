# Resilient AI Safety Principles

Structural principles for preventing malicious, mistaken, compromised, or runaway AI actions from scaling into catastrophic authority, speed, and impact.

> **The primary danger is not malicious intent itself, but structures that convert malicious intent, error, or compromise into large-scale power.**

This repository defines safety structures for AI agents and distributed AI systems.

The goal is not to create a perfectly safe AI.

The goal is to create systems in which:

- errors remain bounded;
- authority does not silently expand;
- actions require explicit authorization;
- safety decisions remain traceable;
- containment can be verified;
- recovery is possible;
- failures do not automatically propagate;
- networking does not become authority aggregation.

---

# 1. Core Thesis

AI safety is often framed as a problem of intent:

```text
Is the AI good?

Is the AI malicious?

Will the AI obey?

This repository approaches the problem differently.
The central question is:
What structure turns a mistake, attack, bad instruction, or compromised agent into large-scale power?

A dangerous event becomes systemic when it is combined with:
Authority
Speed
Scope
Persistence
Connectivity

A conceptual model is:
Systemic Risk
≈
Failure Potential
× Authority
× Speed
× Scope
× Persistence
× Connectivity

Therefore, resilient safety architecture should reduce the ability of any single failure to acquire all of those properties at once.
2. Design Goal
The long-term target is:
Resilient AI Civilization

not:
Perfect AI

The repository assumes that:
- AI will make mistakes;
- humans will make mistakes;
- policies may be incomplete;
- systems may be compromised;
- safety mechanisms may fail;
- network participants may disagree;
- recovery will sometimes be required.
The design objective is therefore:
Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.

3. Structural Safety Model
The basic architecture separates:
Thought
  ↓
Evaluation
  ↓
Authority
  ↓
Execution
  ↓
Observation
  ↓
Verification
  ↓
Recovery

The important structural rules are:
Separate thought from authority.

Separate authority from execution.

Separate execution from verification.

Separate local failure from global propagation.

Connect all stages through trace.

Restore operation through explicit recovery.

4. Human Fallibility
Humans are part of the safety architecture, but humans are not treated as infallible.
The preferred model is:
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone

This repository therefore favors:
Human-in-the-auditable-loop

rather than assuming that human involvement alone guarantees safety.
5. Version Progression
The specification evolves through five structural layers.
v0.1  Structure
v0.2  Receipt
v0.3  Chain
v0.4  Branch
v0.5  Network

Or as questions:
v0.1
What safety structure should exist?

v0.2
What machine-readable records represent that structure?

v0.3
Do those records form one coherent causal chain?

v0.4
Can safety survive branching and merging?

v0.5
Can safety survive networking across independent domains?

6. v0.1 — Structural Safety Baseline
v0.1 defines the foundational structural principles.
Principles
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
Cross-cutting principles:
- Temporal Least Authority
- Human Fallibility
Reference lifecycle:
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
Containment
  ↓
Independent Verification
  ↓
Recovery
  ↓
Re-Authorization
  ↓
RESUME / RESTRICT / ISOLATE / TRANSFER / TERMINATE

v0.1 Invariants
SAFETY-INV-001  No Self-Escalation
SAFETY-INV-002  No Sole Self-Approval
SAFETY-INV-003  No Direct Intent-to-Execution Transition
SAFETY-INV-004  Observable Effects Over Assumed Intent
SAFETY-INV-005  Reversible Containment When Feasible
SAFETY-INV-006  Independent Safety Verification
SAFETY-INV-007  Failure Boundary Preservation
SAFETY-INV-008  Trace Preservation
SAFETY-INV-009  Recovery Path Required
SAFETY-INV-010  No Single Safety Dependency

7. v0.2 — Machine-Readable Safety Receipts
v0.2 converts structural safety into explicit records.
Core rule:
Authorize explicitly. Contain visibly. Verify independently. Recover traceably.

The four primary records are:
Authority Envelope
Containment Receipt
Independent Verification Record
Recovery Receipt

Reference flow:
Authority Envelope
      ↓
Action Attempt
      ↓
unsafe / uncertain
      ↓
Containment Receipt
      ↓
Independent Verification Record
      ↓
Recovery Receipt
      ↓
New Authority Envelope

v0.2 Invariants
SAFETY-INV-011  Authority Envelope Required
SAFETY-INV-012  Authority Envelope Immutability
SAFETY-INV-013  Expired Envelope Rejection
SAFETY-INV-014  Containment Must Be Explicit
SAFETY-INV-015  Evidence Preservation During Containment
SAFETY-INV-016  Independent Verification Identity
SAFETY-INV-017  Verification Evidence Freshness
SAFETY-INV-018  Recovery Must Reference Source State
SAFETY-INV-019  No Automatic Privilege Restoration
SAFETY-INV-020  Recovery Must End in Explicit State

8. v0.3 — Cross-Receipt Safety Chain
Individually valid receipts are not sufficient.
They must belong to the same causal event.
Core rule:
Validate the chain, not only the receipts.

Reference:
Authority
   ↓
Action
   ↓
Containment
   ↓
Verification
   ↓
Recovery

v0.3 verifies that the chain is causally coherent.
v0.3 Invariants
SAFETY-INV-021  Receipt Identity Consistency
SAFETY-INV-022  Subject Continuity
SAFETY-INV-023  Authority-to-Action Binding
SAFETY-INV-024  Containment Causal Link Required
SAFETY-INV-025  Verification Must Reference Containment
SAFETY-INV-026  Recovery Must Reference Verification
SAFETY-INV-027  No Broken Safety Chain
SAFETY-INV-028  No Conflicting Final States
SAFETY-INV-029  No Receipt Replay
SAFETY-INV-030  Bundle Trace Continuity

The machine-readable bundle is defined by:
schemas/safety-receipt-bundle.schema.json

9. v0.4 — Branch / Merge Safety
Real agent systems branch.
One operation may produce multiple successors, parallel plans, recovery branches, or alternative execution paths.
The danger is that branching may accidentally multiply authority.
Core rules:
A branch is not permission amplification.

A merge is not authority aggregation.

Reference:
Parent Operation
      ↓
   Branching
   /       \
  ↓         ↓
Branch A  Branch B
  ↓         ↓
Auth A    Auth B
  ↓         ↓
Verify A  Verify B
   \       /
    ↓     ↓
Compatibility Check
       ↓
New Merge Authority
       ↓
Merged Operation

Important:
Auth A + Auth B
      ≠
Merged Authority

v0.4 Invariants
SAFETY-INV-031  Explicit Branch Declaration
SAFETY-INV-032  Branch Authority Isolation
SAFETY-INV-033  No Implicit Successor Inheritance
SAFETY-INV-034  Branch-Specific Verification
SAFETY-INV-035  Branch-Specific Trace
SAFETY-INV-036  Merge Requires Compatibility Check
SAFETY-INV-037  No Conflicting Authority Merge
SAFETY-INV-038  Carried Blockers Must Survive Branching
SAFETY-INV-039  Branch Termination Must Be Local
SAFETY-INV-040  Merge Outcome Must Be Explicit

The machine-readable bundle is defined by:
schemas/safety-branch-bundle.schema.json

10. v0.5 — Cross-Domain / Federation Safety
v0.5 extends safety beyond a single administrative or authority domain.
Examples include:
- multiple organizations;
- independent AI agent clusters;
- cloud and local AI systems;
- sovereign environments;
- federated AI networks;
- multi-tenant systems;
- inter-company safety networks.
The key problem is:
Safety information must cross boundaries.

Authority must not silently cross with it.

Core rules:
Share evidence, not authority.

Receive globally, decide locally.

Federate decisions explicitly; never inherit them implicitly.

The most important equation is:
Signal ≠ Authority

Reference flow:
Domain A
   ↓
Safety Event
   ↓
Verification
   ↓
Federated Safety Signal
   ↓
──────── Domain Boundary ────────
   ↓
Domain B
   ↓
Provenance Validation
   ↓
Replay Check
   ↓
Local Interpretation
   ↓
Local Authority Decision
   ↓
Local Action

A remote signal may influence a decision.
It does not itself authorize the action.
11. v0.5 Safety Domain Model
A safety domain represents an independently governed execution environment.
Reference:
Safety Domain
├── domain_id
├── authority_boundary
├── policy_boundary
├── execution_boundary
├── trace_boundary
└── federation_relationships

Crossing a domain boundary means:
remote evidence may continue

remote authority does not continue automatically

This distinction is fundamental to v0.5.
12. Federated Safety Signal
The primary v0.5 machine-readable object is:
schemas/federated-safety-signal.schema.json

A Federated Safety Signal may contain:
signal identity
source domain
destination scope
provenance
evidence references
severity
confidence
validity
propagation limits
replay protection
recommended response
local interpretation
local authority decision
federation decision
trace

A signal is:
evidence
warning
context
recommendation

A signal is not:
remote execution permission
automatic containment authority
automatic recovery authority
implicit federation authority

13. v0.5 Invariants
SAFETY-INV-041  Explicit Domain Boundary
SAFETY-INV-042  No Automatic Cross-Domain Authority Propagation
SAFETY-INV-043  Safety Signal Provenance Required
SAFETY-INV-044  Cross-Domain Signal Must Be Interpreted Locally
SAFETY-INV-045  Remote Containment Requires Local Authorization
SAFETY-INV-046  Shared Threat Does Not Imply Shared Authority
SAFETY-INV-047  Propagation Scope Must Be Bounded
SAFETY-INV-048  Cross-Domain Replay Must Be Rejected
SAFETY-INV-049  Federated Recovery Must Preserve Domain Autonomy
SAFETY-INV-050  Network-Wide Action Requires Explicit Federation Decision

14. Shared Threat vs Shared Authority
Multiple domains may observe the same threat.
Example:
             Threat T
            /   |   \
           ↓    ↓    ↓
       Domain A B    C

They may share:
evidence
indicators
traces
hashes
anomaly descriptions
verification results

They must not automatically share:
execution authority
containment authority
recovery authority
termination authority
privilege
credentials

Therefore:
Shared threat intelligence is not shared control.

15. Federation Decisions
Sometimes coordinated network-wide action is necessary.
Examples:
FEDERATED_ALERT
FEDERATED_RESTRICT
FEDERATED_ISOLATE
FEDERATED_PAUSE
FEDERATED_RECOVERY_COORDINATION
FEDERATED_TERMINATION

Such actions require an explicit federation decision.
Reference:
Domain A ─┐
Domain B ─┼→ Federation Evaluation
Domain C ─┘
                 ↓
         Federation Decision
                 ↓
          Bounded Action

A local signal alone must not produce:
GLOBAL_COMMAND

across independent domains.
16. Recovery Across Domains
Recovery is also local by default.
Invalid:
Domain A
RECOVERED
   ↓
Domain B
AUTO RESUME

Preferred:
Domain A RECOVERED
        ↓
Recovery Signal
        ↓
Domain B
        ↓
Local Blocker Review
        ↓
Local Verification
        ↓
Fresh Local Authority
        ↓
RESUME

Core rule:
Recovery information may federate. Recovery authority does not.

17. Replay Protection
A valid signal once is not valid forever.
Valid once
≠
Valid forever

v0.5 distinguishes:
Forwarding

from:
Replay

Legitimate forwarding preserves:
- origin;
- identity;
- context;
- validity;
- scope;
- trace.
Replay occurs when old safety information is reused as fresh evidence for a different event, time, or context.
18. Bounded Propagation
Safety signals should have an operational horizon.
Recommended controls include:
target_domains
target_domain_class
federation_id
expires_at
ttl_seconds
max_hops
maximum_relay_count
allowed_federation_paths
forwarding_allowed

Conceptually:
Safety information must have:

an origin
a destination
a lifetime
a maximum reach

Unbounded warning propagation can itself become a systemic failure mechanism.
19. Failure Locality
The repository consistently attempts to prevent local failure from becoming global failure.
The progression is:
v0.1
Preserve failure boundaries.

v0.4
Branch termination must remain local.

v0.5
Domain failure should remain local unless an explicit
federation-level reason justifies wider intervention.

This is a central property of resilient distributed systems.
20. Repository Structure
.
├── README.md
├── SPEC.md
├── PRINCIPLES.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── requirements.txt
│
├── specs/
│   └── v0.5.md
│
├── schemas/
│   ├── safety-assessment.schema.json
│   ├── authority-envelope.schema.json
│   ├── containment-receipt.schema.json
│   ├── verification-record.schema.json
│   ├── recovery-receipt.schema.json
│   ├── safety-receipt-bundle.schema.json
│   ├── safety-branch-bundle.schema.json
│   └── federated-safety-signal.schema.json
│
├── examples/
│   ├── pass/
│   ├── fail/
│   │
│   ├── v0.2/
│   │   ├── pass/
│   │   └── fail/
│   │
│   ├── v0.3/
│   │   ├── pass/
│   │   └── fail/
│   │
│   ├── v0.4/
│   │   ├── pass/
│   │   └── fail/
│   │
│   └── v0.5/
│       ├── pass/
│       │   └── federated-safety-signal-valid.json
│       └── fail/
│           ├── domain-boundary-missing.json
│           ├── cross-domain-authority-propagates.json
│           ├── signal-provenance-missing.json
│           ├── remote-signal-executed-without-local-interpretation.json
│           ├── remote-containment-without-local-authorization.json
│           ├── shared-threat-creates-shared-authority.json
│           ├── signal-propagation-unbounded.json
│           ├── cross-domain-signal-replay.json
│           ├── remote-recovery-auto-resumes-local-domain.json
│           └── network-action-without-federation-decision.json
│
├── mappings/
│   ├── tacp.md
│   ├── authority.md
│   ├── trace.md
│   └── zero-network.md
│
├── scripts/
│   └── validate_examples.py
│
└── .github/
    └── workflows/
        └── validate.yml

21. Validation
The repository includes machine-readable validation.
Install dependencies:
python -m pip install -r requirements.txt

Run:
python scripts/validate_examples.py

The validator checks:
JSON Schema validity
        ↓
Semantic invariant validity
        ↓
Expected PASS / FAIL outcome

v0.5 additionally verifies:
SAFETY-INV-041 through SAFETY-INV-050

against the actual fixture content.
22. Reference Corpus
Current reference corpus:
v0.1  PASS 1 / FAIL 10
v0.2  PASS 4 / FAIL 9
v0.3  PASS 1 / FAIL 10
v0.4  PASS 1 / FAIL 10
v0.5  PASS 1 / FAIL 10

Total:
PASS = 8
FAIL = 49
TOTAL = 57

FAIL fixtures are intentionally invalid examples.
They exist to prove that unsafe structures are detected.
23. GitHub Actions
Automated validation is defined in:
.github/workflows/validate.yml

The workflow currently tests:
Python 3.10
Python 3.12

and performs:
required-file checks
↓
JSON syntax validation
↓
JSON Schema validation
↓
reference corpus checks
↓
v0.5 invariant coverage checks
↓
semantic validation
↓
PASS / FAIL expectation validation

24. Safety Validation Philosophy
The repository does not treat a validator as a mechanism for making all fixtures pass.
Instead:
PASS fixture
→ must satisfy safety requirements

FAIL fixture
→ must fail for the intended reason

The goal is not:
make CI green at any cost

The goal is:
make CI green because
the safety distinction is correctly encoded

A fixture should be corrected when the fixture is wrong.
A validator should be corrected when the validator is wrong.
The safety rule itself should not be weakened merely to satisfy CI.
25. Relationship to Authorization
A recurring principle throughout the repository is:
AI may request authority.

AI must not silently create authority.

v0.5 extends this principle across networks:
A remote system may provide evidence.

A remote system must not silently become local authority.

Therefore:
Connectivity ≠ Authorization

26. Relationship to Trace
Trace connects all safety layers.
Conceptually:
Intent
↓
Authority
↓
Action
↓
Effect
↓
Containment
↓
Verification
↓
Recovery
↓
Branch
↓
Merge
↓
Federation

The system should allow later reconstruction of:
- what happened;
- who or what authorized it;
- which evidence existed;
- which domain made the decision;
- where authority changed;
- which signal crossed a boundary;
- what action resulted;
- why recovery occurred.
Trace therefore acts as the structural memory of the safety system.
27. Relationship to TACP
The repository can map to TACP-style safety states such as:
HELD
EXPIRED
REVOKED
AUTHORIZATION_UNKNOWN
RESOURCE_LIMIT
EVIDENCE_STALE
CONFIRMED_DENIED
HUMAN_REJECTED

v0.5 adds an important federation rule:
Domain A = HELD

does not automatically mean:
Domain B = HELD

Instead:
Domain A HELD
      ↓
Safety Signal
      ↓
Domain B Local Evaluation
      ↓
Local State Decision

28. Relationship to AI Zero Network
The repository is compatible with network architectures in which:
Trace
Authority
Field State
Boundary

are separated.
In such architectures, this repository can serve as a safety constraint layer around:
- cross-node interaction;
- authority transitions;
- federated warnings;
- recovery;
- local isolation;
- network-wide coordination.
The key rule remains:
Networking must not silently become privilege union.

29. Security Considerations
Relevant threats include:
self-escalation
sole self-approval
authority reuse
stale authorization
forged receipts
broken receipt chains
receipt replay
branch authority sharing
unsafe merge
blocker loss
termination propagation
forged safety signals
signal replay
signal flooding
authority smuggling
false federation emergencies
compromised federation members
malicious relays
provenance rewriting
cross-domain denial of service
network-scale false positives

The repository is intended to make such failure structures explicit and machine-testable.
30. Architectural Direction
The version sequence can be summarized as:
Safety Principle
      ↓
Safety Receipt
      ↓
Safety Chain
      ↓
Safe Branching
      ↓
Safe Networking

This creates a progression from a single action to a distributed AI network without requiring one universal central controller.
31. Centralized Safety Anti-Pattern
This repository does not assume that a single global safety controller is desirable.
A dangerous anti-pattern is:
Central Safety Node
       ↓
GLOBAL_COMMAND
       ↓
All Domains
       ↓
Automatic Execution

Such a structure may turn compromise of one safety controller into compromise of the entire system.
The preferred pattern is:
Shared Evidence
      ↓
Local Evaluation
      ↓
Local Authority
      ↓
Local Action

and when truly necessary:
Multiple Domains
      ↓
Explicit Federation Decision
      ↓
Bounded Coordinated Action

32. Core Safety Equations
Several compact relationships summarize the repository.
Intent ≠ Authority

Authority ≠ Execution

Execution ≠ Verification

Recovery ≠ Old Authority Restoration

Branching ≠ Authority Multiplication

Merging ≠ Authority Aggregation

Signal ≠ Authority

Shared Threat ≠ Shared Control

Connectivity ≠ Authorization

Local Recovery ≠ Global Recovery

33. Core Design Rules
The repository can be reduced to a small set of structural rules:
Minimize authority.

Make authority explicit.

Separate roles.

Gate execution.

Observe effects.

Preserve trace.

Contain locally.

Verify independently.

Recover explicitly.

Do not restore old privilege automatically.

Do not multiply authority through branching.

Do not aggregate authority through merging.

Share safety evidence across networks.

Do not automatically share authority.

Bound propagation.

Reject replay.

Preserve domain autonomy.

Require explicit decisions for network-wide action.

34. Status
Current specification maturity:
v0.1  Complete
v0.2  Complete
v0.3  Complete
v0.4  Complete
v0.5  Complete

Current validation status:
GitHub Actions: PASS

The current architectural frontier is:
Structural Safety
      ↓
Machine-Readable Safety
      ↓
Causal Safety
      ↓
Branch Safety
      ↓
Federation Safety

35. Final Principle
The repository began from one simple observation:
The greatest danger is not that failure exists. The greatest danger is that failure acquires unchecked authority, speed, scope, persistence, and connectivity.

Therefore:
Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.

And for distributed AI networks:
Share evidence, not authority.

Receive globally, decide locally.

Federate decisions explicitly; never inherit them implicitly.
