import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path):
    database_url = f"sqlite:///{tmp_path}/test.db"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "ana@example.com",
            "password": "super-secret",
            "full_name": "Ana Cocina",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

