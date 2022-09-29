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


@blueprint.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update(id):
    """This view is used to allow users to update their posts
    It is passed the id of the post which the user wants to update
    """
    # Return a post by id
    post = get_post(id)


    if request.method == 'POST':
        # Retrieve a title and body for the post from the browser
        title = request.form['title']
        body = request.form['body']
        
        # Used to store errors
        error = None

        # If no title is given then that is an error
        if not title:
            error = 'Title is required.'

        # If there has been an error, then flash it. So that it can be displayed by the webpage. 
        if error is not None:
            flash(error)
        else:
            
            # Retrieve a connection to the database
            database = get_database()
            
            # With that connection, update the post in the post table, with the supplied parameters
            # We update post WHERE it is equal to the supplied id. 
            database.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('blog.index'))

    # If the post could not be updated, then redirect them back to the update page again
    return render_template('blog/update.html', post=post)

@blueprint.route('/<int:id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(id):
    # Retrieves the post by the specified id
    get_post(id) # If the post cannot be found, then the blueprint aborts. 
    
    # Get a connection to the database
    database = get_database()
    
    # From the post table, delete every post where the id equally the supplied id
    database.execute('DELETE FROM post WHERE id = ?', (id,))
    database.commit()
    
    # When a post has been deleted, redirect to the index
    return redirect(url_for('blog.index'))

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def get_post(id, check_author=True):
    """To update and delete posts we need to fetch the post by id.
    Once the post has been found, it then needs to verify if it belongs to the user. 
    
    Is passed a post id, and a bool. Bool is true by default
    The bool is used so that the function can be used to get posts without checking the owner. 
    """
    
    # Get a connection to the database
    # Then search the database to see if a post exists which:
    # Has the id of the selected post, and is owned by the user who requested to delete it
    post = get_database().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # If the post does not exist:
    # Which means that a post with the specified id, which is owned by the specified user
    if post is None:
        abort(404, f"Post id {id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the author, and the author of the post is not the same as the person requesing it,
    # then abort with an error
    if check_author and post['author_id'] != g.user['id']:
        abort(403, "You are not the owner of this post.")

    return post