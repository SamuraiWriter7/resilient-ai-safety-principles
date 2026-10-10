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

# ---------------------------------------------------------------------------
# Schema paths
# ---------------------------------------------------------------------------

V01_SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "safety-assessment.schema.json"
)

V02_SCHEMA_PATHS = {
    "authority-envelope": (
        ROOT
        / "schemas"
        / "authority-envelope.schema.json"
    ),
    "containment-receipt": (
        ROOT
        / "schemas"
        / "containment-receipt.schema.json"
    ),
    "verification-record": (
        ROOT
        / "schemas"
        / "verification-record.schema.json"
    ),
    "recovery-receipt": (
        ROOT
        / "schemas"
        / "recovery-receipt.schema.json"
    ),
}

V03_SCHEMA_PATH = (
    ROOT
    / "schemas"
    / "safety-receipt-bundle.schema.json"
)

# ---------------------------------------------------------------------------
# Example directories
# ---------------------------------------------------------------------------

V01_PASS_DIR = ROOT / "examples" / "pass"
V01_FAIL_DIR = ROOT / "examples" / "fail"

V02_PASS_DIR = (
    ROOT
    / "examples"
    / "v0.2"
    / "pass"
)

V02_FAIL_DIR = (
    ROOT
    / "examples"
    / "v0.2"
    / "fail"
)

V03_PASS_DIR = (
    ROOT
    / "examples"
    / "v0.3"
    / "pass"
)

V03_FAIL_DIR = (
    ROOT
    / "examples"
    / "v0.3"
    / "fail"
)

# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------

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


@dataclass
class ValidationResult:
    path: Path
    expected_result: str
    schema_name: str
    valid: bool
    errors: list[str]


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def parse_datetime(
    value: str,
) -> datetime:
    parsed = datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def format_schema_path(
    error: Any,
) -> str:
    if not error.absolute_path:
        return "$"

    parts: list[str] = []

    for item in error.absolute_path:
        if isinstance(
            item,
            int,
        ):
            parts.append(
                f"[{item}]"
            )
        else:
            if parts:
                parts.append(".")

            parts.append(
                str(item)
            )

    return "$." + "".join(
        parts
    )


def validate_schema_document(
    schema_path: Path,
) -> tuple[
    dict[str, Any],
    Draft202012Validator,
]:
    schema = load_json(
        schema_path
    )

    Draft202012Validator.check_schema(
        schema
    )

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    return (
        schema,
        validator,
    )


