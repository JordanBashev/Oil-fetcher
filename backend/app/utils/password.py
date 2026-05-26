import bcrypt

BCRYPT_MAX_BYTES = 72


def _encode_password(plain_password: str) -> bytes:
    return plain_password.encode("utf-8")[:BCRYPT_MAX_BYTES]


def hash_password(plain_password: str) -> str:
    hashed_bytes = bcrypt.hashpw(_encode_password(plain_password), bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_encode_password(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        return False
