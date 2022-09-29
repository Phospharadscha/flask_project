#########################################################################################
#################################### Imports ############################################
#########################################################################################

import functools # Higher order functions and operations on callable objects
from werkzeug.security import check_password_hash, generate_password_hash # Security related functions
from toolbox.database import get_database # Import the function to get a connection to the database

# A blueprint is a way to organize a group of related views, or other code.
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

#########################################################################################
################################## Blueprint ############################################
#########################################################################################


"""Creates a Flask blueprint named 'auth'. 
This will be used for authentication of users and to allow logging in and out.  

It needs to know where it is defined, so it is passed the __name__.
url_prefix is put at the start of all urls associated with authentication
"""
blueprint = Blueprint('auth', __name__, url_prefix='/auth')

#########################################################################################
###################################### Views ############################################
#########################################################################################

@blueprint.route('/register', methods=('GET', 'POST'))   # Associates the '/register/ url with the register view function
def register():
    """When the user visits '/auth/register' the view returns a HTML with form for registration.
    When a form is submitted, it will validate input and either show the form again, or create a new user.
    This does not include the HMTL template. 
    """
    
    if request.method == 'POST':   # If user submitted the form
        # request.form[] is a type of dictionary mapping. 
        username = request.form['username']
        password = request.form['password']
        
        # Retrieve the database for storing user information
        database = get_database()
        
        # Will store any error from the result of input validation
        error = None

        # Validate user input.
        # Check that they are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # If validation was successful, insert their data into the user table
        if error is None:
            
            # Try catch for error handling
            try:
                # takes SQL query 
                # ? are placeholders for user input, tuple is what to replace the placeholders with
                # The database library will automatically protect from SQL injection 
                database.execute( 
                    "INSERT INTO user (username, password, admin) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), 0), # Password is hashed for security
                )
                database.commit() # Commit changes to the database
            except database.IntegrityError: # If username is already in use
                error = f"User {username} is already registered."
            else: # If no exception, then redirect to login page
                # url_for automatially generates the url for login based on name
                # redirect then redirects the user to that url
                return redirect(url_for("auth.login"))

        # Flash stores messages that can be retrieved when rendering the template
        flash(error)

    # renders a template containing the HTML
    return render_template('authentication/register.html')

@blueprint.route('/login', methods=('GET', 'POST'))
def login():
    """When the user visits '/auth/login' the view returns a HTML with a form for logging in.
    When a form is submitted, it will validate input and either show the form again, or log the user in.
    This does not include the HMTL template. 
    """
    
    if request.method == 'POST': # If user submitted form   
        # request.form[] is a type of dictionary mapping. 
        username = request.form['username']
        password = request.form['password']
        
        # Retrieve the database for storing user information
        database = get_database()
        
        # Will store any error from the result of input validation
        error = None
        
        # Retrieve user information
        # SELECT [ALL] FROM the user table WHERE the username field = the provided username
        user = database.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        
        if user is None: # A matching user could not be found
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password): # Password is hashed and checks if it matches what is stored
            error = 'Incorrect password.' # The user could be found, but the password is incorrect
        
        # Login was successful 
        if error is None:
            # session is a dictionary that stores data across requests
            # When validation succeeds the user id is stored in a new session. 
            # Data is stored in a cookie that is sent to the browser, before being sent back with subsequent request
            session.clear()
            session['user_id'] = user['id']
            
            # url_for automatially generates a url for based on name
            # redirect then redirects the user to that url
            # If the user is logged in, then their information should be loaded and made available to other views
            return redirect(url_for('index'))

        # Flash stores messages that can be retrieved when rendering the template
        flash(error)

    return render_template('authentication/login.html')

@blueprint.route('/logout')
def logout():
    """A view for logging the user out.
    To log out, the session is cleared. This remvoes the user id from the cookies. 
    Once logged out, load_logged_in_user won't load a user on later requests
    """
    session.clear()
    return redirect(url_for('index'))

# Registers a function that runs before the view function, regardless of requested url
@blueprint.before_app_request
def load_logged_in_user():
    # user_id is stored as a cookie for the session
    user_id = session.get('user_id')

    if user_id is None: # If user is not logged in, then set g.user to none
        g.user = None
    else: # if user has been logged in, then retrieve their user information from the database
        g.user = get_database().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
#########################################################################################
###################################### Decorator ########################################
#########################################################################################

def login_required(view):
    """Creating, updating, or deleting a blog post requires the user to be logged in. 
    This, when applied to a view, can check if the user is logged in.
    This is a decorator, which wraps around a provided view function.
    """
    
    # Returns a new view function which wraps the original one it is applied to. 
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        """Checks if a user is loaded. 
        If they are not, then they are redirected to the login screen.
        If they are loaded, then the originally requested view (page) is loaded as expected"""
        if g.user is None:
            # redirect them to the login page instead
            return redirect(url_for('authentication.login'))

        # Return the expected view
        return view(**kwargs)

    return wrapped_view
