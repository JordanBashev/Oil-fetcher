import hashlib

SIGNATURE_SEPARATOR = "\n"


def hash_signatures(signatures: list[str]) -> str:
    """Produce a deterministic SHA256 hash from a list of string signatures.

    Signatures are sorted first so the same set of items always yields the
    same hash regardless of their original order.
    """
    ordered_signatures = sorted(signatures)
    joined = SIGNATURE_SEPARATOR.join(ordered_signatures)
    return hashlib.sha256(joined.encode()).hexdigest()
