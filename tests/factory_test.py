#########################################################################################
#################################### Imports ############################################
#########################################################################################

from toolbox import create_app

#########################################################################################
#################################### Functions ##########################################
#########################################################################################
"""
    The factory function would be tested by other tests, so not much is done here. 
    So, this should either pass the test config, or run a default test (the top function)

"""

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


# Checks for the response data 'Hello, World!'
def test_hello(client):
    response = client.get('/hello')
    assert response.data == b'Hello, World!'