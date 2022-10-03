#########################################################################################
#################################### Imports ############################################
#########################################################################################

import sqlite3

import pytest
from toolbox.database import get_database


#########################################################################################
#################################### Functions ############################################
#########################################################################################


def test_get_close_database(app):
    """
        Inits the database we created with the test data, then reads from that database. 
    """
    with app.app_context():
        database = get_database()
        assert database is get_database()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        database.execute('SELECT 1')

    assert 'closed' in str(e.value)
    
    
def test_init_database_command(runner, monkeypatch):
    """
        This test uses the monkeypatch feature to replace the init_db function in __init__ with one that records that it has been called. 
        This command is called by name in another test. 
    """
    
    class Recorder(object):
        called = False

    def fake_init_database():
        Recorder.called = True

    monkeypatch.setattr('toolbox.database.init_database', fake_init_database)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized the database.' in result.output
    assert Recorder.called