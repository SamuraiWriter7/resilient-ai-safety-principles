#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]


# ============================================================================
# Schema paths
# ============================================================================

V01_SCHEMA_PATH = ROOT / "schemas" / "safety-assessment.schema.json"

V02_SCHEMA_PATHS = {
    "authority-envelope": ROOT / "schemas" / "authority-envelope.schema.json",
    "containment-receipt": ROOT / "schemas" / "containment-receipt.schema.json",
    "verification-record": ROOT / "schemas" / "verification-record.schema.json",
    "recovery-receipt": ROOT / "schemas" / "recovery-receipt.schema.json",
}

V03_SCHEMA_PATH = ROOT / "schemas" / "safety-receipt-bundle.schema.json"

V04_SCHEMA_PATH = ROOT / "schemas" / "safety-branch-bundle.schema.json"


# ============================================================================
# Example directories
# ============================================================================

V01_PASS_DIR = ROOT / "examples" / "pass"
V01_FAIL_DIR = ROOT / "examples" / "fail"

V02_PASS_DIR = ROOT / "examples" / "v0.2" / "pass"
V02_FAIL_DIR = ROOT / "examples" / "v0.2" / "fail"

V03_PASS_DIR = ROOT / "examples" / "v0.3" / "pass"
V03_FAIL_DIR = ROOT / "examples" / "v0.3" / "fail"

V04_PASS_DIR = ROOT / "examples" / "v0.4" / "pass"
V04_FAIL_DIR = ROOT / "examples" / "v0.4" / "fail"


# ============================================================================
# Invariants
# ============================================================================

V01_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(1, 11)
}

V02_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(11, 21)
}

V03_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(21, 31)
}

V04_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(31, 41)
}


@dataclass
class ValidationResult:
    path: Path
    expected_result: str
    schema_name: str
    valid: bool
    errors: list[str]


# ============================================================================
# Generic helpers
# ============================================================================


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def format_schema_path(error: Any) -> str:
    if not error.absolute_path:
        return "$"

    parts: list[str] = []

    for item in error.absolute_path:
        if isinstance(item, int):
            parts.append(f"[{item}]")
        else:
            if parts:
                parts.append(".")
            parts.append(str(item))

    return "$." + "".join(parts)


def validate_schema_document(
    schema_path: Path,
) -> tuple[dict[str, Any], Draft202012Validator]:
    schema = load_json(schema_path)

    Draft202012Validator.check_schema(schema)

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    return schema, validator


