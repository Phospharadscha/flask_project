#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from toolbox.authentication import login_required
from toolbox.database import get_database


#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the calculator. 
The blog will:
- List all posts
- allow logged in users to create posts, 
- allow the author of a post to edit or delete their post
"""
blueprint = Blueprint('calculator', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/') # The '/' will lead to this function
def index():
    """The Index will display all calculators belonging to a specific user, as outlined above
    """
    database = get_database() # Retrieve a connection to the database

    # From the database, fetch every attribute from the calculator table.
    # We only want to select the calculators which have an author_id equal to the id of the current user. 
    # Order them by id. So, in theory, newer calculators are placed at the top.  
    calculators = database.execute(
        'SELECT c.id, author_id, name'
        ' FROM calculator c JOIN user u ON c.author_id = u.id'
        ' ORDER BY c.id DESC'
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the calculators as a parameter. 
    return render_template('calculator/index.html', calculators=calculators)

@blueprint.route('/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create():
    """The view used to allow users to create posts.
    Users must be logged in to create a calculator. 
    """
    if request.method == 'POST':
        # Calculators only need to be passed a name
        name = request.form['name']
        
        # Stores any errors that may arise. 
        error = None

        # name must be provided
        if not name:
            error = 'A name is required.'
 
        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:
            
            # If there was no error, then get a connection to the database
            database = get_database()
            
            # Insert the calculator into the calculator table within the database 
            database.execute(
                'INSERT INTO calculator (name, author_id)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('calculator.index'))

    # If it was unsucessful, then return the user back to the create page
    return render_template('calculator/create.html')

@blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update(id):
    """This view is used to allow users to update their created calculators.
    It is passed the id of the calculator which the user wants to update
    """
    # Return a calculator by id
    calc = get_calculator(id)

    if request.method == 'POST':
        # Retrieve a name for the calculator from the browser
        name = request.form['name']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('calculator.index'))

        if error is not None:
            flash(error)
        else:
            
            # Retrieve a connection to the database
            database = get_database()
            
            # With that connection, update the calculator in the calculator table, with the supplied parameters
            # We update calculator WHERE its id equal to the supplied id. 
            database.execute(
                'UPDATE calculator SET name = ?'
                ' WHERE id = ?',
                (name, calc['id'])
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('calculator.index'))

    # If the calculator could not be updated, then redirect them back to the update page again
    return render_template('calculator/update.html', calc=calc)

@blueprint.route('/<int:id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(id):
    # Retrieves the calculator by the specified id
    get_calculator(id) # If the calculator cannot be found, then the blueprint aborts. 
    
    # Get a connection to the database
    database = get_database()
    
    # From the calculator table, delete every calculator where the id equals the supplied id
    database.execute('DELETE FROM calculator WHERE id = ?', (id,))
    database.commit()
    
    # When a calculator has been deleted, redirect to the index
    return redirect(url_for('calculator.index'))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_calculator(id, check_author=True):
    """To update and delete calculators we need to fetch them by id.
    Once the calculator has been found, it then needs to verify if it belongs to the user. 
    
    Is passed a calculator id, and a bool. Bool is true by default
    The bool is used so that the function can be used to get calculators without checking the owner. Should that be needed 
    """
    
    # Get a connection to the database
    # Then search the database to see if a calculator exists which:
    # Has the id of the selected calculator, and is owned by the user who requested to delete it
    calc = get_database().execute(
        'SELECT c.id, author_id, name'
        ' FROM calculator c JOIN user u ON c.author_id = u.id'
        ' WHERE c.id = ? AND u.id = ?',
        (id, g.user['id'],)
    ).fetchone()

    # If the calculator does not exist:
    # Which means that a calculator with the specified id, which is owned by the specified user
    if calc is None:
        abort(404, f"Calculator id: {id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the owner, and the owner of the calculator is not the same as the person requesing it,
    # then abort with an error
    if check_author and calc['author_id'] != g.user['id']:
        abort(403, "You are not the owner of this calculator.")

    return calc
