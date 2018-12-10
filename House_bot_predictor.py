"""
HousePriceBot Lambda handler.
"""
#from urllib.request import Request, urlopen
from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import math
import logging
import uuid
from boto3.dynamodb.conditions import Key,Attr
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dynamodb = boto3.resource('dynamodb')


def house_price(location,housetype):
    table = dynamodb.Table('House_Price_Bot')
    key1 = 'location' 
    kv1 = location
    key2 = 'housetypes' 
    kv2 = housetype
    response = table.get_item(Key={key1:kv1,key2:kv2})
    print('House Price = ' ,response[u'Item']['price'])
    return response[u'Item']['price']
    
    
def lambda_handler(event, context):
    print('received request: ' + str(event))
    housetype = event['currentIntent']['slots']['housetypes']
    location  = event['currentIntent']['slots']['Locations']
    price = house_price(location ,housetype)
    print ("housetype",housetype)
    print ("location",location)
    print ("House Pirce",price)
    response = {
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": "Fulfilled",
            "message": {
              "contentType": "SSML",
              "content": "{hstp} approx. price in {loc} is {prc}$".format(hstp=housetype,loc=location,prc=price)
            },
        }
    }
    print('result = ' + str(response))
    return response