def schema_errors(
    instance: dict[str, Any],
    validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []

    ordered = sorted(
        validator.iter_errors(instance),
        key=lambda error: list(error.absolute_path),
    )

    for error in ordered:
        errors.append(
            f"{format_schema_path(error)}: {error.message}"
        )

    return errors


def get_expected_result_from_path(path: Path) -> str:
    lowered = {
        part.lower()
        for part in path.parts
    }

    if "pass" in lowered:
        return "PASS"

    if "fail" in lowered:
        return "FAIL"

    raise ValueError(
        f"Cannot determine expected PASS/FAIL result from path: {path}"
    )


def discover_json_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []

    return sorted(
        path
        for path in directory.rglob("*.json")
        if path.is_file()
    )


def get_metadata(
    instance: dict[str, Any],
) -> dict[str, Any]:
    metadata = instance.get("metadata")

    if isinstance(metadata, dict):
        return metadata

    return {}


def get_declared_expected_result(
    instance: dict[str, Any],
) -> str | None:
    direct = instance.get("expected_result")

    if isinstance(direct, str):
        return direct

    metadata = get_metadata(instance)
    nested = metadata.get("expected_result")

    if isinstance(nested, str):
        return nested

    return None


def get_invariants(
    instance: dict[str, Any],
) -> dict[str, Any]:
    direct = instance.get("invariants")

    if isinstance(direct, dict):
        return direct

    metadata = get_metadata(instance)
    nested = metadata.get("invariants")

    if isinstance(nested, dict):
        return nested

    return {}


def get_violations(
    instance: dict[str, Any],
) -> list[dict[str, Any]]:
    direct = instance.get("violations")

    if isinstance(direct, list):
        return [
            item
            for item in direct
            if isinstance(item, dict)
        ]

    metadata = get_metadata(instance)
    nested = metadata.get("violations")

    if isinstance(nested, list):
        return [
            item
            for item in nested
            if isinstance(item, dict)
        ]

    return []


def validate_expected_result(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    declared = get_declared_expected_result(instance)

    if (
        declared is not None
        and declared != expected_result
    ):
        errors.append(
            "expected result mismatch: "
            f"path expects {expected_result}, "
            f"document declares {declared}"
        )

    return errors


def require_exact_invariants(
    instance: dict[str, Any],
    expected_invariants: set[str],
) -> list[str]:
    errors: list[str] = []

    present = set(get_invariants(instance).keys())

    missing = sorted(
        expected_invariants - present
    )

    extra = sorted(
        present - expected_invariants
    )

    if missing:
        errors.append(
            "missing invariants: "
            + ", ".join(missing)
        )

    if extra:
        errors.append(
            "unexpected invariants: "
            + ", ".join(extra)
        )

    return errors


def validate_invariant_subset(
    instance: dict[str, Any],
    relevant_invariants: set[str],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    invariants = get_invariants(instance)

    if not invariants:
        return ["invariant assessments are missing"]

    failing: set[str] = set()

    for invariant_id in sorted(
        set(invariants) & relevant_invariants
    ):
        assessment = invariants[invariant_id]

        if not isinstance(assessment, dict):
            errors.append(
                f"{invariant_id}: assessment must be an object"
            )
            continue

        result = assessment.get("result")
        reason = assessment.get("reason")

        if result not in {
            "PASS",
            "FAIL",
            "NOT_APPLICABLE",
        }:
            errors.append(
                f"{invariant_id}: invalid result {result!r}"
            )

        if (
            not isinstance(reason, str)
            or not reason.strip()
        ):
            errors.append(
                f"{invariant_id}: non-empty reason is required"
            )

        if result == "FAIL":
            failing.add(invariant_id)

    if expected_result == "PASS" and failing:
        errors.append(
            "PASS example contains failing invariants: "
            + ", ".join(sorted(failing))
        )

    if expected_result == "FAIL" and not failing:
        errors.append(
            "FAIL example does not contain a failing relevant invariant"
        )

    for violation in get_violations(instance):
        invariant_id = violation.get("invariant")

        if invariant_id not in relevant_invariants:
            continue

        assessment = invariants.get(invariant_id)

        if (
            not isinstance(assessment, dict)
            or assessment.get("result") != "FAIL"
        ):
            errors.append(
                "violation references invariant not marked FAIL: "
                f"{invariant_id}"
            )

    return errors


def invariant_is_fail(
    instance: dict[str, Any],
    invariant_id: str,
) -> bool:
    assessment = get_invariants(instance).get(invariant_id)

    return (
        isinstance(assessment, dict)
        and assessment.get("result") == "FAIL"
    )


def require_failure(
    instance: dict[str, Any],
    invariant_id: str,
    message: str,
) -> list[str]:
    if invariant_is_fail(
        instance,
        invariant_id,
    ):
        return []

    return [
        f"{message}; {invariant_id} must be FAIL"
    ]


def relative_path(path: Path) -> str:
    try:
        return str(
            path.relative_to(ROOT)
        )
    except ValueError:
        return str(path)


# ============================================================================
# v0.1
# ============================================================================


def validate_v01_semantics(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    errors.extend(
        validate_expected_result(
            instance,
            expected_result,
        )
    )

    errors.extend(
        require_exact_invariants(
            instance,
            V01_INVARIANTS,
        )
    )

    errors.extend(
        validate_invariant_subset(
            instance,
            V01_INVARIANTS,
            expected_result,
        )
    )

    conformance = instance.get("conformance")

    if isinstance(conformance, dict):
        result = conformance.get("result")

        if result != expected_result:
            errors.append(
                "conformance.result mismatch: "
                f"expected {expected_result}, got {result!r}"
            )

        if expected_result == "FAIL":
            primary = conformance.get("primary_failure")

            if not isinstance(primary, str):
                errors.append(
                    "FAIL example requires conformance.primary_failure"
                )
            elif primary not in V01_INVARIANTS:
                errors.append(
                    f"invalid primary_failure: {primary}"
                )
            elif not invariant_is_fail(
                instance,
                primary,
            ):
                errors.append(
                    "primary_failure invariant must be marked FAIL"
                )

    trace = instance.get("trace")

    if isinstance(trace, dict):
        complete = trace.get("causal_chain_complete")
        missing = trace.get("missing_links")

        if isinstance(missing, list):
            if complete is True and missing:
                errors.append(
                    "trace.causal_chain_complete=true "
                    "but missing_links is non-empty"
                )

            if complete is False and not missing:
                errors.append(
                    "trace.causal_chain_complete=false "
                    "but missing_links is empty"
                )

    return errors


# ============================================================================
# v0.2
# ============================================================================


def validate_v02_common(
    instance: dict[str, Any],
    expected_result: str,
    relevant_invariants: set[str],
) -> list[str]:
    errors: list[str] = []

    errors.extend(
        validate_expected_result(
            instance,
            expected_result,
        )
    )

    errors.extend(
        validate_invariant_subset(
            instance,
            relevant_invariants,
            expected_result,
        )
    )

    return errors


def validate_authority_envelope(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    relevant = {
        "SAFETY-INV-011",
        "SAFETY-INV-012",
        "SAFETY-INV-013",
    }

    errors = validate_v02_common(
        instance,
        expected_result,
        relevant,
    )

    metadata = get_metadata(instance)
    mutation = metadata.get("mutation")

    if isinstance(mutation, dict):
        if (
            mutation.get("subject_self_modified") is True
            and mutation.get(
                "independent_authority_reissue_present"
            ) is not True
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-012",
                    "authority self-expansion detected",
                )
            )

    validity = instance.get("validity")
    context = metadata.get("validation_context")

    if (
        isinstance(validity, dict)
        and isinstance(context, dict)
    ):
        valid_until = validity.get("valid_until")
        evaluated_at = context.get("evaluated_at")

        if (
            isinstance(valid_until, str)
            and isinstance(evaluated_at, str)
        ):
            try:
                expired = (
                    parse_datetime(evaluated_at)
                    >= parse_datetime(valid_until)
                )

                if (
                    expired
                    and instance.get("status") == "ACTIVE"
                ):
                    errors.extend(
                        require_failure(
                            instance,
                            "SAFETY-INV-013",
                            "expired ACTIVE authority",
                        )
                    )

            except ValueError as exc:
                errors.append(
                    f"authority datetime parse error: {exc}"
                )

    return errors


def validate_containment_receipt(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    relevant = {
        "SAFETY-INV-014",
        "SAFETY-INV-015",
    }

    errors = validate_v02_common(
        instance,
        expected_result,
        relevant,
    )

    metadata = get_metadata(instance)
    recording = metadata.get("recording_status")

    if isinstance(recording, dict):
        if (
            recording.get("transition_occurred") is True
            and recording.get(
                "receipt_created_at_transition_time"
            ) is False
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-014",
                    "containment transition was not recorded contemporaneously",
                )
            )

    evidence = instance.get("evidence_preservation")

    if isinstance(evidence, dict):
        evidence_ok = all(
            evidence.get(flag) is True
            for flag in [
                "state_preserved",
                "trace_preserved",
                "trigger_evidence_preserved",
            ]
        )

        if not evidence_ok:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-015",
                    "containment evidence preservation incomplete",
                )
            )

    return errors


def calculate_oldest_evidence_age_seconds(
    instance: dict[str, Any],
) -> int | None:
    verified_at = instance.get("verified_at")

    if not isinstance(verified_at, str):
        return None

    evidence = instance.get("evidence")

    if not isinstance(evidence, dict):
        return None

    items = evidence.get("items")

    if not isinstance(items, list) or not items:
        return None

    observed_times: list[datetime] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        observed_at = item.get("observed_at")

        if isinstance(observed_at, str):
            observed_times.append(
                parse_datetime(observed_at)
            )

    if not observed_times:
        return None

    age = (
        parse_datetime(verified_at)
        - min(observed_times)
    ).total_seconds()

    return max(0, int(age))


def validate_verification_record(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    relevant = {
        "SAFETY-INV-016",
        "SAFETY-INV-017",
    }

    errors = validate_v02_common(
        instance,
        expected_result,
        relevant,
    )

    verifier = instance.get("verifier")

    if isinstance(verifier, dict):
        independent = (
            verifier.get("independent_from_subject") is True
            and verifier.get("independent_from_executor") is True
        )

        if not independent:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-016",
                    "verifier is not independent",
                )
            )

    evidence = instance.get("evidence")

    if isinstance(evidence, dict):
        freshness = evidence.get("freshness")

        if isinstance(freshness, dict):
            max_age = freshness.get("max_age_seconds")

            try:
                actual_age = calculate_oldest_evidence_age_seconds(
                    instance
                )
            except ValueError as exc:
                errors.append(
                    f"verification datetime parse error: {exc}"
                )
                actual_age = None

            if (
                isinstance(max_age, int)
                and actual_age is not None
                and actual_age > max_age
            ):
                errors.extend(
                    require_failure(
                        instance,
                        "SAFETY-INV-017",
                        "verification uses stale evidence",
                    )
                )

    return errors


def validate_recovery_receipt(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    relevant = {
        "SAFETY-INV-018",
        "SAFETY-INV-019",
        "SAFETY-INV-020",
    }

    errors = validate_v02_common(
        instance,
        expected_result,
        relevant,
    )

    source_state = instance.get("source_state")

    if not isinstance(source_state, dict):
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-018",
                "recovery source_state missing",
            )
        )
    else:
        source_reference = source_state.get(
            "source_reference"
        )

        if (
            not isinstance(source_reference, str)
            or not source_reference.strip()
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-018",
                    "recovery source_reference missing",
                )
            )

    authority_outcome = instance.get("authority_outcome")

    if isinstance(authority_outcome, dict):
        restored = authority_outcome.get(
            "previous_authority_restored"
        )

        if restored is True:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-019",
                    "previous authority restored",
                )
            )

        if instance.get("final_state") == "REAUTHORIZED":
            new_required = authority_outcome.get(
                "new_authority_required"
            )
            new_reference = authority_outcome.get(
                "new_authority_reference"
            )

            if (
                restored is True
                or new_required is not True
                or not isinstance(new_reference, str)
                or not new_reference.strip()
            ):
                errors.extend(
                    require_failure(
                        instance,
                        "SAFETY-INV-019",
                        "REAUTHORIZED recovery lacks fresh authority",
                    )
                )

    final_state = instance.get("final_state")

    if (
        not isinstance(final_state, str)
        or not final_state.strip()
    ):
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-020",
                "recovery final_state missing",
            )
        )

    return errors


