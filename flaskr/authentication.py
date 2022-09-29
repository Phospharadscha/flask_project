#########################################################################################
#################################### Imports ############################################
#########################################################################################

import functools # Higher order functions and operations on callable objects
from werkzeug.security import check_password_hash, generate_password_hash # Security related functions
from flaskr.database import get_database # Import the function to get a connection to the database

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
    """When the user visits '/auth/register' the register returns a HTML with form for registration.
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
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
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
    return render_template('auth/register.html')