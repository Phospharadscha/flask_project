import functools # Higher order functions and operations on callable objects

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

"""Creates a Flask blueprint named 'auth'. 
This will be used for authentication of users. 

It needs to know where it is defined, so it is passed the __name__.
url_prefix is put at the start of all urls associated with authentication
"""
bp = Blueprint('auth', __name__, url_prefix='/auth')