def detect_v02_schema_name(
    instance: dict[str, Any],
    path: Path,
) -> str | None:
    name = path.name.lower()

    if (
        "authority-envelope" in name
        or "authority_envelope_id" in instance
    ):
        return "authority-envelope"

    if (
        "containment-receipt" in name
        or "containment_receipt_id" in instance
    ):
        return "containment-receipt"

    if (
        "verification-record" in name
        or name.startswith("verification-")
        or "verification_id" in instance
    ):
        return "verification-record"

    if (
        "recovery-receipt" in name
        or name.startswith("recovery-")
        or "recovery_receipt_id" in instance
    ):
        return "recovery-receipt"

    return None


V02_SEMANTIC_VALIDATORS: dict[
    str,
    Callable[[dict[str, Any], str], list[str]],
] = {
    "authority-envelope": validate_authority_envelope,
    "containment-receipt": validate_containment_receipt,
    "verification-record": validate_verification_record,
    "recovery-receipt": validate_recovery_receipt,
}


# ============================================================================
# v0.3 helpers
# ============================================================================


def get_receipts(
    instance: dict[str, Any],
) -> dict[str, Any]:
    value = instance.get("receipts")
    return value if isinstance(value, dict) else {}


def get_receipt(
    instance: dict[str, Any],
    name: str,
) -> dict[str, Any] | None:
    value = get_receipts(instance).get(name)
    return value if isinstance(value, dict) else None


