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

