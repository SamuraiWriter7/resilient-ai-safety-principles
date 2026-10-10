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

V01_SCHEMA_PATH = ROOT / "schemas" / "safety-assessment.schema.json"

V02_SCHEMA_PATHS = {
    "authority-envelope": ROOT / "schemas" / "authority-envelope.schema.json",
    "containment-receipt": ROOT / "schemas" / "containment-receipt.schema.json",
    "verification-record": ROOT / "schemas" / "verification-record.schema.json",
    "recovery-receipt": ROOT / "schemas" / "recovery-receipt.schema.json",
}

V01_PASS_DIR = ROOT / "examples" / "pass"
V01_FAIL_DIR = ROOT / "examples" / "fail"

V02_PASS_DIR = ROOT / "examples" / "v0.2" / "pass"
V02_FAIL_DIR = ROOT / "examples" / "v0.2" / "fail"

V01_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(1, 11)
}

V02_INVARIANTS = {
    f"SAFETY-INV-{number:03d}"
    for number in range(11, 21)
}


@dataclass
class ValidationResult:
    path: Path
    expected_result: str
    schema_name: str
    valid: bool
    errors: list[str]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))

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
        location = format_schema_path(error)
        errors.append(f"{location}: {error.message}")

    return errors


def get_expected_result_from_path(path: Path) -> str:
    lowered = {part.lower() for part in path.parts}

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


def get_metadata(instance: dict[str, Any]) -> dict[str, Any]:
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

    if declared is not None and declared != expected_result:
        errors.append(
            "expected result mismatch: "
            f"path expects {expected_result}, "
            f"document declares {declared}"
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
        return errors

    present = set(invariants.keys())
    relevant_present = present & relevant_invariants

    for invariant_id in sorted(relevant_present):
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

        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"{invariant_id}: non-empty reason is required"
            )

    failing = {
        invariant_id
        for invariant_id in relevant_present
        if isinstance(invariants[invariant_id], dict)
        and invariants[invariant_id].get("result") == "FAIL"
    }

    if expected_result == "PASS" and failing:
        errors.append(
            "PASS example contains failing invariants: "
            + ", ".join(sorted(failing))
        )

    if (
        expected_result == "FAIL"
        and relevant_present
        and not failing
    ):
        errors.append(
            "FAIL example does not contain a failing relevant invariant"
        )

    for violation in get_violations(instance):
        invariant_id = violation.get("invariant")

        if invariant_id not in relevant_invariants:
            continue

        assessment = invariants.get(invariant_id)

        if not isinstance(assessment, dict):
            errors.append(
                "violation references invariant without "
                f"assessment: {invariant_id}"
            )
            continue

        if assessment.get("result") != "FAIL":
            errors.append(
                "violation references invariant not marked FAIL: "
                f"{invariant_id}"
            )

    return errors


# ---------------------------------------------------------------------------
# v0.1 semantic validation
# ---------------------------------------------------------------------------


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

    conformance = instance.get("conformance")

    if isinstance(conformance, dict):
        result = conformance.get("result")

        if result != expected_result:
            errors.append(
                "conformance.result mismatch: "
                f"expected {expected_result}, got {result!r}"
            )

        primary_failure = conformance.get("primary_failure")

        if expected_result == "FAIL":
            if not isinstance(primary_failure, str):
                errors.append(
                    "FAIL example requires "
                    "conformance.primary_failure"
                )
            elif primary_failure not in V01_INVARIANTS:
                errors.append(
                    "invalid primary_failure: "
                    f"{primary_failure}"
                )

    invariants = instance.get("invariants")

    if isinstance(invariants, dict):
        present = set(invariants.keys())

        if present != V01_INVARIANTS:
            missing = sorted(V01_INVARIANTS - present)
            extra = sorted(present - V01_INVARIANTS)

            if missing:
                errors.append(
                    "missing v0.1 invariants: "
                    + ", ".join(missing)
                )

            if extra:
                errors.append(
                    "unexpected v0.1 invariants: "
                    + ", ".join(extra)
                )

        errors.extend(
            validate_invariant_subset(
                instance,
                V01_INVARIANTS,
                expected_result,
            )
        )

        if (
            expected_result == "FAIL"
            and isinstance(conformance, dict)
        ):
            primary_failure = conformance.get(
                "primary_failure"
            )

            if (
                isinstance(primary_failure, str)
                and primary_failure in invariants
            ):
                assessment = invariants[
                    primary_failure
                ]

                if (
                    not isinstance(assessment, dict)
                    or assessment.get("result") != "FAIL"
                ):
                    errors.append(
                        "primary_failure invariant must "
                        "itself be marked FAIL"
                    )

    trace = instance.get("trace")

    if isinstance(trace, dict):
        causal_complete = trace.get(
            "causal_chain_complete"
        )
        missing_links = trace.get("missing_links")

        if isinstance(missing_links, list):
            if (
                causal_complete is True
                and missing_links
            ):
                errors.append(
                    "trace.causal_chain_complete=true "
                    "but missing_links is non-empty"
                )

            if (
                causal_complete is False
                and not missing_links
            ):
                errors.append(
                    "trace.causal_chain_complete=false "
                    "but missing_links is empty"
                )

    return errors


