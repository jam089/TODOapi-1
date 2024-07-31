import pytest


@pytest.fixture(scope="session")
def jwt_payload_example():
    payload = {
        "type": "access",
        "iss": "john@malkovich.com",
        "sub": 7,
        "username": "john",
        "jti": "15937a7e-2a4f-41aa-9267-ee2ec264069b",
        "name": "John Malkovich",
        "logged_in_at": 1722351564.249006,
        "role": "User",
    }
    return payload
