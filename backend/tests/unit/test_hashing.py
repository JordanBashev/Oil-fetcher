"""Unit tests for hash_signatures.

The fetch use case relies on this function to detect whether a fetched dataset
is identical to a stored DatasetVersion. Two properties matter:
  - Same set of signatures -> same hash (deterministic).
  - Order-independent (the sort means the caller can pass rows in any order).
"""
from app.utils.hashing import hash_signatures


def test_hash_is_deterministic() -> None:
    signatures = ["RWTC|2024-01-01|100.5", "RBRTE|2024-01-01|102.7"]

    first_hash = hash_signatures(signatures)
    second_hash = hash_signatures(signatures)

    assert first_hash == second_hash


def test_hash_is_order_independent() -> None:
    forward_order = ["a", "b", "c"]
    reverse_order = ["c", "b", "a"]

    assert hash_signatures(forward_order) == hash_signatures(reverse_order)


def test_hash_changes_when_a_signature_changes() -> None:
    original = ["RWTC|2024-01-01|100.5"]
    revised = ["RWTC|2024-01-01|101.0"]

    assert hash_signatures(original) != hash_signatures(revised)


def test_empty_input_hashes_to_a_stable_value() -> None:
    first = hash_signatures([])
    second = hash_signatures([])

    assert first == second
    assert len(first) == 64  # SHA-256 hex digest length
