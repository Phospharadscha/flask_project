#########################################################################################
#################################### Imports ############################################
#########################################################################################
import os
from flask import Flask

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
        DATABASE=os.path.join(app.instance_path, 'cryptid.sqlite'),
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
    
    # Import modules from the root directory
    from . import database, authentication, blog
    
    # This registers two functions with the application: 
    # - app.teardown_appcontext(close_db)   
    # - app.cli.add_command(init_db_command)
    database.init_app(app)
    
    # Import and register blueprints
    app.register_blueprint(authentication.blueprint)
    
    app.register_blueprint(blog.blueprint)
    # Blog does not have a url_prefix, so the index will be at '/'
    # This makes the blog index the main index
    #  Associates the end-point name 'index' with the / url, so that url_for('index') or url_for('blog.index') both generate the same url
    app.add_url_rule('/', endpoint='index') 


    return app