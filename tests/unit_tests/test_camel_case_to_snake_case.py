import pytest

from core.utils.camel_case_to_snake_case import camel_to_snake


def test_camel_to_snake(camel_examples):
    for example, expected_result in camel_examples.items():
        assert camel_to_snake(example) == expected_result
