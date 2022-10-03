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

    obstacles = get_database().execute(
        'SELECT id, wall_id FROM obstacle'
    ).fetchall()

    # Wall id : number
    obstacles_per_wall = {0 : 0}
    
    for obstacle in obstacles:
        if obstacle['wall_id'] not in obstacles_per_wall: 
            obstacles_per_wall[obstacle['wall_id']] = 1
        else:
            obstacles_per_wall[obstacle['wall_id']] += 1

    paints = get_paint()
    
    # Returns a command to render the specified template, and passes it the walls as a parameter. 
    return render_template('wall/index.html', walls=walls, r_id=r_id, paints=get_paint(), obstacles=obstacles_per_wall)

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
                'INSERT INTO wall (name, room_id, paint_id, shape, surface, original_surface)'
                ' VALUES (?, ?, ?, ?, ?, ?)',
                (name, r_id, paint, shape, -1, -1)
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
        dimensions[1] = request.form.get('dim_two')
        dimensions[2] = request.form.get('dim_three')
    
        
        error = None 
            
        shape = Shape.to_shape(wall_shape.lower())
    
        
        if error is not None:
            flash(error)
        else: 
            if shape is Shape.SQUARE or shape is Shape.CIRCLE or shape is Shape.SEMICIRCLE:
            
                dimensions[0] = check_measurement_input(dimensions[0])
    
                if isinstance(dimensions[0], float):
                    surface_area = shape(dimensions[0])
                    surface_area = get_surface(w_id, surface_area)
    
                    database = get_database()
                    # With that connection, update the house in the house table, with the supplied parameters
                    # We update house WHERE its id equal to the supplied id. 
                    database.execute(
                        'UPDATE wall SET surface = ?, original_surface = ?'
                        ' WHERE id = ?',
                        (surface_area, surface_area, w_id)
                    )
                    database.commit()
    
                else:
                    error = dimensions[0]
            elif shape is Shape.RECTANGLE or shape is Shape.PARALLELOGRAM or shape is Shape.TRIANGLE or shape is Shape.ELLIPSE:
                dimensions[0] = check_measurement_input(dimensions[0])
                dimensions[1] = check_measurement_input(dimensions[1])
    
                if isinstance(dimensions[0], float) and isinstance(dimensions[1], float):
                    surface_area = shape(dimensions[0], dimensions[1])
                    surface_area = get_surface(w_id, surface_area)

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
                    error = dimensions[1]
            elif shape is Shape.TRAPEZOID:
                dimensions[0] = check_measurement_input(dimensions[0])
                dimensions[1] = check_measurement_input(dimensions[1])
                dimensions[2] = check_measurement_input(dimensions[2])
    
                if isinstance(dimensions[0], float) and isinstance(dimensions[1], float) and isinstance(dimensions[2], float):
                    surface_area = shape(dimensions[0], dimensions[1], dimensions[2])
                    surface_area = get_surface(w_id, surface_area)

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
                    error = dimensions[1]
                    error = dimensions[2]
            else:
                return "Error: Shape Not Found" 
    
            return redirect(url_for('wall.index', r_id=r_id))
    
    return render_template('wall/wall_details.html', r_id=r_id, w_id=w_id, wall_shape=wall_shape.lower())

