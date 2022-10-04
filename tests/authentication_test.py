#########################################################################################
#################################### Imports ############################################
#########################################################################################

import pytest
from flask import g, session
from toolbox.database import get_database


#########################################################################################
#################################### Registration Tests #################################
#########################################################################################

def test_register(client, app):
    """
        Test the registration system
        The client object is essentially just a fake user we can use to post information to HTML pages. 
    """

    # Assert that the registration html will run without issue
    # client.get returns the response object returned by Flask
    assert client.get('/authentication/register.html').status_code == 404
    
    # Record the response of calling the registration html and passing it the fake registration information
    # client.post converts the data dict into form data, which can be read by the page
    response = client.post(
        '/authentication/register.html', data={'username': 'a', 'password': 'a'}
    )
    assert response.headers["Location"] == "auth.login"


    # Asser that we will find a user in the database with the username of 'a'
    with app.app_context():
        assert get_database().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# Tell pytest to run teh same function with different arguments
# Here we test different invalid input and error messages
# It is in the order of: Usernames, passwords, and expected message returned by the app
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    
    # Post to the registration with the test values
    response = client.post(
        '/authentication/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data
    
    

#########################################################################################
################################# Login Tests ###########################################
#########################################################################################
    
def test_login(client, authentication):
    """
    Test the login system
    The client object is essentially just a fake user we can use to post information to HTML pages. 
    """
    
    # Asser that when we call the login page we'll get a status code of 200
    assert client.get('/authentication/login').status_code == 200

    # call the login function and record the response
    response = authentication.login()
    
    # We expect that the response will redirect us to the '/' url (house index)
    assert response.headers["Location"] == "/"

    # By using with we can access context variables like session after the reponse is returned to us.
    # Normally, trying to do this owuld raise an error
    with client:
        client.get('/')
        assert session['user_id'] == 2 # we expect that the user_id in session will be '2'  (accounting for the admin login, which is always 1)  
        assert g.user['username'] == 'test' # username should be test


# Tell pytest to run teh same function with different arguments
# Here we test different invalid input and error messages
# It is in the order of: Usernames, passwords, and expected message returned by the app
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(authentication, username, password, message):
    
    # Record the response we get
    response = authentication.login(username, password)
    assert message in response.data # see if that response is what we expected. 
    

#########################################################################################
################################# Logout Tests ##########################################
#########################################################################################

def test_logout(client, authentication):
    """
        Testing the logout function
    """
    
    # Log in with a user
    authentication.login()

    with client:
        authentication.logout() # Have the user log out
        assert 'user_id' not in session # Check to see if their user_id is still stored in the session