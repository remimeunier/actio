import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture(scope="module")
def request_factory():
    return APIRequestFactory()
