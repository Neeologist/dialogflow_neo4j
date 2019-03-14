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

"""Module that defines the Forecast class and defines helper functions to
process and validate date related to the weather forecast class

This is meant to be used with the sample weather agent for Dialogflow, located at
https://console.dialogflow.com/api-client/#/agent//prebuiltAgents/Weather

This sample uses the WWO Weather Forecast API and requires an WWO API key
Get a WWO API key here: https://developer.worldweatheronline.com/api/
"""

import random
from datetime import datetime as dt
from datetime import timedelta

import requests
from neo4j.v1 import GraphDatabase, basic_auth
from config import (NEO4J_URL, USERNAME, PASSWORD)

class Check_Bill(object):
    """The Forecast object implements tracking of and forecast retrieval for
    a request for a weather forecast.  Several methods return various human
    readable strings that contain the weather forecast, condition, temperature
    and the appropriateness of outfits and activities to for forecasted weather

    This requires setting the WWO_API_KEY constant in config.py to a string
    with a valid WWO API key for retrieving weather forecasts

    Attributes:
        city (str): the city for the weather forecast
        datetime_start (datetime.datetime): forecast start date or datetime
        datetime_end (datetime.datetime): forecast end date or datetime
        unit (str): the unit of temperature: Celsius ('C') or Fahrenheit ('F')
        action (dict): any actions in the request (activity, condition, outfit)
        forecast (dict): structure containing the weather forecast from WWO
    """

    def __init__(self, params):
        """Initializes the Forecast object

        gets the forecast for the provided dates
        """

        self.name = params['given-name'][0]
        self.check = self.__check_bill()

    def __check_bill(self):
        """Takes a date or date period and a city

        raises an exception when dates are outside what can be forecasted
        Returns the weather for the period and city as a dict
        """
        cypher =\
        '''MATCH((u:User)-[:subscribe]->(p:Plan)<-[:plan]-(dp:Plans))\
         Where u.name = {name}\
         RETURN p\
        '''
        parameters={'name':self.name}
        response = self.__call_neo4j_api(cypher, parameters)
        forecast = response

        return forecast

    def __call_neo4j_api(self, cypher,parameters):
        """Calls the neo4j driver for query a result

        raises an exception for network errors
        Returns a dict of the JSON 'data' attribute in the response
        """
        driver = GraphDatabase.driver(
            NEO4J_URL,
            auth=basic_auth(USERNAME, PASSWORD))
        session = driver.session()
        response={}
        results = session.run(cypher,parameters)

        for record in results:
            res=record.items()
            for k,v in res:
                response[k]=v

        return response

    def get_current_response(self):
        direc = self.check
        print(direc)
        text = "Greetings, "+self.name+"! It seems it's time to recharge your plan!\n"
        text_message=self.fb_text(text)
        output=[text_message]
        for k,v in direc.items():
            url=v["url"]
            title= "Your current plan is " + v["name"] +", and the monthly fee is " + v["fee"]
            button1_text = "Recharge Now"
            postback1 = None
            button2_text = "Find a New Plan"
            postback2=None
            button3_text = "Analyze my Usage"
            postback3 =None
            card_message=self.fb_card(title, url, button1_text, postback1, button2_text, postback2, button3_text, postback3)
            output.append(card_message)
        # button1_text = "Recharge Now"
        # button2_text = "Find a New Plan"
        # button3_text = "Analyze my Usage"
        # card_message=self.fb_card(title, url, button1_text,None, button2_text, None,button3_text,None)
        # output=[text_message,card_message]
        return output

    def get_recommendation_response(self):
        text = "Based on your historical usage, we recommend you the following plan:\n"
        text_message=self.fb_text(text)
        plans = self.recommendation()
        output=[text_message]
        for k,v in plans.items():
            url=v["url"]
            title= "Recommended!" + v["name"] +", and the monthly fee is " + v["fee"]
            button1_text = "Why this plan?"
            postback1 = "How about " + v["name"]
            button2_text = "No, I will use my existing plan"
            postback2="recharge exisiting plan"
            button3_text = "Talk to an agent"
            postback3 =None
            card_message=self.fb_card(title, url, button1_text, postback1, button2_text, postback2, button3_text, postback3)
            output.append(card_message)
        return output

    def recommendation(self):
        """Takes a date or date period and a city

        raises an exception when dates are outside what can be forecasted
        Returns the weather for the period and city as a dict
        """
        cypher =\
        '''\
            MATCH((u:User)-[:subscribe]->(p:Plan)<-[:plan]-(dp:Plans))\
            Where u.name = {name}\
            OPTIONAL MATCH((p)-[:upgrade]->(up1)-[:upgrade]->(up2))\
            RETURN up1 AS rec1, up2 AS rec2
        '''
        parameters={'name':self.name}
        response = self.__call_neo4j_api(cypher,parameters)
        return response

    def get_recharge_response(self):

        output=[]
        plan = self.recharge()
        for k,v in plan.items():
            text= "Ok, your charge is " + v["fee"]
            text_message=self.fb_text(text)
            output.append(text_message)

        text = "I see we have your VISA credit card ending with 9231 in your information. \
        Should I complete the payment with the same card?\n"
        text_message=self.fb_text(text)
        output.append(text_message)
        return output

    def recharge(self):
        """Takes a date or date period and a city

        raises an exception when dates are outside what can be forecasted
        Returns the weather for the period and city as a dict
        """
        cypher =\
        '''\
            Match(u:User)-[:Bill]->(b)-[:Month]->(m:Bill{Month:"2019-01"})\
            Where u.name = {name}\
            Return m\
        '''
        parameters={'name':self.name}
        response = self.__call_neo4j_api(cypher,parameters)
        return response

    def get_analyze_response(self):

        output=[]
        historical_data = self.analyze()
        hist_fig=generate_figure(historical_data)

        for k,v in plan.items():
            text= "Ok, your charge is " + v["fee"]
            text_message=self.fb_text(text)
            output.append(text_message)

        text = "I see we have your VISA credit card ending with 9231 in your information. \
        Should I complete the payment with the same card?\n"
        text_message=self.fb_text(text)
        output.append(text_message)
        return output

    def analyze(self):
        """Takes a date or date period and a city

        raises an exception when dates are outside what can be forecasted
        Returns the weather for the period and city as a dict
        """
        cypher =\
        '''\
            Match(u:User)-[:usage]->(b)-[:Month]->(m)\
            Where u.name = {name}\
            Return m\
        '''
        parameters={'name':self.name}
        response = self.__call_neo4j_api(cypher,parameters)
        return response

    def fb_text(self, text):
        text_message={
          "text": {
            "text": [
              text
            ]
          },
          "platform": "FACEBOOK"
        }
        return text_message

    def fb_card(self,title, url, button1_text,postback1, button2_text,postback2, button3_text,postback3):

        if(postback1 is None):
            postback1=button1_text
        if(postback2 is None):
            postback2=button2_text
        if(postback3 is None):
            postback3=button3_text

        card_message = {
                "card": {
                  "title": title,
                  "imageUri": url,
                  "buttons": [
                    {
                      "text": button1_text,
                      "postback": postback1
                    },
                    {
                      "text": button2_text,
                      "postback": postback2
                    },
                    {
                      "text": button3_text,
                      "postback": postback3
                    }
                  ]
                },
                "platform": "FACEBOOK"
                }
        return card_message

def validate_params(parameters):
    """Takes a list of parameters from a HTTP request and validates them

    Returns a string of errors (or empty string) and a list of params
    """

    # Initialize error and params
    error_response = ''
    params = {}

    # City
    # if (parameters.get('address') and
    #         isinstance(parameters.get('address'), dict)):
    #     params['city'] = parameters.get('address').get('city')
    # else:
    #     params['city'] = None
    #     error_response += 'please specify city '
    if(parameters.get('given-name')):
        params['given-name'] = parameters.get('given-name')
    else:
        params['given-name'] = None
        #error_response += 'please specify whose bill '


    return error_response.strip(), params