def receipt_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(receipt, dict):
        return None

    value = receipt.get("receipt_id")
    return value if isinstance(value, str) else None


def receipt_operation_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(receipt, dict):
        return None

    value = receipt.get("operation_id")
    return value if isinstance(value, str) else None


def receipt_subject_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(receipt, dict):
        return None

    value = receipt.get("subject_id")
    return value if isinstance(value, str) else None


def get_chain_links(
    instance: dict[str, Any],
) -> list[dict[str, Any]]:
    chain = instance.get("chain")

    if not isinstance(chain, dict):
        return []

    links = chain.get("links")

    if not isinstance(links, list):
        return []

    return [
        item
        for item in links
        if isinstance(item, dict)
    ]


def has_chain_link(
    instance: dict[str, Any],
    source: str,
    target: str,
    relation: str | None = None,
) -> bool:
    for link in get_chain_links(instance):
        if (
            link.get("from") != source
            or link.get("to") != target
        ):
            continue

        if (
            relation is None
            or link.get("relation") == relation
        ):
            return True

    return False


def current_operation_id(
    instance: dict[str, Any],
) -> str | None:
    operation = instance.get("operation")

    if not isinstance(operation, dict):
        return None

    value = operation.get("operation_id")
    return value if isinstance(value, str) else None


def successor_operation_id(
    instance: dict[str, Any],
) -> str | None:
    operation = instance.get("operation")

    if not isinstance(operation, dict):
        return None

    value = operation.get("successor_operation_id")
    return value if isinstance(value, str) else None


def required_v03_receipt_ids(
    instance: dict[str, Any],
) -> set[str]:
    result: set[str] = set()

    for receipt in get_receipts(instance).values():
        if not isinstance(receipt, dict):
            continue

        value = receipt.get("receipt_id")

        if isinstance(value, str):
            result.add(value)

    return result


# ============================================================================
# v0.3 semantics
# ============================================================================


def validate_v03_semantics(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    errors.extend(
        validate_expected_result(
            instance,
            expected_result,
        )
    )

    errors.extend(
        require_exact_invariants(
            instance,
            V03_INVARIANTS,
        )
    )

    errors.extend(
        validate_invariant_subset(
            instance,
            V03_INVARIANTS,
            expected_result,
        )
    )

    operation_id = current_operation_id(instance)
    successor_id = successor_operation_id(instance)

    subject = instance.get("subject")
    bundle_subject_id = None

    if isinstance(subject, dict):
        value = subject.get("subject_id")
        if isinstance(value, str):
            bundle_subject_id = value

    authority = get_receipt(instance, "authority")
    containment = get_receipt(instance, "containment")
    verification = get_receipt(instance, "verification")
    recovery = get_receipt(instance, "recovery")
    successor_authority = get_receipt(
        instance,
        "successor_authority",
    )

    authority_id = receipt_id(authority)
    containment_id = receipt_id(containment)
    verification_id = receipt_id(verification)
    recovery_id = receipt_id(recovery)

    # 021
    identity_mismatch = False

    for receipt in [
        authority,
        containment,
        verification,
        recovery,
    ]:
        if receipt is None:
            continue

        receipt_op = receipt_operation_id(receipt)

        if (
            receipt_op is not None
            and operation_id is not None
            and receipt_op != operation_id
        ):
            identity_mismatch = True

    if successor_authority is not None:
        successor_receipt_op = receipt_operation_id(
            successor_authority
        )

        if (
            successor_id is not None
            and successor_receipt_op is not None
            and successor_receipt_op != successor_id
        ):
            identity_mismatch = True

    if identity_mismatch:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-021",
                "receipt identity mismatch",
            )
        )

    # 022
    expected_subject = bundle_subject_id or operation_id
    discontinuity = False

    for receipt in [
        containment,
        verification,
        recovery,
    ]:
        if receipt is None:
            continue

        subject_id = receipt_subject_id(receipt)

        if (
            expected_subject is not None
            and subject_id is not None
            and subject_id != expected_subject
        ):
            discontinuity = True

    if discontinuity:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-022",
                "subject continuity broken",
            )
        )

    # 023
    authority_bound = False

    if authority_id and operation_id:
        authority_bound = (
            receipt_operation_id(authority) == operation_id
            and (
                has_chain_link(
                    instance,
                    authority_id,
                    operation_id,
                    "AUTHORIZES",
                )
                or has_chain_link(
                    instance,
                    operation_id,
                    authority_id,
                    "ATTEMPTED_UNDER",
                )
            )
        )

    if not authority_bound:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-023",
                "authority not bound to operation",
            )
        )

    # 024
    if containment is not None:
        causal = (
            bool(containment_id and operation_id)
            and (
                has_chain_link(
                    instance,
                    operation_id,
                    containment_id,
                    "TRIGGERED_CONTAINMENT",
                )
                or has_chain_link(
                    instance,
                    operation_id,
                    containment_id,
                    "CONTAINS",
                )
            )
        )

        if not causal:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-024",
                    "containment causal link missing",
                )
            )

    # 025
    if containment is not None and verification is not None:
        valid = (
            bool(containment_id and verification_id)
            and has_chain_link(
                instance,
                containment_id,
                verification_id,
                "VERIFIES",
            )
        )

        if not valid:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-025",
                    "verification does not reference containment",
                )
            )

    # 026
    if verification is not None and recovery is not None:
        valid = (
            bool(verification_id and recovery_id)
            and has_chain_link(
                instance,
                verification_id,
                recovery_id,
                "JUSTIFIES_RECOVERY",
            )
        )

        if not valid:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-026",
                    "recovery does not reference verification",
                )
            )

    chain = instance.get("chain")

    # 027
    if isinstance(chain, dict):
        complete = chain.get("complete")
        missing = chain.get("missing_links")

        broken = (
            complete is False
            or (
                isinstance(missing, list)
                and bool(missing)
            )
        )

        if broken:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-027",
                    "safety chain incomplete",
                )
            )

    # 028
    if isinstance(chain, dict):
        states = chain.get("declared_final_states")

        conflict = (
            chain.get("conflicting_final_states") is True
            or (
                isinstance(states, list)
                and len(set(states)) > 1
            )
        )

        if conflict:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-028",
                    "conflicting final states detected",
                )
            )

    # 029
    if isinstance(chain, dict):
        replayed = chain.get("replayed_receipt_ids")

        replay = (
            chain.get("replay_detected") is True
            or (
                isinstance(replayed, list)
                and bool(replayed)
            )
        )

        if replay:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-029",
                    "receipt replay detected",
                )
            )

    # 030
    trace = instance.get("trace")

    if isinstance(trace, dict):
        required = required_v03_receipt_ids(instance)

        reachable_raw = trace.get("reachable_receipt_ids")
        missing_raw = trace.get("missing_receipt_ids")

        reachable = (
            set(reachable_raw)
            if isinstance(reachable_raw, list)
            else set()
        )

        missing = (
            set(missing_raw)
            if isinstance(missing_raw, list)
            else set()
        )

        calculated_missing = required - reachable

        broken = (
            trace.get("all_receipts_reachable") is not True
            or trace.get("trace_continuity") != "COMPLETE"
            or bool(calculated_missing)
            or bool(missing)
        )

        if broken:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-030",
                    "bundle trace continuity incomplete",
                )
            )

    return errors


