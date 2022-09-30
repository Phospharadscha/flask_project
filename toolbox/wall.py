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

"""Blueprint for the wall. 
The wall will:
- Allow logged in users to create new walls, 
- update walls they have already created
"""
blueprint = Blueprint('wall', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/<int:r_id>/room/wall', methods=['GET', 'POST']) 
def index(r_id):
    """The Index will display all walls, as outlined above
    The function is passed the id of the room it is contained in via the url.
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch walls from the wall table.
    # We only want walls with a room_id equal to the supplied id
    walls = get_database().execute(
        'SELECT w.id, room_id, w.name'
        ' FROM wall w JOIN room r ON w.room_id = r.id'
        ' WHERE r.id = ? ORDER BY w.id DESC',
        (r_id,)
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the walls as a parameter. 
    return render_template('wall/index.html', walls=walls, room_id=r_id)

@blueprint.route('/<int:r_id>/room/wall/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(r_id):
    """The view used to allow users to create new walls.
    the function is passed the room it will be contained in via its url.  
    """
    # Fetch a dictionary of all paints in the paint table. 
    # This will be used to define a drop down menu in html. 
    paints = get_paint()
    
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    # Should swap to enum later
    shapes = ["Square", "Rectangle", "Parallelogram"]
    
    if request.method == 'POST':
        # Posts consist of a title and body
        name = request.form['name']
        paint = request.form.get('paint')
        shape = request.form.get("shape") 
        
        # Stores any errors that may arise. 
        error = None

        # A wall must be given a name
        if not name:
            error = 'A name is required.'
        
        if not paint:
            error = 'A paint must be chosen.'
        else:
            try:
                paint = int(paint)
            except:
                 error = ('Does not return an int: %s' % paint[0])
            
        if not shape:
            error = 'A shape must be chosen.'
 
        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:
            # If there was no error, then get a connection to the database
            database = get_database()
                      
            # Insert the new wall into the wall table within the database 
            database.execute(
                'INSERT INTO wall (name, room_id, paint_id, shape, surface)'
                ' VALUES (?, ?, ?, ?, ?)',
                (name, r_id, paint, shape, 0)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('wall.index', r_id=r_id))

    # If it was unsucessful, then return the user back to the create page
    return render_template('wall/create.html', paints=paints, shapes=shapes)

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_paint():
    """This function is used to retrieve a dictionary containing all of the paint from the paint database. 
    """
    
    # Return a connection to the database 
    database = get_database()
                      
    # We want to fetch all the information from every paint in the paint table 
    paints = database.execute(
        'SELECT id, name FROM paint'
    ).fetchall()
    
    return paints

def get_surface_area(shape):
    pass
