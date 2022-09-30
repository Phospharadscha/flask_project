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
The room will:
- List all rooms
- allow logged in users to create new rooms, 
- allow the creator of a room to edit or delete it
"""
blueprint = Blueprint('room', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/<int:c_id>/room', methods=['GET', 'POST']) 
def index(c_id):
    """The Index will display all rooms owned by the user, as outlined above.
    This function is passed a calculator id from its url. 
    This id is used to authenticate that rooms belong to the user. 
    We use the calculator id, as that is a field in the room table. Furthermore, a user cannot enter a calculator that isn't theres. 
    So, we have already verified the user. 
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch the rooms from the room table
    # We want to select rooms where their calculator_id  value is equal to the passed calculator id
    # They are ordered by the room id. This should mean they are ordered by creation. 
    rooms = get_database().execute(
        'SELECT r.id, calculator_id, r.name'
        ' FROM room r JOIN calculator c ON r.calculator_id = c.id'
        ' WHERE c.id = ? ORDER BY r.id DESC',
        (c_id,)
    ).fetchall()
    
    # Select the calculator which these rooms belong too. 
    # We only want the name of calculator. This will be used to render the name of the calculator. 
    calculator = get_database().execute(
        'SELECT c.name'
        ' FROM calculator c JOIN room r ON r.calculator_id = c.id'
        ' WHERE c.id = ?',
        (c_id,)
    ).fetchone()
    
    # Returns a command to render the specified template, and passes it the rooms as a parameter, the calculator id, and the name of the calculator. 
    return render_template('room/index.html', rooms=rooms, calculator_id=c_id, c_name=calculator)

@blueprint.route('/<int:c_id>/room/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(c_id):
    """The view used to allow users to create rooms.
    Users must be logged in to create a room.
    The function is passed the id of the calculator it belongs too via the url. 
    """
    
    if request.method == 'POST':
        # Rooms consist of a name
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
                      
            # Insert the room into the room table within the database 
            # the name and id of the calculator are passed in 
            database.execute(
                'INSERT INTO room (name, calculator_id)'
                ' VALUES (?, ?)',
                (name, c_id)
            )
            database.commit()
            
            # Redirect the user back to the index page for room
            return redirect(url_for('room.index', c_id=c_id))

    # If it was unsucessful, then return the user back to the create page
    return render_template('room/create.html')

@blueprint.route('/<int:c_id>/room/<int:r_id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def update(c_id, r_id):
    """To update a room we need the id of the calculator it belongs too, and the id of the room we want to update. 
    Both of these parameters are passed to the function through its url. 
    """
    
    # Get the room from the get_room() function. 
    room = get_room(c_id, r_id)
    
    
    if request.method == 'POST':
        # Retrieve a new name for 
        name = request.form['name']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('room.index', c_id=c_id))

        if error is not None:
            flash(error)
        else:
            
            # Retrieve a connection to the database
            database = get_database()
            
            # With that connection, we want to updated the room table with the new room name. 
            database.execute(
                'UPDATE room SET name = ?'
                ' WHERE id = ?',
                (name, r_id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('room.index', c_id=c_id))

    # If the room could not be updated, then redirect them back to the update page again
    return render_template('room/update.html', room=room, calculator_id=c_id)

@blueprint.route('/<int:c_id>/room/<int:r_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(c_id, r_id):
    
    # Retrieves the room by the specified id
    get_room(c_id, r_id) # If the room cannot be found, then the blueprint aborts. 
    
    # Get a connection to the database
    database = get_database()
    
    # From the room table, delete every room where the id is equal to the supplied id
    database.execute('DELETE FROM room WHERE id = ?', (r_id,))
    database.commit()
    
    # Once the room has been deleted, redirect to the index
    return redirect(url_for('room.index', c_id=c_id))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_room(c_id, r_id, check_author=True):
    # Get a connection to the database
    # Then search the database to see if a room exists which:
    # Has the id of the selected room, and has a calculator_id equal to the supplied c_id
    room = get_database().execute(
        'SELECT r.id, calculator_id, r.name'
        ' FROM room r JOIN calculator c ON r.calculator_id = c.id '
        ' WHERE c.id = ? AND r.id = ?',
        (c_id, r_id)
    ).fetchone()

    # If the room does not exist:
    # Which means that a room with the specified id, which is 'within' the specified calculator
    if room is None:
        abort(404, f"Room id: {r_id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the calculator, and the calculator the room is within, is not the same as the calculator passed to it,
    # then abort with an error
    if check_author and room['calculator_id'] != c_id:
        abort(403, "You are not the owner of this room.")

    return room
