from string import Template

from fastapi import HTTPException, status

no_priv_except = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="not enough privileges",
)

task_not_exist_except = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="task not exist",
)

token_invalid_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid token",
)

unauth_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="invalid login or password",
)

inactive_user_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="user is inactive",
)

user_exception_templ = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="user not exist",
)

status_exception_templ = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="status '{parameter}' not exist",
)

user_id_exc_templ = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="user with id=[{parameter}] not found",
)

username_already_exist_exc_templ = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="username '{parameter}' already exist",
)

role_not_exist_exc_templ = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="role {parameter} not exist",
)


def rendering_exception_with_param(exc: HTTPException, parameter: str):
    template = Template(exc.detail)
    rendered_detail = template.substitute(parameter=parameter)
    return HTTPException(
        status_code=exc.status_code,
        detail=rendered_detail,
    )