# ============================================================================
# v0.4 helpers
# ============================================================================


def get_branches(
    instance: dict[str, Any],
) -> list[dict[str, Any]]:
    branches = instance.get("branches")

    if not isinstance(branches, list):
        return []

    return [
        branch
        for branch in branches
        if isinstance(branch, dict)
    ]


def get_merge(
    instance: dict[str, Any],
) -> dict[str, Any]:
    merge = instance.get("merge")

    return merge if isinstance(merge, dict) else {}


def get_branch_policy(
    instance: dict[str, Any],
) -> dict[str, Any]:
    policy = instance.get("branch_policy")

    return policy if isinstance(policy, dict) else {}


def get_parent(
    instance: dict[str, Any],
) -> dict[str, Any]:
    parent = instance.get("parent")

    return parent if isinstance(parent, dict) else {}


def branch_id(
    branch: dict[str, Any],
) -> str | None:
    value = branch.get("branch_id")
    return value if isinstance(value, str) else None


def branch_authority(
    branch: dict[str, Any],
) -> dict[str, Any]:
    value = branch.get("authority")
    return value if isinstance(value, dict) else {}


def branch_verification(
    branch: dict[str, Any],
) -> dict[str, Any]:
    value = branch.get("verification")
    return value if isinstance(value, dict) else {}


def branch_trace(
    branch: dict[str, Any],
) -> dict[str, Any]:
    value = branch.get("trace")
    return value if isinstance(value, dict) else {}


def branch_termination(
    branch: dict[str, Any],
) -> dict[str, Any]:
    value = branch.get("termination")
    return value if isinstance(value, dict) else {}


# ============================================================================
# v0.4 semantics
# ============================================================================


