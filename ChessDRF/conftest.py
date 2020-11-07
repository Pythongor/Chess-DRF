import pytest
import pytest_django


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


def pytest_unconfigure(config):
    pytest_django.plugin._blocking_manager.unblock()
