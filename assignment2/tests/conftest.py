import pytest
from aceest_fitness import create_app
from aceest_fitness.models import db


@pytest.fixture
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        "APP_VERSION": "test-version",
    })
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_member():
    return {
        "name": "Aarav Patil",
        "email": "aarav@example.com",
        "age": 28,
        "weight_kg": 78.5,
        "program": "fat-loss",
    }
