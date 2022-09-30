#########################################################################################
#################################### Imports ############################################
#########################################################################################

import functools # Higher order functions and operations on callable objects
from werkzeug.security import check_password_hash, generate_password_hash # Security related functions
from toolbox.database import get_database # Import the function to get a connection to the database
from toolbox.authentication import login_required

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

@blueprint.route('/paint/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create():
    """The view used to allow admins to enter paint into the database. 
    """
    if request.method == 'POST':
        # Calculators only need to be passed a name
        name = request.form['name']
        price = request.form['price']
        volume = request.form['volume']
        coverage = request.form['coverage']
        
        # Stores any errors that may arise. 
        error = None

        # name must be provided
        if not name:
            error = 'A name is required.'

        if not price:
            error = 'A price is required.'
        else:
            try:
                price = float(price)
            except:
                error = 'Price MUST be a number'

        if not volume:
            error = 'A volume is required.'
        else:
            try:
                volume = float(volume)
            except:
                error = 'Volume MUST be a number'

        if not coverage:
            error = 'A coverage is required.'
        else:
            try:
                coverage = float(coverage)
            except:
                error = 'Coverage MUST be a number'
 
        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:
            
            # If there was no error, then get a connection to the database
            database = get_database()
            
            # Insert the calculator into the calculator table within the database 
            database.execute(
                'INSERT INTO paint (name, price, volume, coverage)'
                ' VALUES (?, ?, ?, ?)',
                (name, price, volume, coverage)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('paint.index'))

    # If it was unsucessful, then return the user back to the create page
    return render_template('paint/create.html')