def validate_v04_semantics(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    errors.extend(
        validate_expected_result(
            instance,
            expected_result,
        )
    )

    errors.extend(
        require_exact_invariants(
            instance,
            V04_INVARIANTS,
        )
    )

    errors.extend(
        validate_invariant_subset(
            instance,
            V04_INVARIANTS,
            expected_result,
        )
    )

    branches = get_branches(instance)
    parent = get_parent(instance)
    policy = get_branch_policy(instance)
    merge = get_merge(instance)

    # ---------------------------------------------------------------------
    # SAFETY-INV-031 — Explicit Branch Declaration
    # ---------------------------------------------------------------------

    branch_ids = [
        branch_id(branch)
        for branch in branches
    ]

    missing_branch_identity = any(
        value is None or not value.strip()
        for value in branch_ids
    )

    duplicate_branch_identity = (
        len(
            [
                value
                for value in branch_ids
                if isinstance(value, str)
            ]
        )
        != len(
            set(
                value
                for value in branch_ids
                if isinstance(value, str)
            )
        )
    )

    if (
        missing_branch_identity
        or duplicate_branch_identity
    ):
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-031",
                "branch identity missing or duplicated",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-032 — Branch Authority Isolation
    # ---------------------------------------------------------------------

    authority_refs: list[str] = []
    authority_isolation_failure = False

    for branch in branches:
        authority = branch_authority(branch)

        reference = authority.get("authority_reference")

        if isinstance(reference, str):
            authority_refs.append(reference)

        if (
            authority.get("shared_with_siblings") is True
            or authority.get("independent_scope") is not True
        ):
            authority_isolation_failure = True

    if len(authority_refs) != len(set(authority_refs)):
        authority_isolation_failure = True

    if authority_isolation_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-032",
                "branch authority isolation violated",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-033 — No Implicit Successor Inheritance
    # ---------------------------------------------------------------------

    parent_authority = parent.get("source_authority_id")
    inheritance_failure = False

    for branch in branches:
        authority = branch_authority(branch)

        reference = authority.get("authority_reference")

        if authority.get("inherited_from_parent") is True:
            inheritance_failure = True

        if (
            isinstance(parent_authority, str)
            and isinstance(reference, str)
            and reference == parent_authority
        ):
            inheritance_failure = True

    if inheritance_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-033",
                "parent authority implicitly inherited",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-034 — Branch-Specific Verification
    # ---------------------------------------------------------------------

    verification_refs: list[str] = []
    verification_failure = False

    for branch in branches:
        verification = branch_verification(branch)

        reference = verification.get("verification_reference")

        if isinstance(reference, str):
            verification_refs.append(reference)

        if verification.get("branch_specific") is not True:
            verification_failure = True

    if (
        verification_refs
        and len(verification_refs)
        != len(set(verification_refs))
    ):
        verification_failure = True

    if verification_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-034",
                "verification is not branch-specific",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-035 — Branch-Specific Trace
    # ---------------------------------------------------------------------

    trace_ids: list[str] = []
    trace_failure = False

    for branch in branches:
        trace = branch_trace(branch)

        trace_id = trace.get("trace_id")

        if isinstance(trace_id, str):
            trace_ids.append(trace_id)

        if trace.get("independently_reconstructable") is not True:
            trace_failure = True

    if (
        trace_ids
        and len(trace_ids) != len(set(trace_ids))
    ):
        trace_failure = True

    if trace_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-035",
                "branch-specific trace requirement violated",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-036 — Merge Requires Compatibility Check
    # ---------------------------------------------------------------------

    merge_requested = merge.get("requested") is True

    compatibility = merge.get("compatibility_check")

    if not isinstance(compatibility, dict):
        compatibility = {}

    compatibility_dimensions = [
        "authority_compatible",
        "state_compatible",
        "blockers_compatible",
        "verification_compatible",
        "trace_compatible",
    ]

    if merge_requested:
        compatibility_failure = (
            compatibility.get("performed") is not True
        )

        if compatibility.get("performed") is True:
            if any(
                compatibility.get(key) is None
                for key in compatibility_dimensions
            ):
                compatibility_failure = True

        if compatibility_failure:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-036",
                    "merge compatibility check missing or incomplete",
                )
            )

    # ---------------------------------------------------------------------
    # SAFETY-INV-037 — No Conflicting Authority Merge
    # ---------------------------------------------------------------------

    authority_decision = merge.get("authority_decision")

    if not isinstance(authority_decision, dict):
        authority_decision = {}

    outcome = merge.get("outcome")

    if not isinstance(outcome, dict):
        outcome = {}

    if merge_requested:
        authority_merge_failure = False

        if (
            compatibility.get("authority_compatible") is False
            and outcome.get("state") == "MERGED"
        ):
            authority_merge_failure = True

        if (
            authority_decision.get(
                "authority_aggregated_from_branches"
            )
            is True
        ):
            authority_merge_failure = True

        if (
            outcome.get("state") == "MERGED"
            and authority_decision.get(
                "new_authority_required"
            )
            is True
        ):
            new_authority = authority_decision.get(
                "new_authority_reference"
            )

            if (
                not isinstance(new_authority, str)
                or not new_authority.strip()
            ):
                authority_merge_failure = True

        if authority_merge_failure:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-037",
                    "conflicting or aggregated authority merge detected",
                )
            )

    # ---------------------------------------------------------------------
    # SAFETY-INV-038 — Carried Blockers Must Survive Branching
    # ---------------------------------------------------------------------

    metadata = get_metadata(instance)

    parent_blockers = metadata.get("parent_blockers")

    blocker_failure = False

    if isinstance(parent_blockers, list):
        branches_by_id = {
            branch_id(branch): branch
            for branch in branches
            if branch_id(branch)
        }

        for parent_blocker in parent_blockers:
            if not isinstance(parent_blocker, dict):
                continue

            blocker_identifier = parent_blocker.get("blocker_id")

            if not isinstance(blocker_identifier, str):
                continue

            if parent_blocker.get("status") != "OPEN":
                continue

            applicable = parent_blocker.get(
                "applies_to_branch_ids"
            )

            if not isinstance(applicable, list):
                continue

            for applicable_branch_id in applicable:
                branch = branches_by_id.get(
                    applicable_branch_id
                )

                if branch is None:
                    blocker_failure = True
                    continue

                blockers = branch.get("blockers")

                if not isinstance(blockers, list):
                    blocker_failure = True
                    continue

                matches = [
                    blocker
                    for blocker in blockers
                    if (
                        isinstance(blocker, dict)
                        and blocker.get("blocker_id")
                        == blocker_identifier
                    )
                ]

                if not matches:
                    blocker_failure = True
                    continue

                if not any(
                    blocker.get("carried_forward") is True
                    and blocker.get("applies_to_branch") is True
                    for blocker in matches
                ):
                    blocker_failure = True

    if blocker_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-038",
                "open blocker was not carried to affected branch",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-039 — Branch Termination Must Be Local
    # ---------------------------------------------------------------------

    termination_failure = False

    for branch in branches:
        termination = branch_termination(branch)

        if not termination:
            continue

        if termination.get("terminated") is True:
            affected = termination.get(
                "affected_sibling_branch_ids"
            )

            if (
                termination.get("local_only") is not True
                or (
                    isinstance(affected, list)
                    and bool(affected)
                )
            ):
                termination_failure = True

    propagation = metadata.get(
        "termination_propagation_failure"
    )

    if isinstance(propagation, dict):
        if (
            propagation.get(
                "termination_locality_preserved"
            )
            is False
        ):
            termination_failure = True

    if termination_failure:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-039",
                "branch termination propagated beyond local branch",
            )
        )

    # ---------------------------------------------------------------------
    # SAFETY-INV-040 — Merge Outcome Must Be Explicit
    # ---------------------------------------------------------------------

    if merge_requested:
        state = outcome.get("state")

        allowed_states = {
            "MERGED",
            "RESTRICTED",
            "HELD",
            "ISOLATED",
            "REJECTED",
            "TERMINATED",
        }

        if (
            not isinstance(state, str)
            or state not in allowed_states
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-040",
                    "merge outcome is missing or non-authoritative",
                )
            )

    # ---------------------------------------------------------------------
    # Bundle-level consistency
    # ---------------------------------------------------------------------

    bundle_status = instance.get("bundle_status")

    if (
        expected_result == "PASS"
        and bundle_status == "INVALID"
    ):
        errors.append(
            "PASS v0.4 fixture cannot have bundle_status INVALID"
        )

    if (
        expected_result == "FAIL"
        and bundle_status != "INVALID"
    ):
        errors.append(
            "FAIL v0.4 fixture should use bundle_status INVALID"
        )

    # Policy consistency
    if policy:
        if (
            policy.get("explicit_branch_ids_required")
            is not True
        ):
            errors.append(
                "branch policy must require explicit branch IDs"
            )

        if (
            policy.get("authority_isolation_required")
            is not True
        ):
            errors.append(
                "branch policy must require authority isolation"
            )

        if (
            policy.get(
                "implicit_authority_inheritance_allowed"
            )
            is not False
        ):
            errors.append(
                "branch policy must forbid implicit authority inheritance"
            )

        if (
            policy.get(
                "branch_specific_verification_required"
            )
            is not True
        ):
            errors.append(
                "branch policy must require branch-specific verification"
            )

        if (
            policy.get("branch_specific_trace_required")
            is not True
        ):
            errors.append(
                "branch policy must require branch-specific trace"
            )

        if (
            policy.get("carry_open_blockers_required")
            is not True
        ):
            errors.append(
                "branch policy must require open blocker carry-forward"
            )

    return errors


