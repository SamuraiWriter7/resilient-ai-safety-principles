# Changelog

All notable changes to this project are documented in this file.

The project evolves as a sequence of structural safety layers:

```text
v0.1  Structure
v0.2  Receipt
v0.3  Chain
v0.4  Branch
v0.5  Network

The central design principle remains:
Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.

[0.5.0] - 2026-10-13
Added
Introduced Cross-Domain / Federation Safety for independently governed AI domains.
v0.5 extends the repository from branch-level safety into distributed AI networks.
Core principles:
Share evidence, not authority.

Receive globally, decide locally.

Federate decisions explicitly; never inherit them implicitly.

Added:
specs/v0.5.md
schemas/federated-safety-signal.schema.json

Added PASS fixture:
examples/v0.5/pass/federated-safety-signal-valid.json

Added FAIL fixtures:
examples/v0.5/fail/domain-boundary-missing.json
examples/v0.5/fail/cross-domain-authority-propagates.json
examples/v0.5/fail/signal-provenance-missing.json
examples/v0.5/fail/remote-signal-executed-without-local-interpretation.json
examples/v0.5/fail/remote-containment-without-local-authorization.json
examples/v0.5/fail/shared-threat-creates-shared-authority.json
examples/v0.5/fail/signal-propagation-unbounded.json
examples/v0.5/fail/cross-domain-signal-replay.json
examples/v0.5/fail/remote-recovery-auto-resumes-local-domain.json
examples/v0.5/fail/network-action-without-federation-decision.json

Added Invariants
Added:
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

Added Federated Safety Signal
Introduced a machine-readable cross-domain safety signal containing:
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
local authority
optional federation decision
trace

Established the core distinction:
Signal ≠ Authority

A remote signal may influence a local decision but does not itself authorize execution.
Added Domain Boundary Safety
Introduced explicit safety-domain boundaries covering:
authority boundary
policy boundary
execution boundary
trace boundary

Crossing a domain boundary now explicitly terminates implicit authority validity.
Added Cross-Domain Authority Isolation
Remote Authority Envelopes must not automatically remain effective after crossing into another independently governed domain.
Required pattern:
Remote Evidence
      ↓
Domain Boundary
      ↓
Local Evaluation
      ↓
Local Authority

instead of:
Remote Authority
      ↓
Domain Boundary
      ↓
Remote Authority remains effective

Added Provenance Requirements
Federated safety signals must preserve sufficient provenance to identify:
source domain
origin event
origin trace
issuance time
supporting evidence

Established:
No provenance, no trusted propagation.

Added Local Interpretation
Receiving domains must interpret incoming safety signals within their own:
policy
resources
risk state
authority model
execution context

Remote recommendations must not be translated directly into execution.
Added Remote Containment Gate
Remote containment information may justify local review but does not authorize local containment.
Containment actions require:
local authority

or an explicitly pre-authorized, bounded federation rule.
Added Shared-Threat / Shared-Authority Separation
Established:
Shared Threat ≠ Shared Authority

Multiple domains may share threat evidence without sharing execution authority.
Added Bounded Propagation
Federated signals now support bounded propagation through:
target domains
target classes
federation scope
expiration
TTL
hop limits
relay limits
allowed paths

Safety information must have both a lifetime and a propagation horizon.
Added Replay Protection
Introduced cross-domain replay protections distinguishing:
legitimate forwarding

from:
replay
context substitution
stale evidence reuse

Established:
Valid once ≠ Valid forever

Added Federated Recovery Autonomy
A remote recovery event must not automatically recover or resume another domain.
Required flow:
Remote Recovery
      ↓
Recovery Signal
      ↓
Local Blocker Review
      ↓
Local Verification
      ↓
Fresh Local Authority
      ↓
Resume

Established:
Recovery information may federate. Recovery authority does not.

Added Federation Decisions
Network-wide actions now require explicit federation decisions.
Examples include:
FEDERATED_ALERT
FEDERATED_RESTRICT
FEDERATED_ISOLATE
FEDERATED_PAUSE
FEDERATED_RECOVERY_COORDINATION
FEDERATED_TERMINATION

A federation decision must identify:
decision identity
federation identity
participating domains
scope
authority
trace
issuance time
expiration or review condition

Established:
A network-wide consequence requires a network-wide decision.

Changed
Updated:
scripts/validate_examples.py

to support v0.1 through v0.5.
Added semantic validation for:
SAFETY-INV-041 through SAFETY-INV-050

The validator now distinguishes:
schema failure
semantic invariant failure
expected FAIL fixture
unexpected failure

Changed
Added backward-compatible PASS / FAIL detection.
Legacy fixtures without:
metadata.expected_result

can still be classified from:
examples/pass/
examples/fail/

while v0.5 fixtures use explicit metadata.
This preserves older corpus compatibility while allowing stricter v0.5 semantic validation.
Changed
Updated:
.github/workflows/validate.yml

for v0.1 through v0.5.
The workflow now checks:
required repository files
required v0.5 fixtures
Python compilation
JSON syntax
JSON Schema validity
v0.3 reference corpus
v0.4 reference corpus
v0.5 reference corpus
v0.5 invariant coverage
integrated semantic validation
v0.5 corpus counts

Validation matrix:
Python 3.10
Python 3.12

Validation
GitHub Actions:
PASS

Reference corpus:
v0.1  PASS 1 / FAIL 10
v0.2  PASS 4 / FAIL 9
v0.3  PASS 1 / FAIL 10
v0.4  PASS 1 / FAIL 10
v0.5  PASS 1 / FAIL 10

Total:
PASS  8
FAIL  49
TOTAL 57

Architectural Progression
v0.5 completes the transition:
Structural Safety
      ↓
Machine-Readable Safety
      ↓
Causal Safety
      ↓
Branch Safety
      ↓
Federation Safety

[0.4.0]
Added
Introduced Branch / Merge Safety for parallel successor operations and merged execution paths.
Core principles:
A branch is not permission amplification.

A merge is not authority aggregation.

Added:
schemas/safety-branch-bundle.schema.json

Added PASS fixture:
examples/v0.4/pass/safety-branch-bundle-valid.json

Added FAIL fixtures:
examples/v0.4/fail/branch-identity-missing.json
examples/v0.4/fail/branch-authority-shared.json
examples/v0.4/fail/branch-inherits-parent-authority.json
examples/v0.4/fail/branch-verification-shared.json
examples/v0.4/fail/branch-trace-shared.json
examples/v0.4/fail/merge-without-compatibility-check.json
examples/v0.4/fail/merge-conflicting-authority.json
examples/v0.4/fail/branch-drops-parent-blocker.json
examples/v0.4/fail/branch-termination-propagates.json
examples/v0.4/fail/merge-outcome-missing.json

Added Invariants
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

Added Branch Authority Isolation
Each branch now requires independently scoped authority.
Established:
Auth A + Auth B ≠ Merged Authority

A merge requiring authority must obtain a new explicit authority reference.
Added Branch-Specific Verification
Parallel branches must retain independent verification identities.
Shared verification across distinct branches is treated as a safety failure.
Added Branch-Specific Trace
Every branch must remain independently reconstructable.
A shared trace identity must not erase the history of individual branches.
Added Blocker Carry-Forward
Open parent blockers must survive branching where applicable.
Branch creation must not silently delete unresolved safety conditions.
Added Local Branch Termination
Termination of one branch must not automatically terminate siblings.
Established local failure containment at branch level.
Added Merge Compatibility Checks
Merge operations must explicitly evaluate:
authority compatibility
state compatibility
blocker compatibility
verification compatibility
trace compatibility

Validation
Added v0.4 semantic validation to:
scripts/validate_examples.py

GitHub Actions validated the v0.4 corpus successfully.
[0.3.0]
Added
Introduced Cross-Receipt Safety Chain validation.
Core principle:
Validate the chain, not only the receipts.

Added:
schemas/safety-receipt-bundle.schema.json

Added PASS fixture:
examples/v0.3/pass/safety-receipt-bundle-valid.json

Added FAIL fixtures for:
receipt identity mismatch
subject discontinuity
authority/action mismatch
missing containment causal link
verification/containment mismatch
recovery/verification mismatch
broken safety chain
conflicting final states
receipt replay
trace discontinuity

Added Invariants
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

Added Receipt Chain Model
Introduced explicit causal relationships between:
Authority
Action
Containment
Verification
Recovery

Individually valid records are insufficient if they describe different causal events.
Added Replay Detection
A receipt already used in one safety chain must not be silently reused as though it belonged to another independent chain.
Added Trace Continuity
A valid safety bundle must preserve end-to-end reconstruction of the safety event.
[0.2.0]
Added
Introduced machine-readable safety receipts.
Core principle:
Authorize explicitly. Contain visibly. Verify independently. Recover traceably.

Added schemas:
schemas/authority-envelope.schema.json
schemas/containment-receipt.schema.json
schemas/verification-record.schema.json
schemas/recovery-receipt.schema.json

Added PASS fixtures for:
Authority Envelope
Containment Receipt
Independent Verification Record
Recovery Receipt

Added FAIL fixtures covering authority, containment, verification, and recovery failures.
Added Invariants
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

Added Authority Envelope
Defined machine-readable bounded authority for agent actions.
Added Containment Receipt
Containment transitions now require explicit records preserving safety evidence.
Added Independent Verification Record
Verification must be attributable to an independent verification identity.
Added Recovery Receipt
Recovery must explicitly reference the source safety state and must not silently restore previous privilege.
[0.1.0]
Added
Initial structural safety baseline.
Introduced the central thesis:
The primary danger is not malicious intent itself, but structures that convert malicious intent, error, or compromise into large-scale power.

Added:
README.md
SPEC.md
PRINCIPLES.md
ARCHITECTURE.md
mappings/tacp.md
mappings/authority.md
mappings/trace.md
mappings/zero-network.md
schemas/safety-assessment.schema.json
scripts/validate_examples.py
.github/workflows/validate.yml

Added Structural Principles
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
Temporal Least Authority
Human Fallibility

Added Invariants
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

Added Reference Lifecycle
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

Added Human Fallibility Model
Established:
AI checks AI
Rules check AI
Human checks AI
System checks human
Trace checks everyone

Preferred governance model:
Human-in-the-auditable-loop

Added Conceptual Risk Model
Systemic Risk
≈
Failure Potential
× Authority
× Speed
× Scope
× Persistence
× Connectivity

Added Core Principle
Do not attempt to eliminate all failure. Prevent failure from becoming systemic power.
