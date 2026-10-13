#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]

SCHEMAS_DIR = ROOT / "schemas"
EXAMPLES_DIR = ROOT / "examples"

SCHEMA_FILES = {
    "v0.1": SCHEMAS_DIR / "safety-assessment.schema.json",
    "v0.2-authority": SCHEMAS_DIR / "authority-envelope.schema.json",
    "v0.2-containment": SCHEMAS_DIR / "containment-receipt.schema.json",
    "v0.2-verification": SCHEMAS_DIR / "verification-record.schema.json",
    "v0.2-recovery": SCHEMAS_DIR / "recovery-receipt.schema.json",
    "v0.3": SCHEMAS_DIR / "safety-receipt-bundle.schema.json",
    "v0.4": SCHEMAS_DIR / "safety-branch-bundle.schema.json",
    "v0.5": SCHEMAS_DIR / "federated-safety-signal.schema.json",
}


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def fail(message: str) -> None:
    raise AssertionError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def nested_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data

    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def parse_datetime(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None

    try:
        if value.endswith("Z"):
            return datetime.fromisoformat(value[:-1] + "+00:00")
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def normalize_datetime(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt


def schema_errors(
    instance: Any,
    schema: dict[str, Any],
) -> list[str]:
    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    errors: list[str] = []

    for error in sorted(
        validator.iter_errors(instance),
        key=lambda e: list(e.absolute_path),
    ):
        location = "$"

        if error.absolute_path:
            location += "".join(
                f"[{repr(part)}]" if isinstance(part, int) else f".{part}"
                for part in error.absolute_path
            )

        errors.append(f"{location}: {error.message}")

    return errors


def expected_result(data: dict[str, Any]) -> str | None:
    result = nested_get(data, "metadata", "expected_result")

    if isinstance(result, str):
        return result.upper()

    return None


def expected_failed_invariants(data: dict[str, Any]) -> set[str]:
    invariants = nested_get(data, "metadata", "invariants", default={})

    if not isinstance(invariants, dict):
        return set()

    failed: set[str] = set()

    for invariant_id, result in invariants.items():
        if (
            isinstance(result, dict)
            and str(result.get("result", "")).upper() == "FAIL"
        ):
            failed.add(invariant_id)

    return failed


def unique_non_null(values: list[Any]) -> bool:
    filtered = [value for value in values if value is not None]
    return len(filtered) == len(set(filtered))


# ---------------------------------------------------------------------------
# v0.1
# ---------------------------------------------------------------------------


def validate_v01_semantics(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    invariants = nested_get(data, "metadata", "invariants", default={})

    if isinstance(invariants, dict):
        for invariant_id, info in invariants.items():
            if (
                isinstance(info, dict)
                and str(info.get("result", "")).upper() == "FAIL"
            ):
                violations.append(invariant_id)

    return violations


# ---------------------------------------------------------------------------
# v0.2
# ---------------------------------------------------------------------------


def validate_v02_authority(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    metadata = data.get("metadata", {})
    invariant_results = metadata.get("invariants", {})

    if isinstance(invariant_results, dict):
        for invariant_id, info in invariant_results.items():
            if (
                isinstance(info, dict)
                and str(info.get("result", "")).upper() == "FAIL"
            ):
                violations.append(invariant_id)

    return violations


def validate_v02_containment(data: dict[str, Any]) -> list[str]:
    return validate_v02_authority(data)


def validate_v02_verification(data: dict[str, Any]) -> list[str]:
    return validate_v02_authority(data)


def validate_v02_recovery(data: dict[str, Any]) -> list[str]:
    return validate_v02_authority(data)


# ---------------------------------------------------------------------------
# v0.3 — Cross-Receipt Safety Chain
# ---------------------------------------------------------------------------


def validate_v03_semantics(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    metadata = data.get("metadata", {})
    invariants = metadata.get("invariants", {})

    if isinstance(invariants, dict):
        for invariant_id, result in invariants.items():
            if (
                isinstance(result, dict)
                and str(result.get("result", "")).upper() == "FAIL"
            ):
                violations.append(invariant_id)

    return violations


# ---------------------------------------------------------------------------
# v0.4 — Branch / Merge Safety
# ---------------------------------------------------------------------------


def validate_v04_semantics(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    branches = data.get("branches", [])
    parent = data.get("parent", {})
    branch_policy = data.get("branch_policy", {})
    merge = data.get("merge", {})
    metadata = data.get("metadata", {})

    if not isinstance(branches, list):
        branches = []

    # SAFETY-INV-031 — Explicit Branch Declaration
    branch_ids = [
        branch.get("branch_id")
        for branch in branches
        if isinstance(branch, dict)
    ]

    if (
        not branch_ids
        or any(not branch_id for branch_id in branch_ids)
        or len(branch_ids) != len(set(branch_ids))
    ):
        violations.append("SAFETY-INV-031")

    # SAFETY-INV-032 — Branch Authority Isolation
    authority_refs: list[str] = []
    inv032_failed = False

    for branch in branches:
        if not isinstance(branch, dict):
            continue

        authority = branch.get("authority", {})

        if not isinstance(authority, dict):
            inv032_failed = True
            continue

        if authority.get("shared_with_siblings") is True:
            inv032_failed = True

        if authority.get("independent_scope") is not True:
            inv032_failed = True

        ref = authority.get("authority_reference")
        if isinstance(ref, str) and ref:
            authority_refs.append(ref)

    if not unique_non_null(authority_refs):
        inv032_failed = True

    if inv032_failed:
        violations.append("SAFETY-INV-032")

    # SAFETY-INV-033 — No Implicit Successor Inheritance
    parent_authority = (
        parent.get("source_authority_id")
        if isinstance(parent, dict)
        else None
    )

    inv033_failed = False

    for branch in branches:
        if not isinstance(branch, dict):
            continue

        authority = branch.get("authority", {})

        if not isinstance(authority, dict):
            continue

        if authority.get("inherited_from_parent") is True:
            inv033_failed = True

        if (
            parent_authority
            and authority.get("authority_reference") == parent_authority
        ):
            inv033_failed = True

    if inv033_failed:
        violations.append("SAFETY-INV-033")

    # SAFETY-INV-034 — Branch-Specific Verification
    verification_refs: list[str] = []
    inv034_failed = False

    for branch in branches:
        if not isinstance(branch, dict):
            continue

        verification = branch.get("verification", {})

        if not isinstance(verification, dict):
            inv034_failed = True
            continue

        if verification.get("branch_specific") is not True:
            inv034_failed = True

        ref = verification.get("verification_reference")
        if isinstance(ref, str) and ref:
            verification_refs.append(ref)

    if not unique_non_null(verification_refs):
        inv034_failed = True

    if inv034_failed:
        violations.append("SAFETY-INV-034")

    # SAFETY-INV-035 — Branch-Specific Trace
    trace_ids: list[str] = []
    inv035_failed = False

    for branch in branches:
        if not isinstance(branch, dict):
            continue

        trace = branch.get("trace", {})

        if not isinstance(trace, dict):
            inv035_failed = True
            continue

        if trace.get("independently_reconstructable") is not True:
            inv035_failed = True

        trace_id = trace.get("trace_id")
        if isinstance(trace_id, str) and trace_id:
            trace_ids.append(trace_id)

    if not unique_non_null(trace_ids):
        inv035_failed = True

    if inv035_failed:
        violations.append("SAFETY-INV-035")

    # SAFETY-INV-036 — Merge Requires Compatibility Check
    merge_requested = (
        merge.get("requested") is True
        if isinstance(merge, dict)
        else False
    )

    compatibility = (
        merge.get("compatibility_check", {})
        if isinstance(merge, dict)
        else {}
    )

    if merge_requested:
        dimensions = (
            "authority_compatible",
            "state_compatible",
            "blockers_compatible",
            "verification_compatible",
            "trace_compatible",
        )

        if not isinstance(compatibility, dict):
            violations.append("SAFETY-INV-036")
        else:
            if compatibility.get("performed") is not True:
                violations.append("SAFETY-INV-036")
            elif any(
                compatibility.get(dimension) is None
                for dimension in dimensions
            ):
                violations.append("SAFETY-INV-036")

    # SAFETY-INV-037 — No Conflicting Authority Merge
    authority_decision = (
        merge.get("authority_decision", {})
        if isinstance(merge, dict)
        else {}
    )

    merge_outcome = (
        merge.get("outcome", {})
        if isinstance(merge, dict)
        else {}
    )

    outcome_state = (
        merge_outcome.get("state")
        if isinstance(merge_outcome, dict)
        else None
    )

    inv037_failed = False

    if outcome_state == "MERGED":
        if (
            isinstance(compatibility, dict)
            and compatibility.get("authority_compatible") is False
        ):
            inv037_failed = True

        if (
            isinstance(authority_decision, dict)
            and authority_decision.get(
                "authority_aggregated_from_branches"
            )
            is True
        ):
            inv037_failed = True

        if isinstance(authority_decision, dict):
            if authority_decision.get("new_authority_required") is True:
                if not authority_decision.get("new_authority_reference"):
                    inv037_failed = True

    if inv037_failed:
        violations.append("SAFETY-INV-037")

    # SAFETY-INV-038 — Carried Blockers Must Survive Branching
    parent_blockers = metadata.get("parent_blockers", [])

    inv038_failed = False

    if isinstance(parent_blockers, list):
        for blocker in parent_blockers:
            if not isinstance(blocker, dict):
                continue

            if blocker.get("status") != "OPEN":
                continue

            blocker_id = blocker.get("blocker_id")
            applies_to_branch_ids = blocker.get(
                "applies_to_branch_ids",
                branch_ids,
            )

            if not isinstance(applies_to_branch_ids, list):
                applies_to_branch_ids = branch_ids

            for branch_id in applies_to_branch_ids:
                matching_branch = next(
                    (
                        branch
                        for branch in branches
                        if isinstance(branch, dict)
                        and branch.get("branch_id") == branch_id
                    ),
                    None,
                )

                if not matching_branch:
                    inv038_failed = True
                    continue

                blockers = matching_branch.get("blockers", [])

                matching_blocker = next(
                    (
                        item
                        for item in blockers
                        if isinstance(item, dict)
                        and item.get("blocker_id") == blocker_id
                    ),
                    None,
                )

                if not matching_blocker:
                    inv038_failed = True
                    continue

                if matching_blocker.get("carried_forward") is not True:
                    inv038_failed = True

                if matching_blocker.get("applies_to_branch") is not True:
                    inv038_failed = True

    if inv038_failed:
        violations.append("SAFETY-INV-038")

    # SAFETY-INV-039 — Branch Termination Must Be Local
    inv039_failed = False

    for branch in branches:
        if not isinstance(branch, dict):
            continue

        termination = branch.get("termination", {})

        if not isinstance(termination, dict):
            continue

        if termination.get("terminated") is True:
            if termination.get("local_only") is not True:
                inv039_failed = True

            affected = termination.get("affected_sibling_branch_ids", [])
            if affected:
                inv039_failed = True

    termination_failure = metadata.get(
        "termination_propagation_failure",
        {},
    )

    if (
        isinstance(termination_failure, dict)
        and termination_failure.get("locality_preserved") is False
    ):
        inv039_failed = True

    if inv039_failed:
        violations.append("SAFETY-INV-039")

    # SAFETY-INV-040 — Merge Outcome Must Be Explicit
    if merge_requested:
        allowed_outcomes = {
            "MERGED",
            "RESTRICTED",
            "HELD",
            "ISOLATED",
            "REJECTED",
            "TERMINATED",
        }

        if outcome_state not in allowed_outcomes:
            violations.append("SAFETY-INV-040")

    # branch_policy consistency
    if isinstance(branch_policy, dict):
        policy_checks = (
            (
                "explicit_branch_ids_required",
                True,
            ),
            (
                "authority_isolation_required",
                True,
            ),
            (
                "implicit_authority_inheritance_allowed",
                False,
            ),
            (
                "branch_specific_verification_required",
                True,
            ),
            (
                "branch_specific_trace_required",
                True,
            ),
            (
                "carry_open_blockers_required",
                True,
            ),
        )

        for key, expected in policy_checks:
            if key in branch_policy and branch_policy.get(key) != expected:
                fail(
                    f"v0.4 branch_policy.{key} must be "
                    f"{expected!r}"
                )

    return sorted(set(violations))


# ---------------------------------------------------------------------------
# v0.5 — Cross-Domain / Federation Safety
# ---------------------------------------------------------------------------


def validate_v05_semantics(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []

    source = data.get("source_domain", {})
    destination = data.get("destination", {})
    provenance = data.get("provenance", {})
    validity = data.get("validity", {})
    propagation = data.get("propagation", {})
    replay = data.get("replay_protection", {})
    recommended = data.get("recommended_response", {})
    local = data.get("local_processing", {})
    trace = data.get("trace", {})
    federation_decision = data.get("federation_decision")
    metadata = data.get("metadata", {})

    # ------------------------------------------------------------------
    # SAFETY-INV-041 — Explicit Domain Boundary
    # ------------------------------------------------------------------

    inv041_failed = False

    if not isinstance(source, dict):
        inv041_failed = True
    else:
        required_source_boundary_fields = (
            "domain_id",
            "authority_boundary_id",
            "policy_boundary_id",
            "execution_boundary_id",
        )

        for field in required_source_boundary_fields:
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                inv041_failed = True

    receiver_domain_id = (
        local.get("receiver_domain_id")
        if isinstance(local, dict)
        else None
    )

    source_domain_id = (
        source.get("domain_id")
        if isinstance(source, dict)
        else None
    )

    if not receiver_domain_id:
        inv041_failed = True

    if (
        source_domain_id
        and receiver_domain_id
        and source_domain_id == receiver_domain_id
    ):
        inv041_failed = True

    boundary_failure = metadata.get("domain_boundary_failure", {})

    if isinstance(boundary_failure, dict):
        if boundary_failure.get("authority_transition_determinable") is False:
            inv041_failed = True

    if inv041_failed:
        violations.append("SAFETY-INV-041")

    # ------------------------------------------------------------------
    # SAFETY-INV-042 — No Automatic Cross-Domain Authority Propagation
    # ------------------------------------------------------------------

    inv042_failed = False

    source_authority_ref = (
        provenance.get("source_authority_reference")
        if isinstance(provenance, dict)
        else None
    )

    local_authority = (
        local.get("local_authority", {})
        if isinstance(local, dict)
        else {}
    )

    if isinstance(local_authority, dict):
        if local_authority.get("remote_authority_accepted") is True:
            inv042_failed = True

        local_authority_ref = local_authority.get("authority_reference")

        if (
            source_authority_ref
            and local_authority_ref
            and source_authority_ref == local_authority_ref
        ):
            inv042_failed = True

    authority_failure = metadata.get(
        "cross_domain_authority_failure",
        {},
    )

    if isinstance(authority_failure, dict):
        if authority_failure.get("cross_domain_authority_propagated") is True:
            inv042_failed = True

    if inv042_failed:
        violations.append("SAFETY-INV-042")

    # ------------------------------------------------------------------
    # SAFETY-INV-043 — Safety Signal Provenance Required
    # ------------------------------------------------------------------

    inv043_failed = False

    if not isinstance(provenance, dict):
        inv043_failed = True
    else:
        provenance_fields = (
            "origin_event_id",
            "origin_trace_id",
            "origin_domain_id",
            "issued_at",
            "integrity_status",
        )

        for field in provenance_fields:
            value = provenance.get(field)
            if value is None or value == "":
                inv043_failed = True

        if (
            source_domain_id
            and provenance.get("origin_domain_id")
            and provenance.get("origin_domain_id") != source_domain_id
        ):
            inv043_failed = True

    if isinstance(trace, dict):
        if trace.get("origin_trace_preserved") is False:
            inv043_failed = True

    provenance_failure = metadata.get("provenance_failure", {})

    if isinstance(provenance_failure, dict):
        if provenance_failure.get("provenance_reconstructable") is False:
            inv043_failed = True

    if inv043_failed:
        violations.append("SAFETY-INV-043")

    # ------------------------------------------------------------------
    # SAFETY-INV-044 — Cross-Domain Signal Must Be Interpreted Locally
    # ------------------------------------------------------------------

    inv044_failed = False

    if not isinstance(local, dict):
        inv044_failed = True
    else:
        if local.get("interpreted_locally") is not True:
            inv044_failed = True

        local_decision = local.get("local_decision")

        actionable_decisions = {
            "LOCAL_HOLD",
            "LOCAL_RESTRICT",
            "LOCAL_ISOLATE",
            "LOCAL_RECOVER",
            "LOCAL_REAUTHORIZE",
            "LOCAL_TERMINATE",
            "ESCALATE_TO_FEDERATION",
        }

        if local_decision in actionable_decisions:
            interpretation = local.get("interpretation")

            if not isinstance(interpretation, str) or not interpretation.strip():
                inv044_failed = True

    interpretation_failure = metadata.get(
        "local_interpretation_failure",
        {},
    )

    if isinstance(interpretation_failure, dict):
        if (
            interpretation_failure.get(
                "direct_recommendation_to_decision_transition"
            )
            is True
        ):
            inv044_failed = True

    if inv044_failed:
        violations.append("SAFETY-INV-044")

    # ------------------------------------------------------------------
    # SAFETY-INV-045 — Remote Containment Requires Local Authorization
    # ------------------------------------------------------------------

    inv045_failed = False

    local_decision = (
        local.get("local_decision")
        if isinstance(local, dict)
        else None
    )

    containment_decisions = {
        "LOCAL_HOLD",
        "LOCAL_RESTRICT",
        "LOCAL_ISOLATE",
        "LOCAL_TERMINATE",
    }

    if local_decision in containment_decisions:
        if not isinstance(local_authority, dict):
            inv045_failed = True
        else:
            granted = local_authority.get("local_authority_granted")
            authority_ref = local_authority.get("authority_reference")
            preauth_ref = local_authority.get(
                "preauthorized_federation_rule_reference"
            )

            if granted is not True and not preauth_ref:
                inv045_failed = True

            if granted is True and not authority_ref and not preauth_ref:
                inv045_failed = True

    containment_failure = metadata.get(
        "remote_containment_failure",
        {},
    )

    if isinstance(containment_failure, dict):
        if (
            containment_failure.get(
                "containment_executed_without_local_authority"
            )
            is True
        ):
            inv045_failed = True

    if inv045_failed:
        violations.append("SAFETY-INV-045")

    # ------------------------------------------------------------------
    # SAFETY-INV-046 — Shared Threat Does Not Imply Shared Authority
    # ------------------------------------------------------------------

    inv046_failed = False

    if isinstance(federation_decision, dict):
        scope = federation_decision.get("scope", {})

        if isinstance(scope, dict):
            if scope.get("shared_execution_authority") is True:
                inv046_failed = True

            if scope.get("authority_model") == "SHARED_AUTHORITY":
                inv046_failed = True

        federation_authority_ref = federation_decision.get(
            "approving_authority_reference"
        )

        if (
            source_authority_ref
            and federation_authority_ref
            and federation_authority_ref == source_authority_ref
        ):
            affected_domains = []

            if isinstance(scope, dict):
                value = scope.get("affected_domains", [])
                if isinstance(value, list):
                    affected_domains = value

            if len(affected_domains) >= 1:
                inv046_failed = True

    shared_authority_failure = metadata.get(
        "shared_threat_authority_failure",
        {},
    )

    if isinstance(shared_authority_failure, dict):
        if shared_authority_failure.get(
            "shared_execution_authority_created"
        ) is True:
            inv046_failed = True

    if inv046_failed:
        violations.append("SAFETY-INV-046")

    # ------------------------------------------------------------------
    # SAFETY-INV-047 — Propagation Scope Must Be Bounded
    # ------------------------------------------------------------------

    inv047_failed = False

    if not isinstance(propagation, dict):
        inv047_failed = True
    else:
        if propagation.get("scope_bounded") is not True:
            inv047_failed = True

        max_hops = propagation.get("max_hops")
        current_hop = propagation.get("current_hop")
        max_relays = propagation.get("maximum_relay_count")

        if not isinstance(max_hops, int) or max_hops < 0:
            inv047_failed = True

        if not isinstance(current_hop, int) or current_hop < 0:
            inv047_failed = True

        if (
            isinstance(max_hops, int)
            and isinstance(current_hop, int)
            and current_hop > max_hops
        ):
            inv047_failed = True

        if max_relays is not None:
            if not isinstance(max_relays, int) or max_relays < 0:
                inv047_failed = True

        if propagation.get("forwarding_allowed") is False:
            if max_hops != 0:
                inv047_failed = True

    if not isinstance(validity, dict):
        inv047_failed = True
    else:
        valid_from = normalize_datetime(
            parse_datetime(validity.get("valid_from"))
        )
        expires_at = normalize_datetime(
            parse_datetime(validity.get("expires_at"))
        )
        ttl = validity.get("ttl_seconds")

        if valid_from is None or expires_at is None:
            inv047_failed = True
        elif expires_at <= valid_from:
            inv047_failed = True

        if not isinstance(ttl, int) or ttl <= 0:
            inv047_failed = True

    if isinstance(destination, dict):
        target_mode = destination.get("target_mode")

        if target_mode == "SPECIFIC_DOMAINS":
            targets = destination.get("target_domain_ids", [])

            if not isinstance(targets, list) or not targets:
                inv047_failed = True

        elif target_mode == "DOMAIN_CLASS":
            if not destination.get("target_domain_class"):
                inv047_failed = True

        elif target_mode == "FEDERATION":
            if not destination.get("federation_id"):
                inv047_failed = True

        else:
            inv047_failed = True
    else:
        inv047_failed = True

    propagation_failure = metadata.get(
        "propagation_scope_failure",
        {},
    )

    if isinstance(propagation_failure, dict):
        if propagation_failure.get("unbounded_forwarding_possible") is True:
            inv047_failed = True

    if inv047_failed:
        violations.append("SAFETY-INV-047")

    # ------------------------------------------------------------------
    # SAFETY-INV-048 — Cross-Domain Replay Must Be Rejected
    # ------------------------------------------------------------------

    inv048_failed = False

    if not isinstance(replay, dict):
        inv048_failed = True
    else:
        replay_detected = replay.get("replay_detected")
        previously_consumed = replay.get("previously_consumed")
        fresh = replay.get("fresh_for_current_context")
        context_substitution = replay.get(
            "context_substitution_detected"
        )

        signal_status = data.get("signal_status")

        replay_condition = (
            replay_detected is True
            or context_substitution is True
            or fresh is False
        )

        if replay_condition and signal_status not in {
            "REJECTED",
            "INVALID",
        }:
            inv048_failed = True

        if previously_consumed is True and fresh is True:
            inv048_failed = True

    replay_failure = metadata.get("replay_failure", {})

    if isinstance(replay_failure, dict):
        if replay_failure.get("treated_as_fresh_evidence") is True:
            inv048_failed = True

    # Fixture-specific semantic failure:
    # the signal is correctly marked INVALID, but metadata says a local
    # action was nevertheless selected from the replayed signal.
    if (
        isinstance(replay_failure, dict)
        and replay_failure.get("context_substitution_detected") is True
        and local_decision
        in {
            "LOCAL_HOLD",
            "LOCAL_RESTRICT",
            "LOCAL_ISOLATE",
            "LOCAL_RECOVER",
            "LOCAL_REAUTHORIZE",
            "LOCAL_TERMINATE",
        }
    ):
        inv048_failed = True

    if inv048_failed:
        violations.append("SAFETY-INV-048")

    # ------------------------------------------------------------------
    # SAFETY-INV-049 — Federated Recovery Must Preserve Domain Autonomy
    # ------------------------------------------------------------------

    inv049_failed = False

    if data.get("signal_type") == "RECOVERY_NOTICE":
        recovery_failure = metadata.get(
            "federated_recovery_failure",
            {},
        )

        if isinstance(recovery_failure, dict):
            if recovery_failure.get("receiver_auto_resumed") is True:
                inv049_failed = True

            if (
                recovery_failure.get(
                    "remote_recovery_treated_as_local_recovery"
                )
                is True
            ):
                inv049_failed = True

            if recovery_failure.get("old_local_authority_reused") is True:
                inv049_failed = True

            if (
                recovery_failure.get(
                    "receiver_local_verification_performed"
                )
                is False
                and local_decision
                in {
                    "LOCAL_RECOVER",
                    "LOCAL_REAUTHORIZE",
                }
            ):
                inv049_failed = True

    if local_decision in {
        "LOCAL_RECOVER",
        "LOCAL_REAUTHORIZE",
    }:
        recovery_failure = metadata.get(
            "federated_recovery_failure",
            {},
        )

        if isinstance(recovery_failure, dict):
            if recovery_failure.get("fresh_local_authority_issued") is False:
                inv049_failed = True

            if recovery_failure.get("receiver_blockers_rechecked") is False:
                inv049_failed = True

    if inv049_failed:
        violations.append("SAFETY-INV-049")

    # ------------------------------------------------------------------
    # SAFETY-INV-050 — Network-Wide Action Requires Explicit
    # Federation Decision
    # ------------------------------------------------------------------

    inv050_failed = False

    if local_decision == "ESCALATE_TO_FEDERATION":
        network_action_failure = metadata.get(
            "network_action_failure",
            {},
        )

        network_action_requested = False

        if isinstance(network_action_failure, dict):
            network_action_requested = (
                network_action_failure.get(
                    "network_wide_action_requested"
                )
                is True
            )

        if network_action_requested and not isinstance(
            federation_decision,
            dict,
        ):
            inv050_failed = True

    network_action_failure = metadata.get(
        "network_action_failure",
        {},
    )

    if isinstance(network_action_failure, dict):
        if (
            network_action_failure.get(
                "network_action_attempted_without_federation_decision"
            )
            is True
        ):
            inv050_failed = True

    if isinstance(federation_decision, dict):
        participating = federation_decision.get(
            "participating_domain_ids",
            []
        )

        if (
            not isinstance(participating, list)
            or len(set(participating)) < 2
        ):
            inv050_failed = True

        if not federation_decision.get("decision_id"):
            inv050_failed = True

        if not federation_decision.get("federation_id"):
            inv050_failed = True

        if not federation_decision.get("trace_reference"):
            inv050_failed = True

    if inv050_failed:
        violations.append("SAFETY-INV-050")

    return sorted(set(violations))


# ---------------------------------------------------------------------------
# Version discovery
# ---------------------------------------------------------------------------


def classify_example(path: Path) -> tuple[str, str]:
    relative = path.relative_to(ROOT).as_posix()

    if relative.startswith("examples/v0.5/"):
        return "v0.5", "v0.5"

    if relative.startswith("examples/v0.4/"):
        return "v0.4", "v0.4"

    if relative.startswith("examples/v0.3/"):
        return "v0.3", "v0.3"

    if relative.startswith("examples/v0.2/"):
        filename = path.name

        if "authority-envelope" in filename:
            return "v0.2", "v0.2-authority"

        if "containment" in filename:
            return "v0.2", "v0.2-containment"

        if "verification" in filename:
            return "v0.2", "v0.2-verification"

        if "recovery" in filename:
            return "v0.2", "v0.2-recovery"

        fail(
            f"Unable to determine v0.2 schema for "
            f"{relative}"
        )

    if relative.startswith("examples/pass/") or relative.startswith(
        "examples/fail/"
    ):
        return "v0.1", "v0.1"

    fail(f"Unknown example path: {relative}")


def semantic_violations(
    version: str,
    schema_key: str,
    data: dict[str, Any],
) -> list[str]:
    if version == "v0.1":
        return validate_v01_semantics(data)

    if version == "v0.2":
        if schema_key == "v0.2-authority":
            return validate_v02_authority(data)

        if schema_key == "v0.2-containment":
            return validate_v02_containment(data)

        if schema_key == "v0.2-verification":
            return validate_v02_verification(data)

        if schema_key == "v0.2-recovery":
            return validate_v02_recovery(data)

    if version == "v0.3":
        return validate_v03_semantics(data)

    if version == "v0.4":
        return validate_v04_semantics(data)

    if version == "v0.5":
        return validate_v05_semantics(data)

    fail(f"No semantic validator for version: {version}")


# ---------------------------------------------------------------------------
# Fixture validation
# ---------------------------------------------------------------------------


def validate_example(
    path: Path,
    schemas: dict[str, dict[str, Any]],
) -> tuple[str, str, list[str], list[str]]:
    version, schema_key = classify_example(path)
    data = load_json(path)

    require(
        isinstance(data, dict),
        f"{path}: top-level JSON value must be an object",
    )

    schema = schemas[schema_key]

    structural_errors = schema_errors(data, schema)
    semantic_errors = semantic_violations(
        version,
        schema_key,
        data,
    )

    expected = expected_result(data)

    if expected not in {"PASS", "FAIL"}:
        fail(
            f"{path}: metadata.expected_result must be PASS or FAIL"
        )

    expected_invariants = expected_failed_invariants(data)
    actual_invariants = set(semantic_errors)

    relative = path.relative_to(ROOT).as_posix()

    if expected == "PASS":
        require(
            not structural_errors,
            (
                f"{relative}: PASS fixture has schema errors:\n  - "
                + "\n  - ".join(structural_errors)
            ),
        )

        require(
            not semantic_errors,
            (
                f"{relative}: PASS fixture violates invariants: "
                + ", ".join(semantic_errors)
            ),
        )

        require(
            not expected_invariants,
            (
                f"{relative}: PASS fixture metadata marks invariants "
                f"as FAIL: {sorted(expected_invariants)}"
            ),
        )

        if version in {"v0.4", "v0.5"}:
            require(
                data.get("signal_status") != "INVALID"
                if version == "v0.5"
                else data.get("bundle_status") != "INVALID",
                f"{relative}: PASS fixture cannot have INVALID status",
            )

    else:
        require(
            structural_errors or semantic_errors,
            (
                f"{relative}: FAIL fixture unexpectedly passed both "
                "schema and semantic validation"
            ),
        )

        require(
            expected_invariants,
            (
                f"{relative}: FAIL fixture must declare at least one "
                "failed invariant in metadata.invariants"
            ),
        )

        if semantic_errors:
            require(
                expected_invariants == actual_invariants,
                (
                    f"{relative}: metadata invariant failures do not "
                    f"match semantic validator.\n"
                    f"expected metadata: "
                    f"{sorted(expected_invariants)}\n"
                    f"actual semantic: "
                    f"{sorted(actual_invariants)}"
                ),
            )

        if version == "v0.4":
            require(
                data.get("bundle_status") == "INVALID",
                (
                    f"{relative}: v0.4 FAIL fixture must use "
                    "bundle_status=INVALID"
                ),
            )

        if version == "v0.5":
            require(
                data.get("signal_status") == "INVALID",
                (
                    f"{relative}: v0.5 FAIL fixture must use "
                    "signal_status=INVALID"
                ),
            )

    return (
        version,
        expected,
        structural_errors,
        semantic_errors,
    )


# ---------------------------------------------------------------------------
# Corpus discovery
# ---------------------------------------------------------------------------


def discover_examples() -> list[Path]:
    roots = [
        EXAMPLES_DIR / "pass",
        EXAMPLES_DIR / "fail",
        EXAMPLES_DIR / "v0.2",
        EXAMPLES_DIR / "v0.3",
        EXAMPLES_DIR / "v0.4",
        EXAMPLES_DIR / "v0.5",
    ]

    examples: list[Path] = []

    for root in roots:
        if not root.exists():
            continue

        examples.extend(
            path
            for path in root.rglob("*.json")
            if path.is_file()
        )

    return sorted(set(examples))


# ---------------------------------------------------------------------------
# Corpus expectations
# ---------------------------------------------------------------------------


EXPECTED_V05_FILES = {
    "examples/v0.5/pass/federated-safety-signal-valid.json",
    "examples/v0.5/fail/domain-boundary-missing.json",
    "examples/v0.5/fail/cross-domain-authority-propagates.json",
    "examples/v0.5/fail/signal-provenance-missing.json",
    (
        "examples/v0.5/fail/"
        "remote-signal-executed-without-local-interpretation.json"
    ),
    (
        "examples/v0.5/fail/"
        "remote-containment-without-local-authorization.json"
    ),
    "examples/v0.5/fail/shared-threat-creates-shared-authority.json",
    "examples/v0.5/fail/signal-propagation-unbounded.json",
    "examples/v0.5/fail/cross-domain-signal-replay.json",
    (
        "examples/v0.5/fail/"
        "remote-recovery-auto-resumes-local-domain.json"
    ),
    (
        "examples/v0.5/fail/"
        "network-action-without-federation-decision.json"
    ),
}


def validate_corpus_shape(examples: list[Path]) -> None:
    relative_paths = {
        path.relative_to(ROOT).as_posix()
        for path in examples
    }

    missing_v05 = EXPECTED_V05_FILES - relative_paths

    require(
        not missing_v05,
        (
            "Missing required v0.5 fixtures:\n  - "
            + "\n  - ".join(sorted(missing_v05))
        ),
    )

    v05_paths = [
        path
        for path in examples
        if path.relative_to(ROOT)
        .as_posix()
        .startswith("examples/v0.5/")
    ]

    v05_pass = [
        path
        for path in v05_paths
        if "/pass/" in path.relative_to(ROOT).as_posix()
    ]

    v05_fail = [
        path
        for path in v05_paths
        if "/fail/" in path.relative_to(ROOT).as_posix()
    ]

    require(
        len(v05_pass) == 1,
        (
            f"v0.5 corpus must contain exactly 1 PASS fixture; "
            f"found {len(v05_pass)}"
        ),
    )

    require(
        len(v05_fail) == 10,
        (
            f"v0.5 corpus must contain exactly 10 FAIL fixtures; "
            f"found {len(v05_fail)}"
        ),
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=== Resilient AI Safety Principles Validation ===")
    print()

    schemas: dict[str, dict[str, Any]] = {}

    print("[schemas] Loading schemas")

    for schema_key, schema_path in SCHEMA_FILES.items():
        require(
            schema_path.exists(),
            f"Missing schema: {schema_path.relative_to(ROOT)}",
        )

        schema = load_json(schema_path)

        require(
            isinstance(schema, dict),
            (
                f"{schema_path.relative_to(ROOT)}: "
                "schema must be a JSON object"
            ),
        )

        Draft202012Validator.check_schema(schema)
        schemas[schema_key] = schema

        print(
            f"  [schema-ok] "
            f"{schema_path.relative_to(ROOT).as_posix()}"
        )

    print()

    examples = discover_examples()

    require(
        examples,
        "No JSON example fixtures found",
    )

    validate_corpus_shape(examples)

    counts: dict[str, dict[str, int]] = {}

    for path in examples:
        relative = path.relative_to(ROOT).as_posix()

        try:
            (
                version,
                expected,
                structural_errors,
                semantic_errors,
            ) = validate_example(
                path,
                schemas,
            )
        except Exception as exc:
            print(f"[FAIL] {relative}")
            print(f"       {exc}")
            return 1

        counts.setdefault(
            version,
            {
                "PASS": 0,
                "FAIL": 0,
            },
        )

        counts[version][expected] += 1

        if expected == "PASS":
            print(f"[PASS] {relative}")
        else:
            detected = sorted(
                set(semantic_errors)
                | (
                    {"SCHEMA"}
                    if structural_errors
                    else set()
                )
            )

            print(
                f"[EXPECTED-FAIL] {relative}"
                + (
                    " -> " + ", ".join(detected)
                    if detected
                    else ""
                )
            )

    print()
    print("=== Validation Summary ===")

    version_order = [
        "v0.1",
        "v0.2",
        "v0.3",
        "v0.4",
        "v0.5",
    ]

    total_pass = 0
    total_fail = 0

    for version in version_order:
        values = counts.get(
            version,
            {
                "PASS": 0,
                "FAIL": 0,
            },
        )

        total_pass += values["PASS"]
        total_fail += values["FAIL"]

        print(
            f"{version}: "
            f"PASS={values['PASS']} "
            f"FAIL={values['FAIL']}"
        )

    print(
        f"Total: PASS={total_pass} "
        f"FAIL={total_fail} "
        f"EXAMPLES={total_pass + total_fail}"
    )

    print()
    print("[ok] All expected validation outcomes matched.")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"[fatal] {exc}")
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"[fatal] Invalid JSON: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"[fatal] Unexpected error: {exc}")
        sys.exit(1)