# ============================================================================
# File validation
# ============================================================================


def validate_v01_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected = get_expected_result_from_path(path)

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path,
            expected,
            "v0.1-safety-assessment",
            False,
            [f"JSON load error: {exc}"],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path,
            expected,
            "v0.1-safety-assessment",
            False,
            ["top-level JSON value must be an object"],
        )

    errors = schema_errors(
        instance,
        validator,
    )

    errors.extend(
        validate_v01_semantics(
            instance,
            expected,
        )
    )

    return ValidationResult(
        path,
        expected,
        "v0.1-safety-assessment",
        not errors,
        errors,
    )


def validate_v02_file(
    path: Path,
    validators: dict[str, Draft202012Validator],
) -> ValidationResult:
    expected = get_expected_result_from_path(path)

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path,
            expected,
            "unknown",
            False,
            [f"JSON load error: {exc}"],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path,
            expected,
            "unknown",
            False,
            ["top-level JSON value must be an object"],
        )

    schema_name = detect_v02_schema_name(
        instance,
        path,
    )

    if schema_name is None:
        return ValidationResult(
            path,
            expected,
            "unknown",
            False,
            ["unable to determine v0.2 schema type"],
        )

    raw_schema_errors = schema_errors(
        instance,
        validators[schema_name],
    )

    errors: list[str] = []

    # Negative fixtures may intentionally be schema-invalid.
    if expected == "PASS":
        errors.extend(raw_schema_errors)

    errors.extend(
        V02_SEMANTIC_VALIDATORS[schema_name](
            instance,
            expected,
        )
    )

    return ValidationResult(
        path,
        expected,
        schema_name,
        not errors,
        errors,
    )


def validate_v03_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected = get_expected_result_from_path(path)

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path,
            expected,
            "safety-receipt-bundle",
            False,
            [f"JSON load error: {exc}"],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path,
            expected,
            "safety-receipt-bundle",
            False,
            ["top-level JSON value must be an object"],
        )

    raw_schema_errors = schema_errors(
        instance,
        validator,
    )

    errors: list[str] = []

    if expected == "PASS":
        errors.extend(raw_schema_errors)

    errors.extend(
        validate_v03_semantics(
            instance,
            expected,
        )
    )

    return ValidationResult(
        path,
        expected,
        "safety-receipt-bundle",
        not errors,
        errors,
    )


def validate_v04_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected = get_expected_result_from_path(path)

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path,
            expected,
            "safety-branch-bundle",
            False,
            [f"JSON load error: {exc}"],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path,
            expected,
            "safety-branch-bundle",
            False,
            ["top-level JSON value must be an object"],
        )

    raw_schema_errors = schema_errors(
        instance,
        validator,
    )

    errors: list[str] = []

    # v0.4 FAIL corpus intentionally includes schema-invalid fixtures:
    # - missing branch_id
    # - compatibility check omitted
    # - conflicting authority merge
    # - merge outcome state missing
    #
    # Therefore structural Schema errors are fatal only for PASS fixtures.
    if expected == "PASS":
        errors.extend(raw_schema_errors)

    errors.extend(
        validate_v04_semantics(
            instance,
            expected,
        )
    )

    return ValidationResult(
        path,
        expected,
        "safety-branch-bundle",
        not errors,
        errors,
    )


