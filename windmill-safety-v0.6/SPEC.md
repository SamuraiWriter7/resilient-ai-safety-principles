# Resilient AI Safety Principles v0.6 — Windmill Blade Safety Bridge

Status: experimental **synthetic** conformance adapter, supplementary to v0.1–v0.5.

## Applicability
The Kazene Windmill v1.0 outer blades are replaceable workers, not authorities. The bridge maps blade failure and exchange to Containment, Verification, and Recovery concepts; it does not redefine existing receipt schemas.

## Normative invariants
- External attack sources MUST NOT receive authority over protective control or be modified as part of this design.
- Loss of central heartbeat, common infrastructure failure, or critical pressure MUST require P and independent perimeter safeguards.
- Failed blades MUST be isolated; operating D/R MUST pause to N or P.
- N and P MUST stop new untrusted interactions; P MUST stop observation workers.
- R MUST process only stored Trace, never initiate active contact with an attack source.
- Blade swap MUST revoke the previous lease and obtain independently checked signature, authorization, Trace integrity, post-swap health, and review before release.
- A blade MUST NOT authorize its own restoration; lack of verified evidence means hold, never silent release.
- Pressure numbers 85 and 95 are synthetic demonstration thresholds only.

## Verification
`python3 windmill-safety-v0.6/scripts/validate.py`

Tests model signals and expected policies. They DO NOT verify actual cryptographic signatures, fail-stop behavior, live GPTs, concurrent tasks, or production-grade isolation. Before deployment, implement independently enforced boundaries and fault injection under realistic loads.