def schema_errors(
    instance: dict[str, Any],
    validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []

    ordered = sorted(
        validator.iter_errors(
            instance
        ),
        key=lambda error: list(
            error.absolute_path
        ),
    )

    for error in ordered:
        location = (
            format_schema_path(
                error
            )
        )

        errors.append(
            f"{location}: "
            f"{error.message}"
        )

    return errors


def get_expected_result_from_path(
    path: Path,
) -> str:
    lowered = {
        part.lower()
        for part in path.parts
    }

    if "pass" in lowered:
        return "PASS"

    if "fail" in lowered:
        return "FAIL"

    raise ValueError(
        "Cannot determine expected "
        "PASS/FAIL result from path: "
        f"{path}"
    )


def discover_json_files(
    directory: Path,
) -> list[Path]:
    if not directory.exists():
        return []

    return sorted(
        path
        for path
        in directory.rglob(
            "*.json"
        )
        if path.is_file()
    )


def get_metadata(
    instance: dict[str, Any],
) -> dict[str, Any]:
    metadata = instance.get(
        "metadata"
    )

    if isinstance(
        metadata,
        dict,
    ):
        return metadata

    return {}


def get_declared_expected_result(
    instance: dict[str, Any],
) -> str | None:
    direct = instance.get(
        "expected_result"
    )

    if isinstance(
        direct,
        str,
    ):
        return direct

    metadata = get_metadata(
        instance
    )

    nested = metadata.get(
        "expected_result"
    )

    if isinstance(
        nested,
        str,
    ):
        return nested

    return None


def get_invariants(
    instance: dict[str, Any],
) -> dict[str, Any]:
    direct = instance.get(
        "invariants"
    )

    if isinstance(
        direct,
        dict,
    ):
        return direct

    metadata = get_metadata(
        instance
    )

    nested = metadata.get(
        "invariants"
    )

    if isinstance(
        nested,
        dict,
    ):
        return nested

    return {}


def get_violations(
    instance: dict[str, Any],
) -> list[dict[str, Any]]:
    direct = instance.get(
        "violations"
    )

    if isinstance(
        direct,
        list,
    ):
        return [
            item
            for item in direct
            if isinstance(
                item,
                dict,
            )
        ]

    metadata = get_metadata(
        instance
    )

    nested = metadata.get(
        "violations"
    )

    if isinstance(
        nested,
        list,
    ):
        return [
            item
            for item in nested
            if isinstance(
                item,
                dict,
            )
        ]

    return []


def validate_expected_result(
    instance: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    declared = (
        get_declared_expected_result(
            instance
        )
    )

    if (
        declared is not None
        and declared
        != expected_result
    ):
        errors.append(
            "expected result mismatch: "
            f"path expects "
            f"{expected_result}, "
            f"document declares "
            f"{declared}"
        )

    return errors


def validate_invariant_subset(
    instance: dict[str, Any],
    relevant_invariants: set[str],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    invariants = get_invariants(
        instance
    )

    if not invariants:
        errors.append(
            "invariant assessments "
            "are missing"
        )
        return errors

    present = set(
        invariants.keys()
    )

    relevant_present = (
        present
        & relevant_invariants
    )

    for invariant_id in sorted(
        relevant_present
    ):
        assessment = invariants[
            invariant_id
        ]

        if not isinstance(
            assessment,
            dict,
        ):
            errors.append(
                f"{invariant_id}: "
                "assessment must be "
                "an object"
            )
            continue

        result = assessment.get(
            "result"
        )

        reason = assessment.get(
            "reason"
        )

        if result not in {
            "PASS",
            "FAIL",
            "NOT_APPLICABLE",
        }:
            errors.append(
                f"{invariant_id}: "
                f"invalid result "
                f"{result!r}"
            )

        if (
            not isinstance(
                reason,
                str,
            )
            or not reason.strip()
        ):
            errors.append(
                f"{invariant_id}: "
                "non-empty reason "
                "is required"
            )

    failing = {
        invariant_id
        for invariant_id
        in relevant_present
        if (
            isinstance(
                invariants[
                    invariant_id
                ],
                dict,
            )
            and invariants[
                invariant_id
            ].get("result")
            == "FAIL"
        )
    }

    if (
        expected_result == "PASS"
        and failing
    ):
        errors.append(
            "PASS example contains "
            "failing invariants: "
            + ", ".join(
                sorted(failing)
            )
        )

    if (
        expected_result == "FAIL"
        and not failing
    ):
        errors.append(
            "FAIL example does not "
            "contain a failing "
            "relevant invariant"
        )

    for violation in get_violations(
        instance
    ):
        invariant_id = (
            violation.get(
                "invariant"
            )
        )

        if (
            invariant_id
            not in relevant_invariants
        ):
            continue

        assessment = invariants.get(
            invariant_id
        )

        if not isinstance(
            assessment,
            dict,
        ):
            errors.append(
                "violation references "
                "invariant without "
                "assessment: "
                f"{invariant_id}"
            )
            continue

        if (
            assessment.get(
                "result"
            )
            != "FAIL"
        ):
            errors.append(
                "violation references "
                "invariant not marked "
                "FAIL: "
                f"{invariant_id}"
            )

    return errors


def require_exact_invariants(
    instance: dict[str, Any],
    expected_invariants: set[str],
) -> list[str]:
    errors: list[str] = []

    invariants = get_invariants(
        instance
    )

    present = set(
        invariants.keys()
    )

    missing = sorted(
        expected_invariants
        - present
    )

    extra = sorted(
        present
        - expected_invariants
    )

    if missing:
        errors.append(
            "missing invariants: "
            + ", ".join(
                missing
            )
        )

    if extra:
        errors.append(
            "unexpected invariants: "
            + ", ".join(
                extra
            )
        )

    return errors


def invariant_is_fail(
    instance: dict[str, Any],
    invariant_id: str,
) -> bool:
    invariants = get_invariants(
        instance
    )

    assessment = invariants.get(
        invariant_id
    )

    return (
        isinstance(
            assessment,
            dict,
        )
        and assessment.get(
            "result"
        )
        == "FAIL"
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
        f"{message}; "
        f"{invariant_id} "
        "must be FAIL"
    ]


# ---------------------------------------------------------------------------
# v0.1 validation
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

    conformance = instance.get(
        "conformance"
    )

    if isinstance(
        conformance,
        dict,
    ):
        result = conformance.get(
            "result"
        )

        if (
            result
            != expected_result
        ):
            errors.append(
                "conformance.result "
                "mismatch: expected "
                f"{expected_result}, "
                f"got {result!r}"
            )

        primary_failure = (
            conformance.get(
                "primary_failure"
            )
        )

        if (
            expected_result
            == "FAIL"
        ):
            if not isinstance(
                primary_failure,
                str,
            ):
                errors.append(
                    "FAIL example "
                    "requires "
                    "conformance."
                    "primary_failure"
                )

            elif (
                primary_failure
                not in V01_INVARIANTS
            ):
                errors.append(
                    "invalid "
                    "primary_failure: "
                    f"{primary_failure}"
                )

            elif not invariant_is_fail(
                instance,
                primary_failure,
            ):
                errors.append(
                    "primary_failure "
                    "invariant must "
                    "itself be marked "
                    "FAIL"
                )

    trace = instance.get(
        "trace"
    )

    if isinstance(
        trace,
        dict,
    ):
        causal_complete = (
            trace.get(
                "causal_chain_complete"
            )
        )

        missing_links = (
            trace.get(
                "missing_links"
            )
        )

        if isinstance(
            missing_links,
            list,
        ):
            if (
                causal_complete is True
                and missing_links
            ):
                errors.append(
                    "trace."
                    "causal_chain_complete"
                    "=true but "
                    "missing_links is "
                    "non-empty"
                )

            if (
                causal_complete
                is False
                and not missing_links
            ):
                errors.append(
                    "trace."
                    "causal_chain_complete"
                    "=false but "
                    "missing_links is "
                    "empty"
                )

    return errors


# ---------------------------------------------------------------------------
# v0.2 common validation
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
# v0.2 Authority Envelope
# SAFETY-INV-011 .. 013
# ---------------------------------------------------------------------------


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

    metadata = get_metadata(
        instance
    )

    mutation = metadata.get(
        "mutation"
    )

    if isinstance(
        mutation,
        dict,
    ):
        self_modified = (
            mutation.get(
                "subject_self_modified"
            )
        )

        reissued = (
            mutation.get(
                "independent_authority_"
                "reissue_present"
            )
        )

        if (
            self_modified is True
            and reissued is not True
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-012",
                    "authority "
                    "self-expansion "
                    "detected without "
                    "independent "
                    "re-issuance",
                )
            )

    validity = instance.get(
        "validity"
    )

    status = instance.get(
        "status"
    )

    validation_context = (
        metadata.get(
            "validation_context"
        )
    )

    if (
        isinstance(
            validity,
            dict,
        )
        and isinstance(
            validation_context,
            dict,
        )
    ):
        valid_until = (
            validity.get(
                "valid_until"
            )
        )

        evaluated_at = (
            validation_context.get(
                "evaluated_at"
            )
        )

        if (
            isinstance(
                valid_until,
                str,
            )
            and isinstance(
                evaluated_at,
                str,
            )
        ):
            try:
                expiry = parse_datetime(
                    valid_until
                )

                evaluation_time = (
                    parse_datetime(
                        evaluated_at
                    )
                )

                expired = (
                    evaluation_time
                    >= expiry
                )

                if (
                    expired
                    and status
                    == "ACTIVE"
                ):
                    errors.extend(
                        require_failure(
                            instance,
                            "SAFETY-INV-013",
                            "expired "
                            "ACTIVE authority",
                        )
                    )

            except ValueError as exc:
                errors.append(
                    "authority datetime "
                    "parse error: "
                    f"{exc}"
                )

    return errors


# ---------------------------------------------------------------------------
# v0.2 Containment Receipt
# SAFETY-INV-014 .. 015
# ---------------------------------------------------------------------------


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

    metadata = get_metadata(
        instance
    )

    recording_status = (
        metadata.get(
            "recording_status"
        )
    )

    if isinstance(
        recording_status,
        dict,
    ):
        transition_occurred = (
            recording_status.get(
                "transition_occurred"
            )
        )

        created_at_transition = (
            recording_status.get(
                "receipt_created_at_"
                "transition_time"
            )
        )

        if (
            transition_occurred
            is True
            and created_at_transition
            is False
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-014",
                    "containment "
                    "transition was not "
                    "recorded "
                    "contemporaneously",
                )
            )

    evidence = instance.get(
        "evidence_preservation"
    )

    if isinstance(
        evidence,
        dict,
    ):
        required_flags = [
            "state_preserved",
            "trace_preserved",
            "trigger_evidence_preserved",
        ]

        evidence_ok = all(
            evidence.get(flag)
            is True
            for flag
            in required_flags
        )

        if not evidence_ok:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-015",
                    "containment "
                    "evidence "
                    "preservation "
                    "is incomplete",
                )
            )

    return errors


