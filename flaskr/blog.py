#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.authentication import login_required
from flaskr.database import get_database


#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the blog. 
The blog will:
- List all posts
- allow logged in users to create posts, 
- allow the author of a post to edit or delete their post
"""
blueprint = Blueprint('blog', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################

@blueprint.route('/') # The '/' will lead to this function
def index():
    """The Index will display all posts, as outlined above
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch the everythinh from the posts table.
    # Order them by created in descending order. So new posts show at the top. 
    posts = database.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the posts as a parameter. 
    return render_template('blog/index.html', posts=posts)

@blueprint.route('/create', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create():
    """The view used to allow users to create posts.
    Users must be logged in to create a post. 
    """
    if request.method == 'POST':
        # Posts consist of a title and body
        title = request.form['title']
        body = request.form['body']
        
        # Stores any errors that may arise. 
        error = None

        # title must be provided
        if not title:
            error = 'Title is required.'

        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:
            
            # If there was no error, then get a connection to the database
            database = get_database()
            
            # Insert the post into the post table within the database 
            database.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('blog.index'))

    # If it was unsucessful, then return the user back to the create page
    return render_template('blog/create.html')