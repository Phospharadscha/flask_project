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

#########################################################################################
######################################## Functions ######################################
#########################################################################################