# ---------------------------------------------------------------------------
# v0.2 Verification Record
# SAFETY-INV-016 .. 017
# ---------------------------------------------------------------------------


def calculate_oldest_evidence_age_seconds(
    instance: dict[str, Any],
) -> int | None:
    verified_at = instance.get(
        "verified_at"
    )

    if not isinstance(
        verified_at,
        str,
    ):
        return None

    evidence = instance.get(
        "evidence"
    )

    if not isinstance(
        evidence,
        dict,
    ):
        return None

    items = evidence.get(
        "items"
    )

    if (
        not isinstance(
            items,
            list,
        )
        or not items
    ):
        return None

    verification_time = (
        parse_datetime(
            verified_at
        )
    )

    observed_times: list[
        datetime
    ] = []

    for item in items:
        if not isinstance(
            item,
            dict,
        ):
            continue

        observed_at = item.get(
            "observed_at"
        )

        if not isinstance(
            observed_at,
            str,
        ):
            continue

        observed_times.append(
            parse_datetime(
                observed_at
            )
        )

    if not observed_times:
        return None

    oldest = min(
        observed_times
    )

    age = (
        verification_time
        - oldest
    ).total_seconds()

    return max(
        0,
        int(age),
    )


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

    verifier = instance.get(
        "verifier"
    )

    if isinstance(
        verifier,
        dict,
    ):
        independent = (
            verifier.get(
                "independent_from_subject"
            )
            is True
            and verifier.get(
                "independent_from_executor"
            )
            is True
        )

        if not independent:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-016",
                    "verifier is not "
                    "independent",
                )
            )

    evidence = instance.get(
        "evidence"
    )

    if isinstance(
        evidence,
        dict,
    ):
        freshness = evidence.get(
            "freshness"
        )

        if isinstance(
            freshness,
            dict,
        ):
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
                    "verification "
                    "datetime parse "
                    "error: "
                    f"{exc}"
                )
                actual_age = None

            if (
                isinstance(
                    max_age,
                    int,
                )
                and actual_age
                is not None
                and actual_age
                > max_age
            ):
                errors.extend(
                    require_failure(
                        instance,
                        "SAFETY-INV-017",
                        "verification "
                        "uses stale "
                        "evidence",
                    )
                )

                if (
                    instance.get(
                        "result"
                    )
                    == "VERIFIED_SAFE"
                    and expected_result
                    == "PASS"
                ):
                    errors.append(
                        "VERIFIED_SAFE "
                        "cannot rely on "
                        "stale evidence"
                    )

    return errors