@blueprint.route('/<int:r_id>/room/wall/<int:w_id>/update_name_paint', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_name_paint(r_id, w_id):
    """This view is used to allow users to update their created houses.
    It is passed the id of the house which the user wants to update
    """

    # Retrieve a connection to the database
    database = get_database()    
        # With that connection, update the house in the house table, with the supplied parameters
        # We update house WHERE its id equal to the supplied id. 
    wall_name = get_database().execute(
        'SELECT name'
        ' FROM wall WHERE id = ?',
        (w_id, )
    ).fetchone()

    database.commit()

    paints = get_paint()

    if request.method == 'POST':
        # Retrieve a name for the house from the browser
        name = request.form['name']
        paint = request.form['paint']
        
        # Used to store errors
        error = None

        # If no name is given then that is an error
        if not name:
            return redirect(url_for('wall.index', r_id=r_id))

        if not paint:
            error = 'Paint cannot be left blank'

        if error is not None:
            flash(error)
        else:
            # With that connection, update the house in the house table, with the supplied parameters
            # We update house WHERE its id equal to the supplied id. 
            database.execute(
                'UPDATE wall SET name = ?, paint_id = ?'
                ' WHERE id = ?',
                (name, paint, w_id)
            )
            database.commit()
            
            # redirect the user back to the index
            return redirect(url_for('wall.index', r_id=r_id))

    # If the house could not be updated, then redirect them back to the update page again
    return render_template('wall/update.html', wall=wall_name, w_id=w_id, r_id=r_id, paints=paints)

@blueprint.route('/<int:r_id>/room/wall/<int:w_id>/update_shape', methods=('GET', 'POST'))
@login_required # Calls the login_required() function from authentication. Must be logged in
def update_shape(r_id, w_id):
    # An array of valid shapes. 
    # Used to define a drop down menu in html
    # Should swap to enum later
    shapes = ["Square", "Rectangle", "Parallelogram", "Trapezoid", "Triangle", "Ellipse", "Circle", "Semicircle"]

    # Retrieve a connection to the database
    database = get_database()    
    
    # With that connection, update the house in the house table, with the supplied parameters
    # We update house WHERE its id equal to the supplied id. 

    wall_name = get_database().execute(
        'SELECT name'
        ' FROM wall WHERE id = ?',
        (w_id, )
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
                'UPDATE wall SET surface = ?, Shape = ?'
                ' WHERE id = ?',
                (-1, shape, w_id)
            )
            database.commit()
            
            # Redirect the user back to the index page
            return redirect(url_for('wall.wall_details', wall=wall_name, r_id=r_id, w_id=w_id, wall_shape=shape))

    # If it was unsucessful, then return the user back to the create page
    return render_template('wall/update_shape.html', wall=wall_name, shapes=shapes, r_id=r_id, w_id=w_id)

@blueprint.route('/<int:r_id>/room/wall/<int:w_id>/delete', methods=('POST',))
@login_required # Calls the login_required() function from authentication. Must be logged in
def delete(r_id, w_id):
    # Retrieves the house by the specified id
    wall = get_wall(w_id, r_id)
    
    # Get a connection to the database
    database = get_database()
  
    database.execute('DELETE FROM wall WHERE id = ?', (w_id,))
    database.commit()
    # When a house has been deleted, redirect to the index
    return redirect(url_for('wall.index', r_id=r_id))

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
    
def get_wall(w_id, r_id, check_author=True):
    # Get a connection to the database
    # Then search the database to see if a room exists which:
    # Has the id of the selected room, and has a house_id equal to the supplied c_id
    wall = get_database().execute(
        'SELECT * FROM wall'
        ' WHERE id = ? AND room_id = ?',
        (w_id, r_id)
    ).fetchone()

    # If the room does not exist:
    # Which means that a room with the specified id, which is 'within' the specified house
    if wall is None:
        abort(404, f"Wall id: {w_id} doesn't exist.") # abort will raise a special exception that returns HTTP status code

    # If we want to check the house, and the house the room is within, is not the same as the house passed to it,
    # then abort with an error
    if check_author and wall['room_id'] != r_id:
        abort(403, "You are not the owner of this wall.")

    return wall   

def update_surface(w_id):
    database = get_database()

    surfaces = database.execute(
        'SELECT surface, original_surface FROM wall'
        ' WHERE id = ?',
        (w_id,)
    ).fetchone()

    obstacles = database.execute(
        'SELECT surface FROM obstacle'
        ' WHERE wall_id = ?',
        (w_id,)
    ).fetchall()

    surface = surfaces['original_surface']

    for obstacle in obstacles:
       surface -= obstacle['surface']

    database.execute(
        'UPDATE wall SET surface = ?'
        ' WHERE id = ?',
        (surface, w_id)
    )
    database.commit()

def get_surface(w_id, surface):
    database = get_database()

    obstacles = database.execute(
        'SELECT surface FROM obstacle'
        ' WHERE wall_id = ?',
        (w_id,)
    ).fetchall()

    if obstacles is not None:
        for obstacle in obstacles:
            surface -= obstacle['surface']
    
    return surface