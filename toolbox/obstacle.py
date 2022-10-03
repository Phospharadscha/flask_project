#########################################################################################
#################################### Imports ############################################
#########################################################################################

from enum import Enum
import math
from . import wall
from tabnanny import check
from flask import (
    Blueprint, flash, g, get_template_attribute, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from toolbox.authentication import login_required
from toolbox.database import get_database

#########################################################################################
#################################### Classes ##########################################
#########################################################################################

class Shape(Enum):
    """Shapes store a lambda function used to evaluate their area
    They can then be easily calculated if I store a shape object on a wall/obstacles/etc. 
    """
    SQUARE = lambda b: pow(b, 2)
    RECTANGLE = lambda b, h: b * h
    PARALLELOGRAM = lambda b, h: b * h
    TRAPEZOID = lambda a, b, h: ((a + b) / 2) * h
    TRIANGLE = lambda b, h: 0.5 * (b * h)
    ELLIPSE = lambda a, b: math.pi * (a*b)
    CIRCLE = lambda r: math.pi * pow(r, 2)
    SEMICIRCLE = lambda r: (math.pi * pow(r, 2)) / 2
    
    def __call__(self, args):
        """Override the usual call method to instead allow for the supplying of a variety of multiple args.
        These args are then passed to the matching lambda function to calculate the respective area. 
        """
        return self.value[0](args)
    
    @classmethod
    def to_shape(self, shape_name):
        """This is a class method, meaning it does not need to be called on a Shape object.
        The method is passed a string, which it will then attempt to return a matching shape for.  
        Error handling is not needed, because the user will only ever select from a drop down. 
        """
        match shape_name:
            case "square":
                return Shape.SQUARE
            case "rectangle":
                return Shape.RECTANGLE
            case "parallelogram":
                return Shape.PARALLELOGRAM
            case "trapezoid":
                return Shape.TRAPEZOID
            case "triangle":
                return Shape.TRIANGLE
            case "ellipse":
                return Shape.ELLIPSE
            case "circle":
                return Shape.CIRCLE
            case "semicircle":
                return Shape.SEMICIRCLE
            case _:
                return None


#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the wall. 
The wall will:
- Allow logged in users to create new obstacles, 
- update obstacles they have already created
"""
blueprint = Blueprint('obstacle', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################


@blueprint.route('/<int:w_id>/wall/obstacle', methods=['GET', 'POST']) 
def index(w_id):
    """The Index will display all walls, as outlined above
    The function is passed the id of the room it is contained in via the url.
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch walls from the wall table.
    # We only want walls with a room_id equal to the supplied id
    
    obstacles = get_database().execute(
        'SELECT *'
        ' FROM obstacle o JOIN wall w ON o.wall_id = w.id'
        ' WHERE w.id = ? ORDER BY o.id DESC',
        (w_id,)
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the walls as a parameter. 
    return render_template('obstacle/index.html', obstacles=obstacles, w_id=w_id)

@blueprint.route('/<int:w_id>/wall/obstacle/create', methods=['GET', 'POST']) 
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(w_id):
    """The view used to allow users to create new walls.
    the function is passed the room it will be contained in via its url.  
    """
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    # Should swap to enum later
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]
    
    if request.method == 'POST':
        # Posts consist of a title and body
        name = request.form['name']
        shape = request.form.get("shape") 

        # Stores any errors that may arise. 
        error = None

        # A wall must be given a name
        if not name:
            error = 'A name is required.'
        
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
                'INSERT INTO obstacle (wall_id, name, shape, surface)'
                ' VALUES (?, ?, ?, ?)',
                (w_id, name, shape, -1)
            )
            database.commit()
            
            o_id = database.execute(
                'SELECT id FROM obstacle WHERE surface = -1'
            ).fetchone()
            
            # Redirect the user back to the index page
            return redirect(url_for('obstacle.obstacle_details', w_id=w_id, o_id=o_id['id'], obstacle_shape=shape))

    # If it was unsucessful, then return the user back to the create page
    return render_template('obstacle/create.html', shapes=shapes)

