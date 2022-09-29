import sqlite3 # Import support for an SQLite database

import click
from flask import current_app, g


def get_db():
    """g is a special object unique to each request. it is used to store data-
    - that might be accessed by multiple functions during a request. 
    The connection is stored and reused, rather than creation of a new connection.
    
    current_app points to the flask application handling the request. 
    This implementation uses an application factory, so there is no application object. 
    """
    if 'db' not in g:  
        g.db = sqlite3.connect(   # Establishes a connection to the file pointed at by the DATABASE configuration key
            current_app.config['DATABASE'],   
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # tells the established connection to return rows that behave like dictionaries
        # With this, columsn can be accessed by name:
        g.db.row_factory = sqlite3.Row

    # Return the database retrieved by the connection 
    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()