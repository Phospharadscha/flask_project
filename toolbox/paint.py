#########################################################################################
#################################### Imports ############################################
#########################################################################################

import functools # Higher order functions and operations on callable objects
from werkzeug.security import check_password_hash, generate_password_hash # Security related functions
from toolbox.database import get_database # Import the function to get a connection to the database
from toolbox.authentication import login_required

# A blueprint is a way to organize a group of related views, or other code.
from flask import (
    Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
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
@login_required
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

        name = request.form['name']
        price = request.form['price']
        volume = request.form['volume']
        coverage = request.form['coverage']
        
        # Stores any errors that may arise. 
        error = None

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

@blueprint.route('/<int:p_id>/paint/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update(p_id):
    """This view is used to allow users to update their created houses.
    It is passed the id of the house which the user wants to update
    """
    
    paint = get_paint(p_id)

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        volume = request.form['volume']
        coverage = request.form['coverage']
        
        # Used to store errors
        error = None

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
                
        # If no name is given then that is an error
        if not name:
            return redirect(url_for('paint.index'))

        if error is not None:
            flash(error)
        else:
            
            # If there was no error, then get a connection to the database
            database = get_database()
            
            database.execute(
                'UPDATE paint SET name, price, volume, coverage'
                ' WHERE id = ?',
                (name, price, volume, coverage, p_id)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('paint.index'))

    # If the house could not be updated, then redirect them back to the update page again
    return render_template('paint/update.html', paint=paint)

@blueprint.route('/<int:p_id>/paint/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(p_id):

    paint = get_paint(p_id)
    

    database = get_database()
    

    database.execute('DELETE FROM paint WHERE id = ?', (p_id,))
    database.commit()
    
    return redirect(url_for('paint.index'))


#########################################################################################
###################################### Functions ########################################
#########################################################################################

def get_paint(id, check_author=True):
    """To update and delete houses we need to fetch them by id.
    Once the house has been found, it then needs to verify if it belongs to the user. 
    
    Is passed a house id, and a bool. Bool is true by default
    The bool is used so that the function can be used to get houses without checking the owner. Should that be needed 
    """
    
    # Get a connection to the database
    # Then search the database to see if a house exists which:
    # Has the id of the selected house, and is owned by the user who requested to delete it
    paint = get_database().execute(
        'SELECT id FROM paint WHERE id = ?',
        (id,)
    ).fetchone()

    # If the house does not exist:
    # Which means that a house with the specified id, which is owned by the specified user
    if paint is None:
        abort(404, f"Paint id: {id} doesn't exist.") # abort will raise a special exception that returns HTTP status code
        
    return paint



