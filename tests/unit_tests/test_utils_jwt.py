from datetime import datetime, UTC, timedelta

import pytest

from core.utils.jwt import encode_jwt, decode_jwt
from core.utils.jwt import hash_password, check_password


def test_encode_decode_jwt(jwt_payload_example, jwt_config):
    payload = jwt_payload_example.copy()
    exp_min = jwt_config.get("expire_minutes")
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=exp_min)
    jwt = encode_jwt(
        payload=payload,
        private_key=jwt_config.get("private_key"),
        algorithm=jwt_config.get("algorithm"),
        expire_minutes=exp_min,
    )
    payload.update(
        iat=int(datetime.timestamp(now)),
        exp=int(datetime.timestamp(expire)),
    )
    decoded_payload = decode_jwt(
        token=jwt,
        public_key=jwt_config.get("public_key"),
        algorithm=jwt_config.get("algorithm"),
    )
    assert decoded_payload == payload


@pytest.mark.parametrize(
    "password",
    [
        "fg345gGdg",
        "!432%#$fG",
    ],
)
def test_hash_n_check_passwords(password):
    hash_pass = hash_password(password)
    assert hash_pass != password
    assert check_password(password, hash_pass)
