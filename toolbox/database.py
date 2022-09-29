#########################################################################################
#################################### Imports ############################################
#########################################################################################
from werkzeug.security import generate_password_hash
import sqlite3 # Import support for an SQLite database

import click
from flask import current_app, g


#########################################################################################
#################################### functions ############################################
#########################################################################################

def get_database():
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

def close_database(e=None):
    """Checks if a connection has been created.
    Does this by checking if g.db is defined. 
    If connection exists, then close the connection.
    """
    database = g.pop('db', None)

    if database is not None:
        database.close()
        
def init_database():
    """Initalises the database which will be used by the application.
    """
    # Call the get_db() function to retrieve a database connection
    # This connection is used to read in the database as a dictionary
    database = get_database()

    # Opens a file relative to the toolbox package. 
    # This means it should work no matter where the project is deployed
    with current_app.open_resource('schema.sql') as file:
        database.executescript(file.read().decode('utf8'))
        
def init_app(app):
    """close_db and init_db_command need to be registered with the application instance.
    However, this uses a factory function, so there is no available instance.
    Instead, this function takes the application and does the registration.
    """
    app.teardown_appcontext(close_database)   # Tells Flask to call that function when cleaning up after returning response
    app.cli.add_command(init_database_command)   # Adds a new command to the command line, which can be called with the 'flask' command


@click.command('init-db')
def init_database_command():
    """Defines a command line command called init-db, which calls the init_db() function.
    If this works, then it displays a success message, as shown below.
    """
    init_database()
    
     # If there was no error, then get a connection to the database
    database = get_database()
    
    # Insert the post into the post table within the database 
    database.execute(
        'INSERT INTO user (username, password, admin)'
        ' VALUES (?, ?, ?)',
        ('admin', generate_password_hash('admin'), 1)
    )
    database.commit()
    
    click.echo('Initialized the database.')