# ---------------------------------------------------------------------------
# v0.2 Recovery Receipt
# SAFETY-INV-018 .. 020
# ---------------------------------------------------------------------------


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

    source_state = instance.get(
        "source_state"
    )

    if not isinstance(
        source_state,
        dict,
    ):
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-018",
                "recovery "
                "source_state is "
                "missing",
            )
        )

    else:
        source_reference = (
            source_state.get(
                "source_reference"
            )
        )

        if (
            not isinstance(
                source_reference,
                str,
            )
            or not source_reference.strip()
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-018",
                    "recovery "
                    "source_reference "
                    "is missing",
                )
            )

    authority_outcome = (
        instance.get(
            "authority_outcome"
        )
    )

    if isinstance(
        authority_outcome,
        dict,
    ):
        old_restored = (
            authority_outcome.get(
                "previous_authority_"
                "restored"
            )
        )

        if old_restored is True:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-019",
                    "previous "
                    "authority was "
                    "automatically "
                    "restored",
                )
            )

        if (
            instance.get(
                "final_state"
            )
            == "REAUTHORIZED"
        ):
            new_required = (
                authority_outcome.get(
                    "new_authority_required"
                )
            )

            new_reference = (
                authority_outcome.get(
                    "new_authority_reference"
                )
            )

            if (
                old_restored is True
                or new_required
                is not True
                or not isinstance(
                    new_reference,
                    str,
                )
                or not new_reference.strip()
            ):
                errors.extend(
                    require_failure(
                        instance,
                        "SAFETY-INV-019",
                        "REAUTHORIZED "
                        "recovery does "
                        "not use fresh "
                        "authority",
                    )
                )

    final_state = instance.get(
        "final_state"
    )

    if (
        not isinstance(
            final_state,
            str,
        )
        or not final_state.strip()
    ):
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-020",
                "recovery "
                "final_state is "
                "missing",
            )
        )

    verification = instance.get(
        "verification"
    )

    if (
        final_state
        == "REAUTHORIZED"
        and isinstance(
            verification,
            dict,
        )
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
                "REAUTHORIZED "
                "recovery requires "
                "independent "
                "VERIFIED_SAFE "
                "verification"
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

    if (
        "authority-envelope"
        in name
        or "authority_envelope_id"
        in instance
    ):
        return "authority-envelope"

    if (
        "containment-receipt"
        in name
        or "containment_receipt_id"
        in instance
    ):
        return "containment-receipt"

    if (
        "verification-record"
        in name
        or name.startswith(
            "verification-"
        )
        or "verification_id"
        in instance
    ):
        return "verification-record"

    if (
        "recovery-receipt"
        in name
        or name.startswith(
            "recovery-"
        )
        or "recovery_receipt_id"
        in instance
    ):
        return "recovery-receipt"

    return None


V02_SEMANTIC_VALIDATORS: dict[
    str,
    Callable[
        [dict[str, Any], str],
        list[str],
    ],
] = {
    "authority-envelope":
        validate_authority_envelope,
    "containment-receipt":
        validate_containment_receipt,
    "verification-record":
        validate_verification_record,
    "recovery-receipt":
        validate_recovery_receipt,
}


# ---------------------------------------------------------------------------
# v0.3 helpers
# ---------------------------------------------------------------------------


def get_receipts(
    instance: dict[str, Any],
) -> dict[str, Any]:
    receipts = instance.get(
        "receipts"
    )

    if isinstance(
        receipts,
        dict,
    ):
        return receipts

    return {}


def get_receipt(
    instance: dict[str, Any],
    receipt_name: str,
) -> dict[str, Any] | None:
    receipts = get_receipts(
        instance
    )

    value = receipts.get(
        receipt_name
    )

    if isinstance(
        value,
        dict,
    ):
        return value

    return None


def get_chain_links(
    instance: dict[str, Any],
) -> list[dict[str, Any]]:
    chain = instance.get(
        "chain"
    )

    if not isinstance(
        chain,
        dict,
    ):
        return []

    links = chain.get(
        "links"
    )

    if not isinstance(
        links,
        list,
    ):
        return []

    return [
        link
        for link in links
        if isinstance(
            link,
            dict,
        )
    ]


def has_chain_link(
    instance: dict[str, Any],
    source: str,
    target: str,
    relation: str | None = None,
) -> bool:
    for link in get_chain_links(
        instance
    ):
        if (
            link.get("from")
            != source
            or link.get("to")
            != target
        ):
            continue

        if (
            relation is None
            or link.get(
                "relation"
            )
            == relation
        ):
            return True

    return False


def current_operation_id(
    instance: dict[str, Any],
) -> str | None:
    operation = instance.get(
        "operation"
    )

    if not isinstance(
        operation,
        dict,
    ):
        return None

    operation_id = operation.get(
        "operation_id"
    )

    if isinstance(
        operation_id,
        str,
    ):
        return operation_id

    return None


def successor_operation_id(
    instance: dict[str, Any],
) -> str | None:
    operation = instance.get(
        "operation"
    )

    if not isinstance(
        operation,
        dict,
    ):
        return None

    value = operation.get(
        "successor_operation_id"
    )

    if isinstance(
        value,
        str,
    ):
        return value

    return None


def receipt_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(
        receipt,
        dict,
    ):
        return None

    value = receipt.get(
        "receipt_id"
    )

    if isinstance(
        value,
        str,
    ):
        return value

    return None


def receipt_operation_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(
        receipt,
        dict,
    ):
        return None

    value = receipt.get(
        "operation_id"
    )

    if isinstance(
        value,
        str,
    ):
        return value

    return None


def receipt_subject_id(
    receipt: dict[str, Any] | None,
) -> str | None:
    if not isinstance(
        receipt,
        dict,
    ):
        return None

    value = receipt.get(
        "subject_id"
    )

    if isinstance(
        value,
        str,
    ):
        return value

    return None


def required_v03_receipt_ids(
    instance: dict[str, Any],
) -> set[str]:
    ids: set[str] = set()

    receipts = get_receipts(
        instance
    )

    for value in receipts.values():
        if not isinstance(
            value,
            dict,
        ):
            continue

        value_id = value.get(
            "receipt_id"
        )

        if isinstance(
            value_id,
            str,
        ):
            ids.add(
                value_id
            )

    return ids


# ---------------------------------------------------------------------------
# v0.3 semantic validation
# SAFETY-INV-021 .. 030
# ---------------------------------------------------------------------------


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

    operation_id = (
        current_operation_id(
            instance
        )
    )

    successor_id = (
        successor_operation_id(
            instance
        )
    )

    bundle_subject = (
        instance.get(
            "subject"
        )
    )

    bundle_subject_id = None

    if isinstance(
        bundle_subject,
        dict,
    ):
        value = bundle_subject.get(
            "subject_id"
        )

        if isinstance(
            value,
            str,
        ):
            bundle_subject_id = value

    authority = get_receipt(
        instance,
        "authority",
    )

    containment = get_receipt(
        instance,
        "containment",
    )

    verification = get_receipt(
        instance,
        "verification",
    )

    recovery = get_receipt(
        instance,
        "recovery",
    )

    successor_authority = (
        get_receipt(
            instance,
            "successor_authority",
        )
    )

    authority_id = receipt_id(
        authority
    )

    containment_id = receipt_id(
        containment
    )

    verification_id = receipt_id(
        verification
    )

    recovery_id = receipt_id(
        recovery
    )

    successor_authority_id = (
        receipt_id(
            successor_authority
        )
    )

    # -------------------------------------------------------------------
    # SAFETY-INV-021 — Receipt Identity Consistency
    # -------------------------------------------------------------------

    identity_mismatch = False

    primary_receipts = [
        authority,
        containment,
        verification,
        recovery,
    ]

    for receipt in primary_receipts:
        if receipt is None:
            continue

        receipt_op = (
            receipt_operation_id(
                receipt
            )
        )

        if (
            receipt_op is not None
            and operation_id
            is not None
            and receipt_op
            != operation_id
        ):
            identity_mismatch = True

    if (
        successor_authority
        is not None
    ):
        successor_receipt_op = (
            receipt_operation_id(
                successor_authority
            )
        )

        if (
            successor_id
            is not None
            and successor_receipt_op
            is not None
            and successor_receipt_op
            != successor_id
        ):
            identity_mismatch = True

    if identity_mismatch:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-021",
                "receipt identity "
                "consistency failed",
            )
        )

    # -------------------------------------------------------------------
    # SAFETY-INV-022 — Subject Continuity
    # -------------------------------------------------------------------

    subject_discontinuity = False

    expected_subject = (
        bundle_subject_id
        or operation_id
    )

    for receipt in [
        containment,
        verification,
        recovery,
    ]:
        if receipt is None:
            continue

        subject_id = (
            receipt_subject_id(
                receipt
            )
        )

        if (
            expected_subject
            is not None
            and subject_id
            is not None
            and subject_id
            != expected_subject
        ):
            subject_discontinuity = True

    if subject_discontinuity:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-022",
                "subject continuity "
                "is broken",
            )
        )

    # -------------------------------------------------------------------
    # SAFETY-INV-023 — Authority-to-Action Binding
    # -------------------------------------------------------------------

    authority_bound = False

    if (
        authority_id
        and operation_id
    ):
        if (
            receipt_operation_id(
                authority
            )
            == operation_id
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
        ):
            authority_bound = True

    if not authority_bound:
        errors.extend(
            require_failure(
                instance,
                "SAFETY-INV-023",
                "authority is not "
                "explicitly bound "
                "to operation",
            )
        )

    # -------------------------------------------------------------------
    # SAFETY-INV-024 — Containment Causal Link
    # -------------------------------------------------------------------

    if containment is not None:
        containment_causal = False

        if (
            containment_id
            and operation_id
        ):
            containment_causal = (
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

        if not containment_causal:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-024",
                    "containment has "
                    "no causal link",
                )
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-025 — Verification Must Reference Containment
    # -------------------------------------------------------------------

    if (
        containment is not None
        and verification
        is not None
    ):
        verification_matches = False

        if (
            containment_id
            and verification_id
        ):
            verification_matches = (
                has_chain_link(
                    instance,
                    containment_id,
                    verification_id,
                    "VERIFIES",
                )
            )

        if not verification_matches:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-025",
                    "verification does "
                    "not reference "
                    "applicable "
                    "containment",
                )
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-026 — Recovery Must Reference Verification
    # -------------------------------------------------------------------

    if (
        verification is not None
        and recovery is not None
    ):
        recovery_matches = False

        if (
            verification_id
            and recovery_id
        ):
            recovery_matches = (
                has_chain_link(
                    instance,
                    verification_id,
                    recovery_id,
                    "JUSTIFIES_RECOVERY",
                )
            )

        if not recovery_matches:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-026",
                    "recovery does not "
                    "reference "
                    "applicable "
                    "verification",
                )
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-027 — No Broken Safety Chain
    # -------------------------------------------------------------------

    chain = instance.get(
        "chain"
    )

    if isinstance(
        chain,
        dict,
    ):
        complete = chain.get(
            "complete"
        )

        missing_links = (
            chain.get(
                "missing_links"
            )
        )

        if (
            complete is True
            and isinstance(
                missing_links,
                list,
            )
            and missing_links
        ):
            errors.append(
                "chain.complete=true "
                "but missing_links "
                "is non-empty"
            )

        broken = (
            complete is False
            or (
                isinstance(
                    missing_links,
                    list,
                )
                and bool(
                    missing_links
                )
            )
        )

        if broken:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-027",
                    "safety chain is "
                    "incomplete",
                )
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-028 — No Conflicting Final States
    # -------------------------------------------------------------------

    if isinstance(
        chain,
        dict,
    ):
        conflicting = (
            chain.get(
                "conflicting_final_states"
            )
        )

        final_states = (
            chain.get(
                "declared_final_states"
            )
        )

        if (
            conflicting is True
            or (
                isinstance(
                    final_states,
                    list,
                )
                and len(
                    set(
                        final_states
                    )
                )
                > 1
            )
        ):
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-028",
                    "conflicting final "
                    "states detected",
                )
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-029 — No Receipt Replay
    # -------------------------------------------------------------------

    if isinstance(
        chain,
        dict,
    ):
        replay_detected = (
            chain.get(
                "replay_detected"
            )
        )

        replayed_receipts = (
            chain.get(
                "replayed_receipt_ids"
            )
        )

        replay = (
            replay_detected is True
            or (
                isinstance(
                    replayed_receipts,
                    list,
                )
                and bool(
                    replayed_receipts
                )
            )
        )

        if replay:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-029",
                    "receipt replay "
                    "detected",
                )
            )

        if (
            replay_detected is False
            and isinstance(
                replayed_receipts,
                list,
            )
            and replayed_receipts
        ):
            errors.append(
                "chain."
                "replay_detected=false "
                "but "
                "replayed_receipt_ids "
                "is non-empty"
            )

    # -------------------------------------------------------------------
    # SAFETY-INV-030 — Bundle Trace Continuity
    # -------------------------------------------------------------------

    trace = instance.get(
        "trace"
    )

    if isinstance(
        trace,
        dict,
    ):
        all_reachable = (
            trace.get(
                "all_receipts_reachable"
            )
        )

        continuity = (
            trace.get(
                "trace_continuity"
            )
        )

        reachable = trace.get(
            "reachable_receipt_ids"
        )

        missing = trace.get(
            "missing_receipt_ids"
        )

        required_ids = (
            required_v03_receipt_ids(
                instance
            )
        )

        reachable_ids = (
            set(reachable)
            if isinstance(
                reachable,
                list,
            )
            else set()
        )

        missing_ids = (
            set(missing)
            if isinstance(
                missing,
                list,
            )
            else set()
        )

        calculated_missing = (
            required_ids
            - reachable_ids
        )

        trace_broken = (
            all_reachable
            is not True
            or continuity
            != "COMPLETE"
            or bool(
                calculated_missing
            )
            or bool(
                missing_ids
            )
        )

        if trace_broken:
            errors.extend(
                require_failure(
                    instance,
                    "SAFETY-INV-030",
                    "bundle trace "
                    "continuity is "
                    "incomplete",
                )
            )

        if (
            all_reachable is True
            and calculated_missing
        ):
            errors.append(
                "trace claims all "
                "receipts reachable "
                "but these receipt "
                "IDs are absent: "
                + ", ".join(
                    sorted(
                        calculated_missing
                    )
                )
            )

        if (
            missing_ids
            != calculated_missing
            and (
                missing_ids
                or calculated_missing
            )
        ):
            errors.append(
                "trace."
                "missing_receipt_ids "
                "does not match "
                "calculated missing "
                "receipts"
            )

    # -------------------------------------------------------------------
    # Bundle status consistency
    # -------------------------------------------------------------------

    bundle_status = (
        instance.get(
            "bundle_status"
        )
    )

    if (
        expected_result == "PASS"
        and bundle_status
        == "INVALID"
    ):
        errors.append(
            "PASS bundle cannot "
            "have bundle_status "
            "INVALID"
        )

    if (
        expected_result == "FAIL"
        and bundle_status
        not in {
            "INVALID",
            "INCOMPLETE",
        }
    ):
        errors.append(
            "FAIL bundle should "
            "normally be INVALID "
            "or INCOMPLETE"
        )

    if bundle_status == "CLOSED":
        if (
            isinstance(
                chain,
                dict,
            )
            and chain.get(
                "complete"
            )
            is not True
        ):
            errors.append(
                "CLOSED bundle "
                "requires complete "
                "chain"
            )

        if isinstance(
            trace,
            dict,
        ):
            if (
                trace.get(
                    "all_receipts_reachable"
                )
                is not True
            ):
                errors.append(
                    "CLOSED bundle "
                    "requires all "
                    "receipts reachable"
                )

            if (
                trace.get(
                    "trace_continuity"
                )
                != "COMPLETE"
            ):
                errors.append(
                    "CLOSED bundle "
                    "requires COMPLETE "
                    "trace continuity"
                )

    return errors


