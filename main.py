# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is a example for a neo4j fulfillment webhook for an Dialogflow agent
This is meant to be used with the sample agent for Dialogflow, located at


This sample uses the neo4j api and requires an WWO API key

"""

import json

from flask import Flask, request, make_response, jsonify

from get_response import Check_Bill, validate_params

app = Flask(__name__)
log = app.logger
customer_name=""

@app.route('/', methods=['POST'])
def webhook():
    """This method handles the http requests for the Dialogflow webhook

    This is meant to be used in conjunction with the weather Dialogflow agent
    """
    req = request.get_json(silent=True, force=True)
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    if action == 'check_bill':
        res = check_bill(req)
    elif action == 'recommendation':
        res = recommendation(req)
    elif action == 'recharge_exisiting_plan':
        res = recharge(req)
    elif action == 'analyze_usage':
        res = analyze(req)
    else:
        log.error('Unexpected action.')

    print('Action: ' + action)

    return make_response(jsonify({'fulfillmentMessages': res}))


def check_bill(req):
    """Returns a string containing text with a response to the user
    with his/her billing information

    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    parameters = req['queryResult']['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))

    # validate request parameters, return an error if there are issues
    error, check_bill_params = validate_params(parameters)
    if error:
        return error

    if (check_bill_params["given-name"]) is not None:
        customer_name = check_bill_params["given-name"][0]
    print("customer name is : " + customer_name)
    # create a forecast object which retrieves the forecast from a external API
    try:
        checkbill = Check_Bill(check_bill_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # If the user requests a datetime period (a date/time range), get the
    # response
    #response="Hello World!"
    response = checkbill.get_current_response()

    return response

def recommendation(req):
    """Returns a string containing text with a response to the user
    with his/her billing information

    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    parameters = req['queryResult']['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))
    context=req['queryResult']['outputContexts']
    # validate request parameters, return an error if there are issues
    error, recommend_params = validate_params(parameters)
    if error:
        return error
    recommend_params["given-name"]=context[0]["parameters"]["given-name"]
    print(recommend_params)
    # create a forecast object which retrieves the forecast from a external API
    try:
        recommd = Check_Bill(recommend_params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # If the user requests a datetime period (a date/time range), get the
    # response
    #response="Hello World!"
    response = recommd.get_recommendation_response()
    print(response)
    return response

def recharge(req):
    """Returns a string containing text with a response to the user
    with his/her billing information

    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    parameters = req['queryResult']['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))
    context=req['queryResult']['outputContexts']
    # validate request parameters, return an error if there are issues
    error, params = validate_params(parameters)
    if error:
        return error
    params["given-name"]=context[0]["parameters"]["given-name"]
    print(params)
    # create a forecast object which retrieves the forecast from a external API
    try:
        recharge = Check_Bill(params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # If the user requests a datetime period (a date/time range), get the
    # response
    #response="Hello World!"
    response = recharge.get_recharge_response()
    print(response)
    return response

def analyze(req):
    """Returns a string containing text with a response to the user
    with his/her billing information

    Takes the city for the forecast and (optional) dates
    uses the template responses found in weather_responses.py as templates
    """
    parameters = req['queryResult']['parameters']

    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))
    context=req['queryResult']['outputContexts']
    # validate request parameters, return an error if there are issues
    error, params = validate_params(parameters)
    if error:
        return error
    params["given-name"]=context[0]["parameters"]["given-name"]
    print(params)
    # create a forecast object which retrieves the forecast from a external API
    try:
        analyze = Check_Bill(params)
    # return an error if there is an error getting the forecast
    except (ValueError, IOError) as error:
        return error

    # If the user requests a datetime period (a date/time range), get the
    # response
    #response="Hello World!"
    response = analyze.get_analyze_response()
    print(response)
    return response
# def weather_activity(req):
#     """Returns a string containing text with a response to the user
#     with a indication if the activity provided is appropriate for the
#     current weather or a prompt for more information
#
#     Takes a city, activity and (optional) dates
#     uses the template responses found in weather_responses.py as templates
#     and the activities listed in weather_entities.py
#     """
#
#     # validate request parameters, return an error if there are issues
#     error, forecast_params = validate_params(req['queryResult']['parameters'])
#     if error:
#         return error
#
#     # Check to make sure there is a activity, if not return an error
#     if not forecast_params['activity']:
#         return 'What activity were you thinking of doing?'
#
#     # create a forecast object which retrieves the forecast from a external API
#     try:
#         forecast = Forecast(forecast_params)
#     # return an error if there is an error getting the forecast
#     except (ValueError, IOError) as error:
#         return error
#
#     # get the response
#     return forecast.get_activity_response()
#
#
# def weather_condition(req):
#     """Returns a string containing a human-readable response to the user
#     with the probability of the provided weather condition occurring
#     or a prompt for more information
#
#     Takes a city, condition and (optional) dates
#     uses the template responses found in weather_responses.py as templates
#     and the conditions listed in weather_entities.py
#     """
#
#     # validate request parameters, return an error if there are issues
#     error, forecast_params = validate_params(req['queryResult']['parameters'])
#     if error:
#         return error
#
#     # Check to make sure there is a activity, if not return an error
#     if not forecast_params['condition']:
#         return 'What weather condition would you like to check?'
#
#     # create a forecast object which retrieves the forecast from a external API
#     try:
#         forecast = Forecast(forecast_params)
#     # return an error if there is an error getting the forecast
#     except (ValueError, IOError) as error:
#         return error
#
#     # get the response
#     return forecast.get_condition_response()
#
#
# def weather_outfit(req):
#     """Returns a string containing text with a response to the user
#     with a indication if the outfit provided is appropriate for the
#     current weather or a prompt for more information
#
#     Takes a city, outfit and (optional) dates
#     uses the template responses found in weather_responses.py as templates
#     and the outfits listed in weather_entities.py
#     """
#
#     # validate request parameters, return an error if there are issues
#     error, forecast_params = validate_params(req['queryResult']['parameters'])
#     if error:
#         return error
#
#     # Validate that there are the required parameters to retrieve a forecast
#     if not forecast_params['outfit']:
#         return 'What are you planning on wearing?'
#
#     # create a forecast object which retrieves the forecast from a external API
#     try:
#         forecast = Forecast(forecast_params)
#     # return an error if there is an error getting the forecast
#     except (ValueError, IOError) as error:
#         return error
#
#     return forecast.get_outfit_response()
#
#
# def weather_temperature(req):
#     """Returns a string containing text with a response to the user
#     with a indication if temperature provided is consisting with the
#     current weather or a prompt for more information
#
#     Takes a city, temperature and (optional) dates.  Temperature ranges for
#     hot, cold, chilly and warm can be configured in config.py
#     uses the template responses found in weather_responses.py as templates
#     """
#
#     parameters = req['queryResult']['parameters']
#
#     # validate request parameters, return an error if there are issues
#     error, forecast_params = validate_params(parameters)
#     if error:
#         return error
#
#     # If the user didn't specify a temperature, get the weather for them
#     if not forecast_params['temperature']:
#         return weather(req)
#
#     # create a forecast object which retrieves the forecast from a external API
#     try:
#         forecast = Forecast(forecast_params)
#     # return an error if there is an error getting the forecast
#     except (ValueError, IOError) as error:
#         return error
#
#     return forecast.get_temperature_response()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
