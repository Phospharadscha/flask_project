#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, get_template_attribute, redirect, render_template, request, url_for
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
blueprint = Blueprint('wall', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/<int:r_id>/room/wall', methods=['GET', 'POST']) # The '/' will lead to this function
def index(r_id):
    """The Index will display all posts, as outlined above
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch the everythinh from the posts table.
    # Order them by created in descending order. So new posts show at the top.     
    walls = get_database().execute(
        'SELECT w.id, room_id, w.name'
        ' FROM wall w JOIN room r ON w.room_id = r.id'
        ' WHERE r.id = ? ORDER BY w.id DESC',
        (r_id,)
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the posts as a parameter. 
    return render_template('wall/index.html', walls=walls, room_id=r_id)

@blueprint.route('/<int:r_id>/room/wall/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(r_id):
    """The view used to allow users to create posts.
    Users must be logged in to create a post. 
    """
    paints = get_paint()
    shapes = ["Square"]
    
    if request.method == 'POST':
        # Posts consist of a title and body
        name = request.form['name']
        paint = request.opt
        shape = request.form['shape']
        
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
            return redirect(url_for('wall.index', r_id=r_id))

    # If it was unsucessful, then return the user back to the create page
    return render_template('wall/create.html', paints=paints, shape=shapes)

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_paint(): 
    database = get_database()
                      
    # Insert the post into the post table within the database 
    paints = database.execute(
        'SELECT * FROM paint'
    ).fetchall()
    
    return paints
