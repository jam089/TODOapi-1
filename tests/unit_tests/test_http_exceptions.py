import pytest
from api.http_exceptions import rendering_exception_with_param
from fastapi import HTTPException, status


def test_rendering_exception_with_valid_template():
    test_exc_with_param = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Test error with $parameter not found",
    )
    result = rendering_exception_with_param(test_exc_with_param, "bugs")
    assert result.detail == "Test error with bugs not found"
    assert result.status_code == status.HTTP_404_NOT_FOUND


def test_rendering_exception_with_no_param_template():
    test_exc_without_param = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Test error not found",
    )
    result = rendering_exception_with_param(test_exc_without_param, "bugs")
    assert result.detail == "Test error not found"
    assert result.status_code == status.HTTP_404_NOT_FOUND


def test_rendering_exception_with_invalid_template():
    test_exc_invalid = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Test error with $parameter and $wrong",
    )
    with pytest.raises(KeyError):
        rendering_exception_with_param(test_exc_invalid, "bugs")
