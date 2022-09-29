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
blueprint = Blueprint('room', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/<int:id>/room', methods=['GET', 'POST']) # The '/' will lead to this function
def index(id):
    """The Index will display all posts, as outlined above
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch the everythinh from the posts table.
    # Order them by created in descending order. So new posts show at the top.     
    rooms = get_database().execute(
        'SELECT r.id, calculator_id, r.name'
        ' FROM room r JOIN calculator c ON r.calculator_id = c.id'
        ' WHERE c.id = ? ORDER BY r.id DESC',
        (id,)
    ).fetchall()
    # Returns a command to render the specified template, and passes it the posts as a parameter. 
    return render_template('room/index.html', rooms=rooms, calculator_id=id)

@blueprint.route('/<int:id>/room/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(id):
    """The view used to allow users to create posts.
    Users must be logged in to create a post. 
    """
    if request.method == 'POST':
        # Posts consist of a title and body
        name = request.form['name']
        
        # Stores any errors that may arise. 
        error = None

        # title must be provided
        if not name:
            error = 'A name is required.'
 
        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:
            # If there was no error, then get a connection to the database
            database = get_database()
                      
            # Insert the post into the post table within the database 
            database.execute(
                'INSERT INTO room (name, calculator_id)'
                ' VALUES (?, ?)',
                (name, id)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('room.index', id=id))

    # If it was unsucessful, then return the user back to the create page
    return render_template('room/create.html')

@blueprint.route('/<int:c_id>/room/<int:r_id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def update(c_id, r_id):
    
    room = get_room(c_id, r_id)
    
    if request.method == 'POST':
        # Retrieve a title and body for the post from the browser
        name = request.form['name']
        # Used to store errors
        error = None

        # If no title is given then that is an error
        if not name:
            return redirect(url_for('room.index', id=c_id))

        if error is not None:
            flash(error)
        else:
            
            # Retrieve a connection to the database
            database = get_database()
            
            # With that connection, update the post in the post table, with the supplied parameters
            # We update post WHERE it is equal to the supplied id. 
            database.execute(
                'INSERT INTO room (name, calculator_id)'
                ' VALUES (?, ?)',
                (name, c_id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('room.index', id=c_id))

    # If the post could not be updated, then redirect them back to the update page again
    return render_template('room/update.html', room=room, calculator_id=c_id)

@blueprint.route('/<int:c_id>/room/<int:r_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(c_id, r_id):
    # Retrieves the post by the specified id
    get_room(c_id, r_id) # If the post cannot be found, then the blueprint aborts. 
    
    # Get a connection to the database
    database = get_database()
    
    # From the post table, delete every post where the id equally the supplied id
    database.execute('DELETE FROM room WHERE id = ?', (r_id,))
    database.commit()
    
    # When a post has been deleted, redirect to the index
    return redirect(url_for('room.index', id=c_id))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_room(c_id, r_id, check_author=True):
    # Get a connection to the database
    # Then search the database to see if a post exists which:
    # Has the id of the selected post, and is owned by the user who requested to delete it
    room = get_database().execute(
        'SELECT r.id, calculator_id, r.name'
        ' FROM room r JOIN calculator c ON r.calculator_id = c.id '
        ' WHERE c.id = ? AND r.id = ?',
        (c_id, r_id)
    ).fetchone()

    # If the post does not exist:
    # Which means that a post with the specified id, which is owned by the specified user
    if room is None:
        abort(404, f"Room id: {r_id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the author, and the author of the post is not the same as the person requesing it,
    # then abort with an error
    if check_author and room['calculator_id'] != c_id:
        abort(403, "You are not the owner of this room.")

    return room