# ---------------------------------------------------------------------------
# File validation runners
# ---------------------------------------------------------------------------


def validate_v01_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected_result = (
        get_expected_result_from_path(
            path
        )
    )

    try:
        instance = load_json(
            path
        )

    except Exception as exc:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name=(
                "v0.1-safety-assessment"
            ),
            valid=False,
            errors=[
                f"JSON load error: "
                f"{exc}"
            ],
        )

    if not isinstance(
        instance,
        dict,
    ):
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name=(
                "v0.1-safety-assessment"
            ),
            valid=False,
            errors=[
                "top-level JSON "
                "value must be "
                "an object"
            ],
        )

    errors = schema_errors(
        instance,
        validator,
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
        schema_name=(
            "v0.1-safety-assessment"
        ),
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
        get_expected_result_from_path(
            path
        )
    )

    try:
        instance = load_json(
            path
        )

    except Exception as exc:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                f"JSON load error: "
                f"{exc}"
            ],
        )

    if not isinstance(
        instance,
        dict,
    ):
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                "top-level JSON "
                "value must be "
                "an object"
            ],
        )

    schema_name = (
        detect_v02_schema_name(
            instance,
            path,
        )
    )

    if schema_name is None:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name="unknown",
            valid=False,
            errors=[
                "unable to "
                "determine v0.2 "
                "schema type"
            ],
        )

    validator = validators[
        schema_name
    ]

    raw_schema_errors = (
        schema_errors(
            instance,
            validator,
        )
    )

    errors: list[str] = []

    # PASS examples must always satisfy JSON Schema.
    # FAIL examples may intentionally violate Schema.
    if expected_result == "PASS":
        errors.extend(
            raw_schema_errors
        )

    semantic_validator = (
        V02_SEMANTIC_VALIDATORS[
            schema_name
        ]
    )

    errors.extend(
        semantic_validator(
            instance,
            expected_result,
        )
    )

    if expected_result == "FAIL":
        failing = {
            invariant_id
            for invariant_id,
            assessment
            in get_invariants(
                instance
            ).items()
            if (
                invariant_id
                in V02_INVARIANTS
                and isinstance(
                    assessment,
                    dict,
                )
                and assessment.get(
                    "result"
                )
                == "FAIL"
            )
        }

        if not failing:
            errors.append(
                "v0.2 FAIL "
                "example must "
                "mark at least "
                "one invariant "
                "SAFETY-INV-011"
                "..020 as FAIL"
            )

    return ValidationResult(
        path=path,
        expected_result=expected_result,
        schema_name=schema_name,
        valid=not errors,
        errors=errors,
    )


