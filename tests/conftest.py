import pytest
from core.config import settings


@pytest.fixture(scope="session")
def jwt_config():
    jwt_config = {
        "private_key": settings.api.auth_jwt.private_key_path.read_text(),
        "public_key": settings.api.auth_jwt.public_key_path.read_text(),
        "algorithm": settings.api.auth_jwt.algorithm,
        "expire_minutes": 15,
    }
    return jwt_config
