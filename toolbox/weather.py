#########################################################################################
#################################### Imports ############################################
#########################################################################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, Response
)
from werkzeug.exceptions import abort

from toolbox.authentication import login_required
from toolbox.database import get_database

import json
import urllib.request

#########################################################################################
#################################### Blueprint ##########################################
#########################################################################################

"""Blueprint for the weather api
"""
blueprint = Blueprint('weather', __name__)

#########################################################################################
######################################## views ##########################################
#########################################################################################


@blueprint.route('/forecast', methods=['GET', 'POST'])
def get_weather():
    
    target_city = 'London'
    
    if request.method == 'POST':
        target_city = request.form['city']
    
    try:
        
        request_data = {}
        request_data['q'] = target_city
        request_data['appid'] = '031f7e7f165f2e7c24de04b9358e39f6'
        request_data['units'] = 'metric'
        url_values = urllib.parse.urlencode(request_data)
        url = 'http://api.openweathermap.org/data/2.5/forecast'
        full_url = url + '?' + url_values
        request_data = urllib.request.urlopen(full_url)

        resp = Response(request_data)
        resp.status_code = 200
        
        return render_template('weather/index.html', title=f'Weather for: {target_city}', data=json.loads(request_data.read().decode('utf8')))
    except:
        
        target_city = 'London'
        
        request_data = {}
        request_data['q'] = target_city
        request_data['appid'] = '031f7e7f165f2e7c24de04b9358e39f6'
        request_data['units'] = 'metric'
        url_values = urllib.parse.urlencode(request_data)
        url = 'http://api.openweathermap.org/data/2.5/forecast'
        full_url = url + '?' + url_values
        request_data = urllib.request.urlopen(full_url)

        resp = Response(request_data)
        resp.status_code = 200
        
        return render_template('weather/index.html', title=f'Weather for: {target_city}', data=json.loads(request_data.read().decode('utf8')))
    