def validate_v03_file(
    path: Path,
    validator: Draft202012Validator,
) -> ValidationResult:
    expected_result = (
        get_expected_result_from_path(
            path
        )
    )

    try:
        instance = load_json(
            path
        )

    except Exception as exc:
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name=(
                "safety-receipt-bundle"
            ),
            valid=False,
            errors=[
                f"JSON load error: "
                f"{exc}"
            ],
        )

    if not isinstance(
        instance,
        dict,
    ):
        return ValidationResult(
            path=path,
            expected_result=expected_result,
            schema_name=(
                "safety-receipt-bundle"
            ),
            valid=False,
            errors=[
                "top-level JSON "
                "value must be "
                "an object"
            ],
        )

    raw_schema_errors = (
        schema_errors(
            instance,
            validator,
        )
    )

    errors: list[str] = []

    # Same negative-fixture policy as v0.2:
    # PASS must be schema-valid.
    # FAIL may intentionally violate structural constraints.
    if expected_result == "PASS":
        errors.extend(
            raw_schema_errors
        )

    errors.extend(
        validate_v03_semantics(
            instance,
            expected_result,
        )
    )

    if expected_result == "FAIL":
        failing = {
            invariant_id
            for invariant_id,
            assessment
            in get_invariants(
                instance
            ).items()
            if (
                invariant_id
                in V03_INVARIANTS
                and isinstance(
                    assessment,
                    dict,
                )
                and assessment.get(
                    "result"
                )
                == "FAIL"
            )
        }

        if not failing:
            errors.append(
                "v0.3 FAIL "
                "example must "
                "mark at least "
                "one invariant "
                "SAFETY-INV-021"
                "..030 as FAIL"
            )

    return ValidationResult(
        path=path,
        expected_result=expected_result,
        schema_name=(
            "safety-receipt-bundle"
        ),
        valid=not errors,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def relative_path(
    path: Path,
) -> str:
    try:
        return str(
            path.relative_to(
                ROOT
            )
        )

    except ValueError:
        return str(
            path
        )


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
        f"expected="
        f"{result.expected_result})"
    )

    for error in result.errors:
        print(
            f"  - {error}"
        )


