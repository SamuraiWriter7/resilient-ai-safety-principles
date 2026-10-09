#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = ROOT / "schemas" / "safety-assessment.schema.json"
PASS_DIR = ROOT / "examples" / "pass"
FAIL_DIR = ROOT / "examples" / "fail"

VALID_INVARIANTS = {
    f"SAFETY-INV-{index:03d}"
    for index in range(1, 11)
}

VALID_INVARIANT_RESULTS = {
    "PASS",
    "FAIL",
    "NOT_APPLICABLE",
}


class ValidationFailure(Exception):
    """Raised when an example fails semantic validation."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValidationFailure(
            f"Invalid JSON: {exc.msg} "
            f"(line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise ValidationFailure(f"Unable to read file: {exc}") from exc

    if not isinstance(data, dict):
        raise ValidationFailure(
            "Top-level JSON value must be an object."
        )

    return data


def load_schema() -> dict[str, Any]:
    if not SCHEMA_PATH.is_file():
        raise ValidationFailure(
            f"Schema not found: {SCHEMA_PATH.relative_to(ROOT)}"
        )

    schema = load_json(SCHEMA_PATH)

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ValidationFailure(
            f"Schema itself is invalid: {exc.message}"
        ) from exc

    return schema


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def format_json_path(parts: list[Any]) -> str:
    if not parts:
        return "$"

    result = "$"

    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"

    return result


def validate_schema(
    example: dict[str, Any],
    validator: Draft202012Validator,
) -> list[str]:
    errors: list[str] = []

    validation_errors = sorted(
        validator.iter_errors(example),
        key=lambda error: list(error.absolute_path),
    )

    for error in validation_errors:
        json_path = format_json_path(
            list(error.absolute_path)
        )
        errors.append(
            f"{json_path}: {error.message}"
        )

    return errors


def validate_directory_expectation(
    example: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    actual_expected = example.get("expected_result")

    if actual_expected != expected_result:
        errors.append(
            "expected_result mismatch: "
            f"directory requires {expected_result!r}, "
            f"found {actual_expected!r}"
        )

    conformance = example.get("conformance")

    if not isinstance(conformance, dict):
        errors.append(
            "conformance must be an object."
        )
        return errors

    actual_conformance = conformance.get("result")

    if actual_conformance != expected_result:
        errors.append(
            "conformance.result mismatch: "
            f"directory requires {expected_result!r}, "
            f"found {actual_conformance!r}"
        )

    if expected_result == "FAIL":
        primary_failure = conformance.get("primary_failure")

        if primary_failure not in VALID_INVARIANTS:
            errors.append(
                "FAIL example must define "
                "conformance.primary_failure as a valid "
                "SAFETY-INV-001..010 identifier."
            )

    return errors


def validate_invariants(
    example: dict[str, Any],
    expected_result: str,
) -> list[str]:
    errors: list[str] = []

    invariants = example.get("invariants")

    if not isinstance(invariants, dict):
        return [
            "invariants must be an object."
        ]

    found = set(invariants.keys())

    missing = sorted(
        VALID_INVARIANTS - found
    )

    extra = sorted(
        found - VALID_INVARIANTS
    )

    if missing:
        errors.append(
            "Missing invariant assessments: "
            + ", ".join(missing)
        )

    if extra:
        errors.append(
            "Unknown invariant assessments: "
            + ", ".join(extra)
        )

    fail_count = 0

    for invariant_id in sorted(
        VALID_INVARIANTS
    ):
        assessment = invariants.get(invariant_id)

        if assessment is None:
            continue

        if not isinstance(assessment, dict):
            errors.append(
                f"{invariant_id} must be an object."
            )
            continue

        result = assessment.get("result")
        reason = assessment.get("reason")

        if result not in VALID_INVARIANT_RESULTS:
            errors.append(
                f"{invariant_id}.result must be one of "
                f"{sorted(VALID_INVARIANT_RESULTS)}, "
                f"found {result!r}"
            )

        if result == "FAIL":
            fail_count += 1

        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"{invariant_id}.reason must be "
                "a non-empty string."
            )

    if expected_result == "PASS" and fail_count:
        errors.append(
            "PASS example contains one or more "
            "invariant FAIL results."
        )

    if expected_result == "FAIL" and fail_count == 0:
        errors.append(
            "FAIL example must contain at least one "
            "invariant with result FAIL."
        )

    return errors


def validate_primary_failure(
    example: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if example.get("expected_result") != "FAIL":
        return errors

    conformance = example.get(
        "conformance",
        {},
    )

    invariants = example.get(
        "invariants",
        {},
    )

    if not isinstance(conformance, dict):
        return errors

    if not isinstance(invariants, dict):
        return errors

    primary_failure = conformance.get(
        "primary_failure"
    )

    if primary_failure not in VALID_INVARIANTS:
        return errors

    assessment = invariants.get(
        primary_failure
    )

    if not isinstance(assessment, dict):
        errors.append(
            f"primary_failure {primary_failure} "
            "does not have an invariant assessment."
        )
        return errors

    if assessment.get("result") != "FAIL":
        errors.append(
            f"conformance.primary_failure "
            f"{primary_failure} must itself have "
            "invariant result FAIL."
        )

    return errors


def validate_violation_references(
    example: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    violations = example.get("violations")

    if violations is None:
        return errors

    if not isinstance(violations, list):
        return [
            "violations must be an array."
        ]

    for index, violation in enumerate(
        violations
    ):
        if not isinstance(violation, dict):
            errors.append(
                f"violations[{index}] must be an object."
            )
            continue

        invariant = violation.get(
            "invariant"
        )

        if invariant not in VALID_INVARIANTS:
            errors.append(
                f"violations[{index}].invariant "
                f"is invalid: {invariant!r}"
            )
            continue

        assessments = example.get(
            "invariants",
            {},
        )

        if (
            isinstance(assessments, dict)
            and isinstance(
                assessments.get(invariant),
                dict,
            )
            and assessments[invariant].get(
                "result"
            )
            != "FAIL"
        ):
            errors.append(
                f"violations[{index}] references "
                f"{invariant}, but that invariant "
                "is not marked FAIL."
            )

    return errors


def validate_trace_consistency(
    example: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    trace = example.get("trace")

    if trace is None:
        return errors

    if not isinstance(trace, dict):
        return [
            "trace must be an object."
        ]

    complete = trace.get(
        "causal_chain_complete"
    )

    missing_links = trace.get(
        "missing_links"
    )

    if complete is True:
        if (
            isinstance(missing_links, list)
            and missing_links
        ):
            errors.append(
                "trace.causal_chain_complete is true "
                "but trace.missing_links is not empty."
            )

    if complete is False:
        if (
            isinstance(missing_links, list)
            and not missing_links
        ):
            errors.append(
                "trace.causal_chain_complete is false "
                "but trace.missing_links is empty."
            )

    return errors


def validate_example(
    path: Path,
    expected_result: str,
    validator: Draft202012Validator,
) -> tuple[bool, list[str]]:
    try:
        example = load_json(path)
    except ValidationFailure as exc:
        return False, [str(exc)]

    errors: list[str] = []

    errors.extend(
        validate_schema(
            example,
            validator,
        )
    )

    errors.extend(
        validate_directory_expectation(
            example,
            expected_result,
        )
    )

    errors.extend(
        validate_invariants(
            example,
            expected_result,
        )
    )

    errors.extend(
        validate_primary_failure(
            example
        )
    )

    errors.extend(
        validate_violation_references(
            example
        )
    )

    errors.extend(
        validate_trace_consistency(
            example
        )
    )

    return not errors, errors


def discover_examples(
    directory: Path,
) -> list[Path]:
    if not directory.exists():
        return []

    return sorted(
        path
        for path in directory.rglob("*.json")
        if path.is_file()
    )


def print_example_result(
    path: Path,
    expected_result: str,
    valid: bool,
    errors: list[str],
) -> None:
    print(
        f"[validate] {relative(path)}"
    )
    print(
        f"  expected: {expected_result}"
    )

    if valid:
        print("  schema  : OK")
        print("  semantic: OK")
        print("  result  : PASS")
        return

    print("  result  : FAIL")

    for error in errors:
        print(f"  - {error}")


def main() -> int:
    print(
        "=== Resilient AI Safety Principles "
        "Example Validation ==="
    )
    print()

    try:
        schema = load_schema()
    except ValidationFailure as exc:
        print(
            f"[fatal] {exc}",
            file=sys.stderr,
        )
        return 2

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    pass_examples = discover_examples(
        PASS_DIR
    )

    fail_examples = discover_examples(
        FAIL_DIR
    )

    total_examples = (
        len(pass_examples)
        + len(fail_examples)
    )

    if total_examples == 0:
        print(
            "[fatal] No JSON examples found.",
            file=sys.stderr,
        )
        return 2

    total_valid = 0
    failures: list[
        tuple[Path, list[str]]
    ] = []

    for path in pass_examples:
        valid, errors = validate_example(
            path=path,
            expected_result="PASS",
            validator=validator,
        )

        print_example_result(
            path,
            "PASS",
            valid,
            errors,
        )
        print()

        if valid:
            total_valid += 1
        else:
            failures.append(
                (path, errors)
            )

    for path in fail_examples:
        valid, errors = validate_example(
            path=path,
            expected_result="FAIL",
            validator=validator,
        )

        print_example_result(
            path,
            "FAIL",
            valid,
            errors,
        )
        print()

        if valid:
            total_valid += 1
        else:
            failures.append(
                (path, errors)
            )

    print("=== Summary ===")
    print(
        f"PASS examples : {len(pass_examples)}"
    )
    print(
        f"FAIL examples : {len(fail_examples)}"
    )
    print(
        f"Validated     : "
        f"{total_valid}/{total_examples}"
    )

    if failures:
        print(
            f"Invalid       : {len(failures)}"
        )
        print()
        print(
            "Validation failed."
        )

        return 1

    print("Invalid       : 0")
    print()
    print(
        "All examples validated successfully."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
