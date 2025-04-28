from string import Template

from fastapi import HTTPException, status

no_priv_except = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough privileges",
)

task_not_exist_except = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Task not exist",
)

token_invalid_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid token",
)

unauth_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid login or password",
)

inactive_user_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is inactive",
)

user_exception_templ = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not exist",
)

status_exception_templ = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Status '$parameter' not exist",
)

user_id_exc_templ = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User with id=[$parameter] not found",
)

username_already_exist_exc_templ = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Username '$parameter' already exist",
)

role_not_exist_exc_templ = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Role '$parameter' not exist",
)


def rendering_exception_with_param(exc: HTTPException, parameter: str):
    template = Template(exc.detail)
    rendered_detail = template.substitute(parameter=parameter)
    return HTTPException(
        status_code=exc.status_code,
        detail=rendered_detail,
    )