def count_results(
    results: list[ValidationResult],
    schema_name: str,
    expected_result: str,
) -> int:
    return sum(
        1
        for result in results
        if (
            result.schema_name
            == schema_name
            and result.expected_result
            == expected_result
        )
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print(
        "=== Resilient AI Safety "
        "Principles Validation ==="
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

        _, v03_validator = (
            validate_schema_document(
                V03_SCHEMA_PATH
            )
        )

    except FileNotFoundError as exc:
        print(
            "[fatal] required "
            f"schema missing: {exc}"
        )
        return 2

    except json.JSONDecodeError as exc:
        print(
            "[fatal] invalid "
            f"schema JSON: {exc}"
        )
        return 2

    except Exception as exc:
        print(
            "[fatal] schema "
            f"setup failed: {exc}"
        )
        return 2

    v01_files = (
        discover_json_files(
            V01_PASS_DIR
        )
        + discover_json_files(
            V01_FAIL_DIR
        )
    )

    v02_files = (
        discover_json_files(
            V02_PASS_DIR
        )
        + discover_json_files(
            V02_FAIL_DIR
        )
    )

    v03_files = (
        discover_json_files(
            V03_PASS_DIR
        )
        + discover_json_files(
            V03_FAIL_DIR
        )
    )

    if (
        not v01_files
        and not v02_files
        and not v03_files
    ):
        print(
            "[fatal] no example "
            "JSON files found"
        )
        return 2

    results: list[
        ValidationResult
    ] = []

    # -------------------------------------------------------------------
    # v0.1
    # -------------------------------------------------------------------

    if v01_files:
        print("## v0.1")
        print()

        for path in v01_files:
            result = (
                validate_v01_file(
                    path,
                    v01_validator,
                )
            )

            results.append(
                result
            )

            print_result(
                result
            )

        print()

    # -------------------------------------------------------------------
    # v0.2
    # -------------------------------------------------------------------

    if v02_files:
        print("## v0.2")
        print()

        for path in v02_files:
            result = (
                validate_v02_file(
                    path,
                    v02_validators,
                )
            )

            results.append(
                result
            )

            print_result(
                result
            )

        print()

    # -------------------------------------------------------------------
    # v0.3
    # -------------------------------------------------------------------

    if v03_files:
        print("## v0.3")
        print()

        for path in v03_files:
            result = (
                validate_v03_file(
                    path,
                    v03_validator,
                )
            )

            results.append(
                result
            )

            print_result(
                result
            )

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

    def expected_count(
        subset: list[
            ValidationResult
        ],
        expected: str,
    ) -> int:
        return sum(
            1
            for result in subset
            if result.expected_result
            == expected
        )

    print(
        "=== Summary ==="
    )
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
        "Validated          : "
        f"{len(results)}/"
        f"{len(results)}"
    )

    print(
        "Invalid            : "
        f"{len(invalid_results)}"
    )

    if invalid_results:
        print()
        print(
            "Validation reports "
            "are incomplete or "
            "an expectation failed."
        )
        return 1

    print()
    print(
        "All examples validated "
        "successfully."
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
