import pytest

from core.utils.camel_case_to_snake_case import camel_to_snake


@pytest.mark.parametrize(
    "example, expected",
    [
        ("TestClass", "test_class"),
        ("TTestClass", "t_test_class"),
        ("TestClass123", "test_class123"),
        ("DoubleTTestClass123", "double_t_test_class123"),
    ],
)
def test_camel_to_snake(example, expected):
    assert camel_to_snake(example) == expected
