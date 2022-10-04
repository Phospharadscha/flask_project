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

"""Blueprint for the obstacles. 
The obstacle blueprint will:
- Allow logged in users to create new obstacles within their owned walls, 
- update obstacles they have already created
"""
blueprint = Blueprint('obstacle', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################


@blueprint.route('/<int:w_id>/wall/obstacle', methods=['GET', 'POST']) 
def index(w_id):
    """The Index will display all obstacles, as outlined above
    The function is passed the id of the wall it is contained in via the url.
    """
    database = get_database() # Retrieve a connection to the database
    
    # From the database, fetch obstacles from the obstacle table.
    # We only want obstacles with a wall_id equal to the supplied id
    obstacles = get_database().execute(
        'SELECT *'
        ' FROM obstacle o JOIN wall w ON o.wall_id = w.id'
        ' WHERE w.id = ? ORDER BY o.id DESC',
        (w_id,)
    ).fetchall()
    
    # Returns a command to render the specified template, and passes it the obstacles as a parameter. 
    return render_template('obstacle/index.html', obstacles=obstacles, w_id=w_id)

@blueprint.route('/<int:w_id>/wall/obstacle/create', methods=['GET', 'POST']) 
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def create(w_id):
    """The view used to allow users to create new obstacles.
    the function is passed the wall it will be contained in via its url.  
    """
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]
    
    if request.method == 'POST':
        
        # Obstacles consist of a name and shape
        # They also require a surface area, but that is defined later
        name = request.form['name']
        shape = request.form.get("shape") 

        # Stores any errors that may arise. 
        error = None

        # An obstacle must be given a name and a shape
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

            # Insert the new obstacle into the obstacle table within the database 
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
    """
        This function allows us to define the dimensions of the obstacle. 
        We defined the shape in create(), so here we just supply the dimensiosn and calculate the surface area.
        That is then used to update the obstacle table. 
    """
    
    surface_area = 0 
    
    dimensions = [0, 0, 0]

    if request.method == 'POST':
        # Expect to recieve up to 3 dimensions, depending on the shape
        dimensions[0] = request.form.get('dim_one')
        dimensions[1] = request.form.get('dim_two')
        dimensions[2] = request.form.get('dim_three')
    
        
        error = None 
        shape = Shape.to_shape(obstacle_shape.lower()) # Retrive a shape object to calculate the dimensions
    
        # Flash an error if there is one
        if error is not None:
            flash(error)
        else:  # Otherwise, calculate the surface area
            
            # Depending on the shape calculate the surface area
            if shape is Shape.SQUARE or shape is Shape.CIRCLE or shape is Shape.SEMICIRCLE:
            
                dimensions[0] = check_measurement_input(dimensions[0]) # Validate the user input. Returns either the input as a float, or an error message
    
                # If it is not a float, then it is an error
                if isinstance(dimensions[0], float): 
                    surface_area = shape(dimensions[0])
    
                    database = get_database()
                    
                    # With that connection, update the obstacle in the database, with the supplied parameters
                    database.execute(
                        'UPDATE obstacle SET surface = ?'
                        ' WHERE id = ?',
                        (surface_area, o_id)
                    )
                    database.commit()
    
                else: # If it was en error then set that error
                    error = dimensions[0]
            elif shape is Shape.RECTANGLE or shape is Shape.PARALLELOGRAM or shape is Shape.TRIANGLE or shape is Shape.ELLIPSE:
                dimensions[0] = check_measurement_input(dimensions[0])
                dimensions[1] = check_measurement_input(dimensions[1])
    
                if isinstance(dimensions[0], float) and isinstance(dimensions[1], float):
                    surface_area = shape(dimensions[0], dimensions[1])
    
                    database = get_database()
 
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
            
            if error is not None:
                flash(error)
            else: 
                # Now we have calculated the surface area, we need to update the area of the wall it is within. 
                # That way, we account for the new obstacle as soon as it is created
                wall.update_surface(w_id) 

                return redirect(url_for('obstacle.index', w_id=w_id))

    return render_template('obstacle/obstacle_details.html', w_id=w_id, o_id=o_id, obstacle_shape=obstacle_shape.lower())

@blueprint.route('/<int:w_id>/wall/<int:o_id>/update_name', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_name(o_id, w_id):
    """
        This view is used to allow users to update the names of created obstacles.
        The id of the obstacle is passed via the url 
    """

    # Retrieve a connection to the database
    database = get_database()    
        # With that connection, fetch the name of the obstacle we want to rename
    obstacle_name = get_database().execute(
        'SELECT name'
        ' FROM obstacle WHERE id = ?',
        (o_id,)
    ).fetchone()

    database.commit()

    if request.method == 'POST':
        # Retrieve a name for the house from the browser
        name = request.form['name']
        
        
        error = None
        
        # If no name is given then we just redirect to the index. Since the name will not be updated if left blank
        if not name:
            return redirect(url_for('obstacle.index', w_id=w_id))


        if error is not None:
            flash(error)
        else:
            
            # With that connection, update the obstacle in the house table, with the new name
            database.execute(
                'UPDATE obstacle SET name = ?'
                ' WHERE id = ?',
                (name, o_id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('obstacle.index', w_id=w_id))

    return render_template('obstacle/update.html', obstacle=obstacle_name, o_id=o_id, w_id=w_id)

@blueprint.route('/<int:w_id>/wall/<int:o_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(w_id, o_id):
    
    # Retrieves the obstacle by the specified id
    obstacle = get_obstacle(o_id, w_id)
    
    # Get a connection to the database
    database = get_database()
  
    # Delete from database at the passed id
    database.execute('DELETE FROM obstacle WHERE id = ?', (o_id,))
    database.commit()
    
    return redirect(url_for('obstacle.index', w_id=w_id))

@blueprint.route('/<int:w_id>/wall/<int:o_id>/obstacle/update_shape', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_shape(w_id, o_id):
    """
        This function is used to update the shape and dimensions of the obstacle. 
        It is a second function because you may just want to update the name, without needing to update the dimensions as well. 
    """ 
    
    
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]

    # Retrieve a connection to the database
    database = get_database()    
    
    # With that connection, update the obstacle in the obstacle table
    obstacle_name = get_database().execute(
        'SELECT name'
        ' FROM obstacle WHERE id = ?',
        (o_id, )
    ).fetchone()

    database.commit()

    if request.method == 'POST':
        # We need to get a shape for the object
        shape = request.form.get("shape") 
        
        error = None

        if not shape:
            error = 'A shape must be chosen.'
            
        if error is not None:
            flash(error)
        else:            

            database.execute(
                'UPDATE obstacle SET surface = ?, shape = ?'
                ' WHERE id = ?',
                (-1, shape, o_id)
            )
            database.commit()
            
            return redirect(url_for('obstacle.obstacle_details', obstacle=obstacle_name, w_id=w_id, o_id=o_id, obstacle_shape=shape)) # Once we have the shape, redirect to the function which calculates surface area

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