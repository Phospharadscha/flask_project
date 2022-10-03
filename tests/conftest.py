#########################################################################################
#################################### Imports ############################################
#########################################################################################

import os
import tempfile

import pytest
from toolbox import create_app
from toolbox.database import get_database, init_database

#########################################################################################
#################################### Classes ############################################
#########################################################################################

class AuthenticationActions(object):
    """
        This class will createa post request to login with client details. 
        Can be used in tests relating to authentication.
    """

    # Create a client object
    def __init__(self, client):
        self._client = client
        
    # Call the login html page and supply it with the username and password we want to use for testing
    def login(self, username='test', password='test'):
        return self._client.post(
            '/authentication/login',
            data={'username': username, 'password': password}
        )
    
    # Log the user out. 
    def logout(self):
        return self._client.get('/auth/logout')

#########################################################################################
############################# Test Functions ############################################
#########################################################################################
"""Fixtures match function namse with the names of arguments in the test functions.
"""


with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')
@pytest.fixture
def app():
    # Create and open a temporary file. It returns the descriptor, and path to the file
    db_fd, db_path = tempfile.mkstemp() 
    # Tell Flask app is in test mode. 
    # Changes internal behaviour to make it easier to test
    # We also ovveride the path to the database, so it uses the temp path created above. 
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    # Initialize the database and run the data.sql script to popualate it with some users
    with app.app_context():
        init_database()
        get_database().executescript(_data_sql)
    yield app
    # Close the database 
    os.close(db_fd)
    os.unlink(db_path)
    

@pytest.fixture
def client(app):
    """calls app.test_client() with the object created by the fixture above.
    This is used to make requests without running the server
    """
    
    return app.test_client()
@pytest.fixture
def runner(app):
    """Creates a runner that can call the click commands we register in the app
    """
    
    return app.test_cli_runner()

@pytest.fixture
def authentication(client):
    """
        Create an object for the authentication tests and run them. 
    """
    return AuthenticationActions(client)
