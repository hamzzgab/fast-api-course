from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def get_hash(password: str):
    return password_hash.hash(password)


def verify(plain_password, hash_password):
    return password_hash.verify(plain_password, hash_password)