@blueprint.route('/<int:w_id>/wall/obstacle/<int:o_id><string:obstacle_shape>/details', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def obstacle_details(w_id, o_id, obstacle_shape):
    surface_area = 0 
    
    dimensions = [0, 0, 0]

    if request.method == 'POST':
        dimensions[0] = request.form.get('dim_one')
        dimensions[1] = request.form.get('dim_two')
        dimensions[2] = request.form.get('dim_three')
    
        
        error = None 
            
        shape = Shape.to_shape(obstacle_shape.lower())
    
        
        if error is not None:
            flash(error)
        else: 
            if shape is Shape.SQUARE or shape is Shape.CIRCLE or shape is Shape.SEMICIRCLE:
            
                dimensions[0] = check_measurement_input(dimensions[0])
    
                if isinstance(dimensions[0], float):
                    surface_area = shape(dimensions[0])
    
                    database = get_database()
                    # With that connection, update the house in the house table, with the supplied parameters
                    # We update house WHERE its id equal to the supplied id. 
                    database.execute(
                        'UPDATE obstacle SET surface = ?'
                        ' WHERE id = ?',
                        (surface_area, o_id)
                    )
                    database.commit()
    
                else:
                    error = dimensions[0]
            elif shape is Shape.RECTANGLE or shape is Shape.PARALLELOGRAM or shape is Shape.TRIANGLE or shape is Shape.ELLIPSE:
                dimensions[0] = check_measurement_input(dimensions[0])
                dimensions[1] = check_measurement_input(dimensions[1])
    
                if isinstance(dimensions[0], float) and isinstance(dimensions[1], float):
                    surface_area = shape(dimensions[0], dimensions[1])
    
                    database = get_database()
                    # With that connection, update the house in the house table, with the supplied parameters
                    # We update house WHERE its id equal to the supplied id. 
                    database.execute(
                        'UPDATE obstacle SET surface = ?'
                        ' WHERE id = ?',
                        (surface_area, o_id)
                    )
                    database.commit()
    
                else:
                    error = dimensions[0]
                    error = dimensions[1]
            elif shape is Shape.TRAPEZOID:
                dimensions[0] = check_measurement_input(dimensions[0])
                dimensions[1] = check_measurement_input(dimensions[1])
                dimensions[2] = check_measurement_input(dimensions[2])
    
                if isinstance(dimensions[0], float) and isinstance(dimensions[1], float) and isinstance(dimensions[2], float):
                    surface_area = shape(dimensions[0], dimensions[1], dimensions[2])
    
                    database = get_database()
                    # With that connection, update the house in the house table, with the supplied parameters
                    # We update house WHERE its id equal to the supplied id. 
                    database.execute(
                        'UPDATE obstacle SET surface = ?'
                        ' WHERE id = ?',
                        (surface_area, o_id)
                    )
                    database.commit()
    
                else:
                    error = dimensions[0]
                    error = dimensions[1]
                    error = dimensions[2]
            else:
                return "Error: Shape Not Found" 

            wall.update_surface(w_id)
    
            return redirect(url_for('obstacle.index', w_id=w_id))
    
    return render_template('obstacle/obstacle_details.html', w_id=w_id, o_id=o_id, obstacle_shape=obstacle_shape.lower())

@blueprint.route('/<int:w_id>/wall/<int:o_id>/update_name', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_name(o_id, w_id):
    """This view is used to allow users to update their created houses.
    It is passed the id of the house which the user wants to update
    """

    # Retrieve a connection to the database
    database = get_database()    
        # With that connection, update the house in the house table, with the supplied parameters
        # We update house WHERE its id equal to the supplied id. 
    obstacle_name = get_database().execute(
        'SELECT name'
        ' FROM obstacle WHERE id = ?',
        (o_id,)
    ).fetchone()

    database.commit()

    if request.method == 'POST':
        # Retrieve a name for the house from the browser
        name = request.form['name']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('obstacle.index', w_id=w_id))

        if error is not None:
            flash(error)
        else:
            # With that connection, update the house in the house table, with the supplied parameters
            # We update house WHERE its id equal to the supplied id. 
            database.execute(
                'UPDATE obstacle SET name = ?'
                ' WHERE id = ?',
                (name, o_id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('obstacle.index', w_id=w_id))

    # If the house could not be updated, then redirect them back to the update page again
    return render_template('obstacle/update.html', obstacle=obstacle_name, o_id=o_id, w_id=w_id)

@blueprint.route('/<int:w_id>/wall/<int:o_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(w_id, o_id):
    # Retrieves the house by the specified id
    obstacle = get_obstacle(o_id, w_id)
    
    # Get a connection to the database
    database = get_database()
  
    database.execute('DELETE FROM obstacle WHERE id = ?', (o_id,))
    database.commit()
    # When a house has been deleted, redirect to the index
    return redirect(url_for('obstacle.index', w_id=w_id))

@blueprint.route('/<int:w_id>/wall/<int:o_id>/obstacle/update_shape', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_shape(w_id, o_id):
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    # Should swap to enum later
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]

    # Retrieve a connection to the database
    database = get_database()    
    
    # With that connection, update the house in the house table, with the supplied parameters
    # We update house WHERE its id equal to the supplied id. 

    obstacle_name = get_database().execute(
        'SELECT name'
        ' FROM obstacle WHERE id = ?',
        (o_id, )
    ).fetchone()

    database.commit()


    if request.method == 'POST':
        # Posts consist of a title and body
        shape = request.form.get("shape") 
        
        # Stores any errors that may arise. 
        error = None

        # A wall must be given a name
        if not shape:
            error = 'A shape must be chosen.'
 
        # If there as an error then flash it, so it can be displayed by the page
        if error is not None:
            flash(error)
        else:            
            # With that connection, update the house in the house table, with the supplied parameters
            # We update house WHERE its id equal to the supplied id. 
            database.execute(
                'UPDATE obstacle SET surface = ?, shape = ?'
                ' WHERE id = ?',
                (-1, shape, o_id)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('obstacle.obstacle_details', obstacle=obstacle_name, w_id=w_id, o_id=o_id, obstacle_shape=shape))

    # If it was unsucessful, then return the user back to the create page
    return render_template('obstacle/update_shape.html', obstacle=obstacle_name, shapes=shapes, w_id=w_id, o_id=o_id)

#########################################################################################
######################################## Functions ######################################
#########################################################################################

def check_measurement_input(input):
    if input is None:
            return 'Measurement cannot be left empty'
    else:
        try:
            input = float(input)
        except:
            return 'Measurement must be a number'
        else: 
            if input <= 0:
                return 'Measurement must be a positive number greater than 0'
            else:
                return input
 
def get_obstacle(o_id, w_id, check_author=True):
    # Get a connection to the database
    # Then search the database to see if a room exists which:
    # Has the id of the selected room, and has a house_id equal to the supplied c_id
    obstacle = get_database().execute(
        'SELECT * FROM obstacle'
        ' WHERE id = ? AND wall_id = ?',
        (o_id, w_id)
    ).fetchone()

    # If the room does not exist:
    # Which means that a room with the specified id, which is 'within' the specified house
    if obstacle is None:
        abort(404, f"Obstacle id: {o_id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the house, and the house the room is within, is not the same as the house passed to it,
    # then abort with an error
    if check_author and obstacle['wall_id'] != w_id:
        abort(403, "You are not the owner of this obstacle.")

    return obstacle