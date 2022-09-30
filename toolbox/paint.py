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


"""Create the blueprint for paints
"""
blueprint = Blueprint('paint', __name__)

#########################################################################################
###################################### Views ############################################
#########################################################################################

@blueprint.route('/paint') # The '/' will lead to this function
def index():
    """The Index will display all paints
    """
    database = get_database() # Retrieve a connection to the database

    # From the database, fetch every paint from the paint table.
    # Order them by id. So, in theory, newer calculators are placed at the top.  
    paints = database.execute(
        'SELECT * FROM paint'
        ' ORDER BY id DESC'
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the calculators as a parameter. 
    return render_template('paint/index.html', paints=paints)
