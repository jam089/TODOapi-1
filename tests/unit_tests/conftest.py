import pytest


@pytest.fixture(scope="session")
def camel_examples():
    camel_examples = {
        "TestClass": "test_class",
        "TTestClass": "t_test_class",
        "TestClass123": "test_class123",
        "DoubleTTestClass123": "double_t_test_class123",
    }
    return camel_examples


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


@pytest.fixture(scope="session")
def passwords():
    passwords = [
        "fg345gGdg",
        "!432%#$fG",
    ]
    return passwords
