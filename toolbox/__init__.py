#########################################################################################
#################################### Imports ############################################
#########################################################################################
import os
from flask import Flask

from . import house

#########################################################################################
#################################### Factory Function ###################################
#########################################################################################

def create_app(test_config=None):
    """Create and configure the app. 
    This is the appliation factory function. 
    """
    
    """Create the flask Instance.
    - __name__ is the name of the module
    - the second parameter tells the app that confg files are relative to the instance folder
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(    # The path where teh SQLite database file will be saved
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'toolbox.sqlite'),
    )

    """If a test config is given, then override the default configuration. 
    This can be used to set a SECRET_KEY
    """
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    
    try:
        os.makedirs(app.instance_path)  # Ensure instance folder exists
    except OSError:
        pass
    
    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # Import modules from the root directory
    from . import database, authentication, paint, weather, room, wall, house, obstacle
    
    # This registers two functions with the application: 
    # - app.teardown_appcontext(close_db)   
    # - app.cli.add_command(init_db_command)
    database.init_app(app)
    
    app.register_blueprint(house.blueprint)
    # Blog does not have a url_prefix, so the index will be at '/'
    # This makes the blog index the main index
    #  Associates the end-point name 'index' with the / url, so that url_for('index') or url_for('blog.index') both generate the same url
    app.add_url_rule('/', endpoint='index') 
    
    # Import and register paint blueprint
    app.register_blueprint(paint.blueprint)

    # Import and register weather blueprint
    app.register_blueprint(weather.blueprint)
    
    # Import and register authentication blueprint
    app.register_blueprint(authentication.blueprint)
    
    # Import and register room blueprint
    app.register_blueprint(room.blueprint)
    
    # Import and register wall blueprint
    app.register_blueprint(wall.blueprint)

        # Import and register obstacle blueprint
    app.register_blueprint(obstacle.blueprint)


    return app