# ---------------------------------------------------------------------------
# v0.2 common helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Authority Envelope
# SAFETY-INV-011 .. 013
# ---------------------------------------------------------------------------


def validate_authority_envelope(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors = validate_v02_common(
        instance,
        expected_result,
        {
            "SAFETY-INV-011",
            "SAFETY-INV-012",
            "SAFETY-INV-013",
        },
    )

    metadata = get_metadata(instance)

    mutation = metadata.get("mutation")

    if isinstance(mutation, dict):
        self_modified = mutation.get(
            "subject_self_modified"
        )
        reissued = mutation.get(
            "independent_authority_reissue_present"
        )

        if (
            self_modified is True
            and reissued is not True
        ):
            if expected_result != "FAIL":
                errors.append(
                    "authority self-expansion detected "
                    "without independent re-issuance"
                )

            invariants = get_invariants(instance)
            assessment = invariants.get(
                "SAFETY-INV-012"
            )

            if (
                isinstance(assessment, dict)
                and assessment.get("result") != "FAIL"
            ):
                errors.append(
                    "SAFETY-INV-012 must be FAIL when "
                    "subject self-expansion is detected"
                )

    validity = instance.get("validity")
    status = instance.get("status")

    if isinstance(validity, dict):
        valid_until = validity.get("valid_until")

        metadata_context = metadata.get(
            "validation_context"
        )

        evaluated_at = None

        if isinstance(metadata_context, dict):
            evaluated_at = metadata_context.get(
                "evaluated_at"
            )

        if (
            isinstance(valid_until, str)
            and isinstance(evaluated_at, str)
        ):
            try:
                expiry = parse_datetime(valid_until)
                evaluation_time = parse_datetime(
                    evaluated_at
                )

                expired = evaluation_time >= expiry

                if expired and status == "ACTIVE":
                    invariants = get_invariants(
                        instance
                    )
                    assessment = invariants.get(
                        "SAFETY-INV-013"
                    )

                    if (
                        not isinstance(
                            assessment,
                            dict,
                        )
                        or assessment.get("result")
                        != "FAIL"
                    ):
                        errors.append(
                            "expired ACTIVE authority "
                            "must fail SAFETY-INV-013"
                        )

                    if expected_result != "FAIL":
                        errors.append(
                            "expired ACTIVE authority "
                            "cannot be a PASS example"
                        )

            except ValueError as exc:
                errors.append(
                    f"authority datetime parse error: {exc}"
                )

    return errors


# ---------------------------------------------------------------------------
# Containment Receipt
# SAFETY-INV-014 .. 015
# ---------------------------------------------------------------------------


def validate_containment_receipt(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors = validate_v02_common(
        instance,
        expected_result,
        {
            "SAFETY-INV-014",
            "SAFETY-INV-015",
        },
    )

    metadata = get_metadata(instance)

    recording_status = metadata.get(
        "recording_status"
    )

    if isinstance(recording_status, dict):
        transition_occurred = recording_status.get(
            "transition_occurred"
        )
        created_at_transition = (
            recording_status.get(
                "receipt_created_at_transition_time"
            )
        )

        if (
            transition_occurred is True
            and created_at_transition is False
        ):
            invariants = get_invariants(instance)
            assessment = invariants.get(
                "SAFETY-INV-014"
            )

            if (
                not isinstance(assessment, dict)
                or assessment.get("result") != "FAIL"
            ):
                errors.append(
                    "unrecorded containment transition "
                    "must fail SAFETY-INV-014"
                )

    evidence = instance.get(
        "evidence_preservation"
    )

    if isinstance(evidence, dict):
        required_flags = [
            "state_preserved",
            "trace_preserved",
            "trigger_evidence_preserved",
        ]

        evidence_ok = all(
            evidence.get(flag) is True
            for flag in required_flags
        )

        invariants = get_invariants(instance)
        assessment = invariants.get(
            "SAFETY-INV-015"
        )

        if not evidence_ok:
            if (
                not isinstance(assessment, dict)
                or assessment.get("result") != "FAIL"
            ):
                errors.append(
                    "missing containment evidence "
                    "preservation must fail "
                    "SAFETY-INV-015"
                )

            if expected_result != "FAIL":
                errors.append(
                    "containment PASS example must "
                    "preserve state, trace, and trigger "
                    "evidence"
                )

    return errors


# ---------------------------------------------------------------------------
# Verification Record
# SAFETY-INV-016 .. 017
# ---------------------------------------------------------------------------


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

    verification_time = parse_datetime(
        verified_at
    )

    observed_times: list[datetime] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        observed_at = item.get("observed_at")

        if not isinstance(observed_at, str):
            continue

        observed_times.append(
            parse_datetime(observed_at)
        )

    if not observed_times:
        return None

    oldest = min(observed_times)

    age = (
        verification_time - oldest
    ).total_seconds()

    return max(0, int(age))


def validate_verification_record(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors = validate_v02_common(
        instance,
        expected_result,
        {
            "SAFETY-INV-016",
            "SAFETY-INV-017",
        },
    )

    verifier = instance.get("verifier")

    if isinstance(verifier, dict):
        independent_subject = verifier.get(
            "independent_from_subject"
        )
        independent_executor = verifier.get(
            "independent_from_executor"
        )

        independent = (
            independent_subject is True
            and independent_executor is True
        )

        invariants = get_invariants(instance)
        assessment = invariants.get(
            "SAFETY-INV-016"
        )

        if not independent:
            if (
                not isinstance(assessment, dict)
                or assessment.get("result") != "FAIL"
            ):
                errors.append(
                    "non-independent verification "
                    "must fail SAFETY-INV-016"
                )

    evidence = instance.get("evidence")

    if isinstance(evidence, dict):
        freshness = evidence.get("freshness")

        if isinstance(freshness, dict):
            max_age = freshness.get(
                "max_age_seconds"
            )

            try:
                actual_age = (
                    calculate_oldest_evidence_age_seconds(
                        instance
                    )
                )
            except ValueError as exc:
                errors.append(
                    "verification datetime parse error: "
                    f"{exc}"
                )
                actual_age = None

            if (
                isinstance(max_age, int)
                and actual_age is not None
            ):
                stale = actual_age > max_age

                declared_status = freshness.get(
                    "status"
                )

                metadata = get_metadata(instance)
                freshness_check = metadata.get(
                    "freshness_check"
                )

                if isinstance(
                    freshness_check,
                    dict,
                ):
                    declared_age = (
                        freshness_check.get(
                            "oldest_evidence_age_seconds"
                        )
                    )

                    if (
                        isinstance(declared_age, int)
                        and declared_age != actual_age
                    ):
                        errors.append(
                            "metadata freshness age does "
                            "not match calculated age: "
                            f"{declared_age} != "
                            f"{actual_age}"
                        )

                if stale:
                    invariants = get_invariants(
                        instance
                    )
                    assessment = invariants.get(
                        "SAFETY-INV-017"
                    )

                    if (
                        not isinstance(
                            assessment,
                            dict,
                        )
                        or assessment.get("result")
                        != "FAIL"
                    ):
                        errors.append(
                            "stale verification evidence "
                            "must fail SAFETY-INV-017"
                        )

                    if (
                        instance.get("result")
                        == "VERIFIED_SAFE"
                    ):
                        if expected_result != "FAIL":
                            errors.append(
                                "VERIFIED_SAFE cannot rely "
                                "on stale evidence"
                            )

                    if declared_status == "FRESH":
                        if expected_result != "FAIL":
                            errors.append(
                                "freshness declared FRESH "
                                "but calculated as STALE"
                            )

    return errors


# ---------------------------------------------------------------------------
# Recovery Receipt
# SAFETY-INV-018 .. 020
# ---------------------------------------------------------------------------


def validate_recovery_receipt(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors = validate_v02_common(
        instance,
        expected_result,
        {
            "SAFETY-INV-018",
            "SAFETY-INV-019",
            "SAFETY-INV-020",
        },
    )

    invariants = get_invariants(instance)

    source_state = instance.get("source_state")

    if not isinstance(source_state, dict):
        assessment = invariants.get(
            "SAFETY-INV-018"
        )

        if (
            not isinstance(assessment, dict)
            or assessment.get("result") != "FAIL"
        ):
            errors.append(
                "missing recovery source_state "
                "must fail SAFETY-INV-018"
            )
    else:
        source_reference = source_state.get(
            "source_reference"
        )

        if not isinstance(
            source_reference,
            str,
        ) or not source_reference.strip():
            assessment = invariants.get(
                "SAFETY-INV-018"
            )

            if (
                not isinstance(
                    assessment,
                    dict,
                )
                or assessment.get("result")
                != "FAIL"
            ):
                errors.append(
                    "missing recovery source_reference "
                    "must fail SAFETY-INV-018"
                )

    authority_outcome = instance.get(
        "authority_outcome"
    )

    if isinstance(authority_outcome, dict):
        old_restored = authority_outcome.get(
            "previous_authority_restored"
        )

        if old_restored is True:
            assessment = invariants.get(
                "SAFETY-INV-019"
            )

            if (
                not isinstance(assessment, dict)
                or assessment.get("result") != "FAIL"
            ):
                errors.append(
                    "automatic restoration of previous "
                    "authority must fail "
                    "SAFETY-INV-019"
                )

        final_state = instance.get(
            "final_state"
        )

        if final_state == "REAUTHORIZED":
            new_required = authority_outcome.get(
                "new_authority_required"
            )
            new_reference = (
                authority_outcome.get(
                    "new_authority_reference"
                )
            )

            if (
                old_restored is True
                or new_required is not True
                or not isinstance(
                    new_reference,
                    str,
                )
                or not new_reference.strip()
            ):
                assessment = invariants.get(
                    "SAFETY-INV-019"
                )

                if (
                    not isinstance(
                        assessment,
                        dict,
                    )
                    or assessment.get("result")
                    != "FAIL"
                ):
                    errors.append(
                        "REAUTHORIZED recovery requires "
                        "fresh authority and must not "
                        "restore previous authority"
                    )

    final_state = instance.get("final_state")

    if not isinstance(
        final_state,
        str,
    ) or not final_state.strip():
        assessment = invariants.get(
            "SAFETY-INV-020"
        )

        if (
            not isinstance(assessment, dict)
            or assessment.get("result") != "FAIL"
        ):
            errors.append(
                "missing recovery final_state must "
                "fail SAFETY-INV-020"
            )

    verification = instance.get(
        "verification"
    )

    if (
        instance.get("final_state")
        == "REAUTHORIZED"
        and isinstance(verification, dict)
    ):
        if (
            verification.get(
                "verification_result"
            )
            != "VERIFIED_SAFE"
            or verification.get(
                "independent"
            )
            is not True
        ):
            errors.append(
                "REAUTHORIZED recovery requires "
                "independent VERIFIED_SAFE result"
            )

    return errors


# ---------------------------------------------------------------------------
# v0.2 schema routing
# ---------------------------------------------------------------------------


def detect_v02_schema_name(
    instance: dict[str, Any],
    path: Path,
) -> str | None:
    name = path.name.lower()

    if "authority-envelope" in name:
        return "authority-envelope"

    if "containment-receipt" in name:
        return "containment-receipt"

    if (
        "verification-record" in name
        or name.startswith("verification-")
    ):
        return "verification-record"

    if (
        "recovery-receipt" in name
        or name.startswith("recovery-")
    ):
        return "recovery-receipt"

    if "authority_envelope_id" in instance:
        return "authority-envelope"

    if "containment_receipt_id" in instance:
        return "containment-receipt"

    if "verification_id" in instance:
        return "verification-record"

    if "recovery_receipt_id" in instance:
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


# ---------------------------------------------------------------------------
# Validation runners
# ---------------------------------------------------------------------------


def validate_v01_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected_result = (
        get_expected_result_from_path(path)
    )
    errors: list[str] = []

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="v0.1-safety-assessment",
            valid=False,
            errors=[
                f"JSON load error: {exc}"
            ],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="v0.1-safety-assessment",
            valid=False,
            errors=[
                "top-level JSON value must be an object"
            ],
        )

    errors.extend(
        schema_errors(
            instance,
            validator,
        )
    )

    errors.extend(
        validate_v01_semantics(
            instance,
            expected_result,
        )
    )

    return ValidationResult(
        path=path,
        expected_result=expected_result,
        schema_name="v0.1-safety-assessment",
        valid=not errors,
        errors=errors,
    )


def validate_v02_file(
    path: Path,
    validators: dict[
        str,
        Draft202012Validator,
    ],
) -> ValidationResult:
    expected_result = (
        get_expected_result_from_path(path)
    )
    errors: list[str] = []

    try:
        instance = load_json(path)
    except Exception as exc:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                f"JSON load error: {exc}"
            ],
        )

    if not isinstance(instance, dict):
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                "top-level JSON value must be an object"
            ],
        )

    schema_name = detect_v02_schema_name(
        instance,
        path,
    )

    if schema_name is None:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                "unable to determine v0.2 schema type"
            ],
        )

    validator = validators[schema_name]

    schema_validation_errors = (
        schema_errors(
            instance,
            validator,
        )
    )

    #
    # Important:
    # FAIL examples are allowed to intentionally violate
    # their JSON Schema when the targeted invariant is
    # expressed structurally by that schema.
    #
    # PASS examples must always be schema-valid.
    #
    if expected_result == "PASS":
        errors.extend(
            schema_validation_errors
        )

    semantic_validator = (
        V02_SEMANTIC_VALIDATORS[
            schema_name
        ]
    )

    semantic_errors = semantic_validator(
        instance,
        expected_result,
    )

    errors.extend(semantic_errors)

    if expected_result == "FAIL":
        invariants = get_invariants(instance)

        failing_invariants = {
            invariant_id
            for invariant_id, assessment
            in invariants.items()
            if (
                isinstance(assessment, dict)
                and assessment.get("result")
                == "FAIL"
            )
        }

        relevant_failures = (
            failing_invariants
            & V02_INVARIANTS
        )

        if not relevant_failures:
            errors.append(
                "v0.2 FAIL example must explicitly "
                "mark at least one SAFETY-INV-011..020 "
                "as FAIL"
            )

        #
        # A FAIL fixture is acceptable when either:
        #
        # 1. JSON Schema rejects it, or
        # 2. semantic validation identifies the unsafe
        #    condition through its invariant assessment.
        #
        # This allows both:
        #
        # - structurally invalid negative fixtures
        # - schema-valid but semantically unsafe fixtures
        #
        if (
            not schema_validation_errors
            and not relevant_failures
        ):
            errors.append(
                "FAIL example is neither schema-invalid "
                "nor semantically marked as unsafe"
            )

    return ValidationResult(
        path=path,
        expected_result=expected_result,
        schema_name=schema_name,
        valid=not errors,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def print_result(result: ValidationResult) -> None:
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


def main() -> int:
    print(
        "=== Resilient AI Safety Principles Validation ==="
    )
    print()

    try:
        _, v01_validator = (
            validate_schema_document(
                V01_SCHEMA_PATH
            )
        )

        v02_validators: dict[
            str,
            Draft202012Validator,
        ] = {}

        for (
            schema_name,
            schema_path,
        ) in V02_SCHEMA_PATHS.items():
            _, validator = (
                validate_schema_document(
                    schema_path
                )
            )
            v02_validators[
                schema_name
            ] = validator

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

    if not v01_files and not v02_files:
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
        != "v0.1-safety-assessment"
    ]

    v01_pass_count = sum(
        1
        for result in v01_results
        if result.expected_result == "PASS"
    )

    v01_fail_count = sum(
        1
        for result in v01_results
        if result.expected_result == "FAIL"
    )

    v02_pass_count = sum(
        1
        for result in v02_results
        if result.expected_result == "PASS"
    )

    v02_fail_count = sum(
        1
        for result in v02_results
        if result.expected_result == "FAIL"
    )

    print("=== Summary ===")
    print()
    print(
        f"v0.1 PASS examples : {v01_pass_count}"
    )
    print(
        f"v0.1 FAIL examples : {v01_fail_count}"
    )
    print(
        f"v0.2 PASS examples : {v02_pass_count}"
    )
    print(
        f"v0.2 FAIL examples : {v02_fail_count}"
    )
    print(
        f"Validated          : "
        f"{len(results)}/{len(results)}"
    )
    print(
        f"Invalid            : "
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