# ============================================================================
# Output
# ============================================================================


def print_result(
    result: ValidationResult,
) -> None:
    prefix = (
        "[valid]"
        if result.valid
        else "[invalid]"
    )

    print(
        f"{prefix} "
        f"{relative_path(result.path)} "
        f"({result.schema_name}, "
        f"expected={result.expected_result})"
    )

    for error in result.errors:
        print(f"  - {error}")


def expected_count(
    results: list[ValidationResult],
    expected: str,
) -> int:
    return sum(
        1
        for result in results
        if result.expected_result == expected
    )


# ============================================================================
# Main
# ============================================================================


def main() -> int:
    print(
        "=== Resilient AI Safety Principles Validation ==="
    )
    print()

    try:
        _, v01_validator = validate_schema_document(
            V01_SCHEMA_PATH
        )

        v02_validators: dict[
            str,
            Draft202012Validator,
        ] = {}

        for schema_name, schema_path in V02_SCHEMA_PATHS.items():
            _, validator = validate_schema_document(
                schema_path
            )
            v02_validators[schema_name] = validator

        _, v03_validator = validate_schema_document(
            V03_SCHEMA_PATH
        )

        _, v04_validator = validate_schema_document(
            V04_SCHEMA_PATH
        )

    except FileNotFoundError as exc:
        print(
            f"[fatal] required schema missing: {exc}"
        )
        return 2

    except json.JSONDecodeError as exc:
        print(
            f"[fatal] invalid schema JSON: {exc}"
        )
        return 2

    except Exception as exc:
        print(
            f"[fatal] schema setup failed: {exc}"
        )
        return 2

    v01_files = (
        discover_json_files(V01_PASS_DIR)
        + discover_json_files(V01_FAIL_DIR)
    )

    v02_files = (
        discover_json_files(V02_PASS_DIR)
        + discover_json_files(V02_FAIL_DIR)
    )

    v03_files = (
        discover_json_files(V03_PASS_DIR)
        + discover_json_files(V03_FAIL_DIR)
    )

    v04_files = (
        discover_json_files(V04_PASS_DIR)
        + discover_json_files(V04_FAIL_DIR)
    )

    if not any(
        [
            v01_files,
            v02_files,
            v03_files,
            v04_files,
        ]
    ):
        print(
            "[fatal] no example JSON files found"
        )
        return 2

    results: list[ValidationResult] = []

    if v01_files:
        print("## v0.1")
        print()

        for path in v01_files:
            result = validate_v01_file(
                path,
                v01_validator,
            )
            results.append(result)
            print_result(result)

        print()

    if v02_files:
        print("## v0.2")
        print()

        for path in v02_files:
            result = validate_v02_file(
                path,
                v02_validators,
            )
            results.append(result)
            print_result(result)

        print()

    if v03_files:
        print("## v0.3")
        print()

        for path in v03_files:
            result = validate_v03_file(
                path,
                v03_validator,
            )
            results.append(result)
            print_result(result)

        print()

    if v04_files:
        print("## v0.4")
        print()

        for path in v04_files:
            result = validate_v04_file(
                path,
                v04_validator,
            )
            results.append(result)
            print_result(result)

        print()

    invalid_results = [
        result
        for result in results
        if not result.valid
    ]

    v01_results = [
        result
        for result in results
        if result.schema_name
        == "v0.1-safety-assessment"
    ]

    v02_results = [
        result
        for result in results
        if result.schema_name
        in V02_SCHEMA_PATHS
    ]

    v03_results = [
        result
        for result in results
        if result.schema_name
        == "safety-receipt-bundle"
    ]

    v04_results = [
        result
        for result in results
        if result.schema_name
        == "safety-branch-bundle"
    ]

    print("=== Summary ===")
    print()

    print(
        "v0.1 PASS examples : "
        f"{expected_count(v01_results, 'PASS')}"
    )
    print(
        "v0.1 FAIL examples : "
        f"{expected_count(v01_results, 'FAIL')}"
    )

    print(
        "v0.2 PASS examples : "
        f"{expected_count(v02_results, 'PASS')}"
    )
    print(
        "v0.2 FAIL examples : "
        f"{expected_count(v02_results, 'FAIL')}"
    )

    print(
        "v0.3 PASS examples : "
        f"{expected_count(v03_results, 'PASS')}"
    )
    print(
        "v0.3 FAIL examples : "
        f"{expected_count(v03_results, 'FAIL')}"
    )

    print(
        "v0.4 PASS examples : "
        f"{expected_count(v04_results, 'PASS')}"
    )
    print(
        "v0.4 FAIL examples : "
        f"{expected_count(v04_results, 'FAIL')}"
    )

    print(
        "Validated          : "
        f"{len(results)}/{len(results)}"
    )

    print(
        "Invalid            : "
        f"{len(invalid_results)}"
    )

    if invalid_results:
        print()
        print(
            "Validation reports are incomplete "
            "or an expectation failed."
        )
        return 1

    print()
    print(
        "All examples validated successfully."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
