#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from . import room

from toolbox.authentication import login_required
from toolbox.database import get_database


#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the house. 
The blog will:
- List all posts
- allow logged in users to create posts, 
- allow the author of a post to edit or delete their post
"""
blueprint = Blueprint('house', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/') # The '/' will lead to this function
@login_required
def index():
    """The Index will display all houses belonging to a specific user, as outlined above
    """
    database = get_database() # Retrieve a connection to the database

    # From the database, fetch every attribute from the house table.
    # We only want to select the houses which have an author_id equal to the id of the current user. 
    # Order them by id. So, in theory, newer houses are placed at the top.  
    houses = database.execute(
        'SELECT h.id, author_id, name'
        ' FROM house h JOIN user u ON h.author_id = u.id'
        ' ORDER BY h.id DESC'
    ).fetchall()
    

    return render_template('house/index.html', houses=houses)

@blueprint.route('/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create():
    """The view used to allow users to create posts.
    Users must be logged in to create a house. 
    """
    if request.method == 'POST':
        # houses only need to be passed a name
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
            
            # Insert the house into the house table within the database 
            database.execute(
                'INSERT INTO house (name, author_id)'
                ' VALUES (?, ?)',
                (name, g.user['id'])
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('house.index'))

    # If it was unsucessful, then return the user back to the create page
    return render_template('house/create.html')

@blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update(id):
    """This view is used to allow users to update their created houses.
    It is passed the id of the house which the user wants to update
    """
    # Return a house by id
    house = get_house(id)

    if request.method == 'POST':
        # Retrieve a name for the house from the browser
        name = request.form['name']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('house.index'))

        if error is not None:
            flash(error)
        else:
            
            # Retrieve a connection to the database
            database = get_database()
            
            # With that connection, update the house in the house table, with the supplied parameters
            # We update house WHERE its id equal to the supplied id. 
            database.execute(
                'UPDATE house SET name = ?'
                ' WHERE id = ?',
                (name, house['id'])
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('house.index'))

    # If the house could not be updated, then redirect them back to the update page again
    return render_template('house/update.html', house=house)

@blueprint.route('/<int:id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(id):
    # Retrieves the house by the specified id
    get_house(id) # If the house cannot be found, then the blueprint aborts. 
    rooms = get_rooms(id)
    
    # Get a connection to the database
    database = get_database()
    
    # delete every wall and room that would be within the house that is to be deleted. 
    if rooms is not None:
        for room in rooms:
            database.execute('DELETE FROM wall WHERE room_id = ?', (room['id'],))
            database.commit()
            
            database.execute('DELETE FROM room WHERE id = ?', (room['id'],))
            database.commit()
    
    # From the house table, delete every house where the id equals the supplied id
    database.execute('DELETE FROM house WHERE id = ?', (id,))
    database.commit()
    
    # When a house has been deleted, redirect to the index
    return redirect(url_for('house.index'))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_values():
    houses = get_database().execute(
        'SELECT * FROM house'
    ).fetchall()
    
    for house in houses: 
        rooms = get_database().execute(
            'SELECT * FROM room WHERE house_id = ?',
            (house['id'],)
        ).fetchall()
    
        # fetch the total cost, number of buckets, and paint values per wall 
        room_values =  room.get_values(rooms)
        
        
    
    

def get_house(id, check_author=True):
    """To update and delete houses we need to fetch them by id.
    Once the house has been found, it then needs to verify if it belongs to the user. 
    
    Is passed a house id, and a bool. Bool is true by default
    The bool is used so that the function can be used to get houses without checking the owner. Should that be needed 
    """
    
    # Get a connection to the database
    # Then search the database to see if a house exists which:
    # Has the id of the selected house, and is owned by the user who requested to delete it
    calc = get_database().execute(
        'SELECT h.id, author_id, name'
        ' FROM house h JOIN user u ON h.author_id = u.id'
        ' WHERE h.id = ? AND u.id = ?',
        (id, g.user['id'],)
    ).fetchone()

    # If the house does not exist:
    # Which means that a house with the specified id, which is owned by the specified user
    if calc is None:
        abort(404, f"House id: {id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the owner, and the owner of the house is not the same as the person requesing it,
    # then abort with an error
    if check_author and calc['author_id'] != g.user['id']:
        abort(403, "You are not the owner of this house.")

    return calc

def get_rooms(id):
    database = get_database()
    
    rooms = get_database().execute(
        'SELECT * FROM room WHERE house_id = ?',
        (id,)
    ).fetchall()
    
    return rooms