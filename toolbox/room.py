#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from toolbox import database

from . import wall

from toolbox.authentication import login_required
from toolbox.database import get_database

#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the house. 
The room will:
- List all rooms
- allow logged in users to create new rooms, 
- allow the creator of a room to edit or delete it
"""
blueprint = Blueprint('room', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/<int:h_id>/room', methods=['GET', 'POST']) 
def index(h_id):
    """The Index will display all rooms owned by the user, as outlined above.
    This function is passed a house id from its url. 
    This id is used to authenticate that rooms belong to the user. 
    We use the house id, as that is a field in the room table. Furthermore, a user cannot enter a house that isn't theres. 
    So, we have already verified the user. 
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch the rooms from the room table
    # We want to select rooms where their house_id  value is equal to the passed house id
    # They are ordered by the room id. This should mean they are ordered by creation. 
    rooms = get_database().execute(
        'SELECT r.id, house_id, r.name'
        ' FROM room r JOIN house h ON r.house_id = h.id'
        ' WHERE h.id = ? ORDER BY r.id DESC',
        (h_id,)
    ).fetchall()
    
    # Select the house which these rooms belong too. 
    # We only want the name of house. This will be used to render the name of the house. 
    house = get_database().execute(
        'SELECT h.name'
        ' FROM house h JOIN room r ON r.house_id = h.id'
        ' WHERE h.id = ?',
        (h_id,)
    ).fetchone()
    
    # Returns a dictionary ordered by the room id
    # each room stores values on the total cost, paints required, and number of walls
    room_values = get_values(rooms)
    
    # Returns a command to render the specified template, and passes it the rooms as a parameter, the house id, and the name of the house. 
    return render_template('room/index.html', rooms=rooms, house_id=h_id, h_name=house, room_values=room_values)

@blueprint.route('/<int:h_id>/room/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(h_id):
    """The view used to allow users to create rooms.
    Users must be logged in to create a room.
    The function is passed the id of the house it belongs too via the url. 
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
            # the name and id of the house are passed in 
            database.execute(
                'INSERT INTO room (name, house_id)'
                ' VALUES (?, ?)',
                (name, h_id)
            )
            database.commit()
            
            # Redirect the user back to the index page for room
            return redirect(url_for('room.index', h_id=h_id))

    # If it was unsucessful, then return the user back to the create page
    return render_template('room/create.html')

@blueprint.route('/<int:h_id>/room/<int:r_id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def update(h_id, r_id):
    """To update a room we need the id of the house it belongs too, and the id of the room we want to update. 
    Both of these parameters are passed to the function through its url. 
    """
    
    # Get the room from the get_room() function. 
    room = get_room(h_id, r_id)
    
    
    if request.method == 'POST':
        # Retrieve a new name for 
        name = request.form['name']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('room.index', h_id=h_id))

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
            return redirect(url_for('room.index', h_id=h_id))

    # If the room could not be updated, then redirect them back to the update page again
    return render_template('room/update.html', room=room, house_id=h_id)

@blueprint.route('/<int:h_id>/room/<int:r_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(h_id, r_id):
    
    # Retrieves the room by the specified id
    get_room(h_id, r_id) # If the room cannot be found, then the blueprint aborts. 
    
    # Get a connection to the database
    database = get_database()
    
    # From the room table, delete every room where the id is equal to the supplied id
    # also delete every wall that was within that room. 
    database.execute('DELETE FROM wall WHERE room_id = ?', (r_id,))
    database.commit()
    
    database.execute('DELETE FROM room WHERE id = ?', (r_id,))
    database.commit()
    
    # Once the room has been deleted, redirect to the index
    return redirect(url_for('room.index', h_id=h_id))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_values(rooms):
    walls = get_database().execute(
        'SELECT * FROM wall'
    ).fetchall()
    
    values = wall.get_values() 
    room_values = {}
    
    for room in rooms: 
        total_cost = 0
        number_of_walls = 0
        paint_vals = {}
        
        for w in walls:      
            if w['room_id'] == room['id']:
                number_of_walls += 1
                total_cost += values[w['id']][0]

                p_id = w['paint_id']
                if p_id not in paint_vals: 
                    paint_vals[p_id] = values[w['id']][1]
                else:
                    paint_vals[p_id] += values[w['id']][1]

        r_id = room['id']
        room_values[r_id] = (total_cost, number_of_walls, paint_vals)
    

    return room_values


def get_room(h_id, r_id, check_author=True):
    # Get a connection to the database
    # Then search the database to see if a room exists which:
    # Has the id of the selected room, and has a house_id equal to the supplied c_id
    room = get_database().execute(
        'SELECT r.id, house_id, r.name'
        ' FROM room r JOIN house h ON r.house_id = h.id '
        ' WHERE h.id = ? AND r.id = ?',
        (h_id, r_id)
    ).fetchone()

    # If the room does not exist:
    # Which means that a room with the specified id, which is 'within' the specified house
    if room is None:
        abort(404, f"Room id: {r_id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the house, and the house the room is within, is not the same as the house passed to it,
    # then abort with an error
    if check_author and room['house_id'] != h_id:
        abort(403, "You are not the owner of this room.")

    return room
