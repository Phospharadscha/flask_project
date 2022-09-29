import functools # Higher order functions and operations on callable objects
from werkzeug.security import check_password_hash, generate_password_hash # Security related functions
from flaskr.db import get_db # Import the function to get a connection to the database

# A blueprint is a way to organize a group of related views, or other code.
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

"""Creates a Flask blueprint named 'auth'. 
This will be used for authentication of users and to allow logging in and out.  

It needs to know where it is defined, so it is passed the __name__.
url_prefix is put at the start of all urls associated with authentication
"""
bp = Blueprint('auth', __name__, url_prefix='/auth')