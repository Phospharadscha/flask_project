#########################################################################################
#################################### Imports ############################################
#########################################################################################

from enum import Enum
import math
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
    TRAPEZOID = lambda b, h, a: ((a + b) / 2) * h
    TRIANGLE = lambda b, h: 0.5 * (b * h)
    ELLIPSE = lambda b, a: math.pi * (a*b)
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
        'SELECT w.id, room_id, w.name, paint_id, surface'
        ' FROM wall w JOIN room r ON w.room_id = r.id'
        ' WHERE r.id = ? ORDER BY w.id DESC',
        (r_id,)
    ).fetchall()

    paints = get_paint()
    
    # Returns a command to render the specified template, and passes it the walls as a parameter. 
    return render_template('wall/index.html', walls=walls, room_id=r_id, paints=get_paint())

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
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]
    
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
                (name, r_id, paint, shape, -1)
            )
            database.commit()
            
            w_id = database.execute(
                'SELECT id FROM wall WHERE surface = -1'
            ).fetchone()
            
            # Redirect the user back to the index page
            return redirect(url_for('wall.wall_details', r_id=r_id, w_id=w_id['id'], wall_shape=shape))

    # If it was unsucessful, then return the user back to the create page
    return render_template('wall/create.html', paints=paints, shapes=shapes)

@blueprint.route('/<int:r_id>/room/wall/create/<int:w_id><string:wall_shape>/details', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in. 
def wall_details(r_id, w_id, wall_shape):
    surface_area = 0 
    
    dimensions = [0, 0, 0]
    
    
    
    if request.method == 'POST':
        dimensions[0] = request.form.get('dim_one')
    
        
        error = None 
            
        shape = Shape.to_shape(wall_shape.lower())
    
        
        if error is not None:
            flash(error)
        else: 
            if shape is Shape.SQUARE:
            
                dimensions[0] = check_measurement_input(dimensions[0])
    
                if isinstance(dimensions[0], float):
                    surface_area = shape(dimensions[0])
    
                    database = get_database()
                    # With that connection, update the house in the house table, with the supplied parameters
                    # We update house WHERE its id equal to the supplied id. 
                    database.execute(
                        'UPDATE wall SET surface = ?'
                        ' WHERE id = ?',
                        (surface_area, w_id)
                    )
                    database.commit()
    
                else:
                    error = dimensions[0]
            elif shape is Shape.RECTANGLE or shape is Shape.PARALLELOGRAM or shape is Shape.TRIANGLE:
                pass
            elif shape is Shape.TRAPEZOID:
                pass
            elif shape is Shape.ELLIPSE:
                pass
            elif shape is Shape.CIRCLE or shape is Shape.SEMICIRCLE:
                pass
            else:
                return "tee hee" 
    
            return redirect(url_for('wall.index', r_id=r_id))
    
    return render_template('wall/wall_details.html', r_id=r_id, w_id=w_id, wall_shape=wall_shape.lower())

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
    
    
    

