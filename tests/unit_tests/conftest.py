import pytest


@pytest.fixture
def camel_examples():
    camel_examples = {
        "TestClass": "test_class",
        "TTestClass": "t_test_class",
        "TestClass123": "test_class123",
        "DoubleTTestClass123": "double_t_test_class123",
    }
    return camel_examples
