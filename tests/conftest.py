import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pytest
from glide_test_api import create_app



@pytest.fixture
def app():

    app = create_app({
        'TESTING': True,
        'EMPLOYEES_ENDPOINT': 'https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp/employees'
    })

    yield app



@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()