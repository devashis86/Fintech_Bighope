from __future__ import print_function # Python 2/3 compatibility
#import numpy as np
import os
import time
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


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """


def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


""" --- Helper Functions --- """


def parse_int(n):
    try:
        return int(n)
    except ValueError:
        return float('nan')


def build_validation_result(is_valid, violated_slot, message_content):
    if message_content is None:
        return {
            "isValid": is_valid,
            "violatedSlot": violated_slot,
        }

    return {
        'isValid': is_valid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }



    
def house_price_pred(location,housetype):
    table = dynamodb.Table('house_price_final')
    key1 = 'location' 
    kv1 = location
    key2 = 'house_type'
    kv2 = housetype
    #response = table.get_item(Key={key1:kv1})
    result = table.scan(
        FilterExpression = Attr('zipcode').eq(kv1) & Attr('house_type').eq(kv2)
        #KeyConditionExpression=Key('zipcode').eq(kv1) & Key('house_type').eq(kv2)
    )
    print('result' , result)
    
    curr_price = []
    pred_price = []
    for price in result['Items']:
        #print('test price ',int(price['saleprice']))
        curr_price.append(float(price['saleprice']))
        pred_price.append(float(price['predict_sale_price']))
    
    #print('price lst', price_lst)
    
    #print ('avearge price',sum(price_lst))
    
    pred_price_per = round(((abs(sum(pred_price) - sum(curr_price))/sum(curr_price))*100),2)
    
    print('House Price Growth % = ' ,pred_price_per)
    return str(pred_price_per)


def validate_housepred_hstyp(housetype_zip):
    
    housetypes = ['condos','singlefamily','townhomes']
	
    if housetype_zip is not None and housetype_zip.lower() not in housetypes:
        return build_validation_result(False,
                                       'housetype',
                                       'We do not have {}, would you like a different search?  '
                                       'Our current available housetypes (condos,singlefamily,townhomes)'.format(housetype_zip))

    return build_validation_result(True, None, None)	


def validate_housepred(location_zip):
    locations = ['20171', '20191', '20190']
    
    if location_zip is not None and location_zip.lower() not in locations:
        return build_validation_result(False,
                                       'location',
                                       'We do not have {}, would you like a different type of location?  '
                                       'Our current available locations (20171,20191,20190)'.format(location_zip))
        
    

    return build_validation_result(True, None, None)


""" --- Functions that control the bot's behavior --- """

def house_price_dtl(location,housetype):
    table = dynamodb.Table('house_price_final')
    key1 = 'location' 
    kv1 = location
    key2 = 'house_type'
    kv2 = housetype
    #response = table.get_item(Key={key1:kv1})
    result = table.scan(
        FilterExpression = Attr('zipcode').eq(kv1) & Attr('house_type').eq(kv2)
        #KeyConditionExpression=Key('zipcode').eq(kv1) & Key('house_type').eq(kv2)
    )
    row_count = 0
    item_dtl = ''
    for item in result['Items']:
    	if row_count <=3:

    		item_dtl = item_dtl + item['house_no'] + '' + item['house_street'] + ' Cuurent $' + item['saleprice'] + ' Predicted $' + item['predict_sale_price'] + '\n'

    		row_count = row_count + 1


    return item_dtl


def housepredict(intent_request):
    """
    Performs dialog management and fulfillment for ordering flowers.
    Beyond fulfillment, the implementation of this intent demonstrates the use of the elicitSlot dialog action
    in slot validation and re-prompting.
    """
    
    
    location_zip = get_slots(intent_request)["location"]
    housetype_zip = get_slots(intent_request)["housetype"]
    source = intent_request['invocationSource']
    
    print('received request: ' + str(intent_request))
    print ("housetype",housetype_zip)
    print ("location1",location_zip)

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt for the first violation detected.
        slots = get_slots(intent_request)
        print('slots are' ,str(slots))  
        validation_result = validate_housepred(location_zip)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result['violatedSlot'],
                               validation_result['message'])
		
        validation_result2 = validate_housepred_hstyp(housetype_zip)
        if not validation_result2['isValid']:
            slots[validation_result2['violatedSlot']] = None
            return elicit_slot(intent_request['sessionAttributes'],
                               intent_request['currentIntent']['name'],
                               slots,
                               validation_result2['violatedSlot'],
                               validation_result2['message'])

        # Pass the price of the flowers back through session attributes to be used in various prompts defined
        # on the bot model.
        output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
        if location_zip is not None and housetype_zip is not None:
            output_session_attributes['Price'] = house_price_pred(location_zip,housetype_zip)#len(location_zip)*5#house_price_pred(location_zip,housetype_zip) 
            #price = house_price_pred(location_zip,housetype_zip)# Elegant pricing model
			
        return delegate(output_session_attributes, get_slots(intent_request))

    # Order the flowers, and rely on the goodbye message of the bot to define the message to the end user.
    # In a real bot, this would likely involve a call to a backend service.
    print(intent_request['sessionAttributes']['Price'])     
    return close(intent_request['sessionAttributes'],
                         'Fulfilled',
                         {'contentType': 'PlainText',
                          'content': 'Approx. next year growth prediction for {hstyp} in {loc} is {prc}%'.format(hstyp=housetype_zip,loc=location_zip,prc=intent_request['sessionAttributes']['Price'])})

""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'gethousepredict':
        return housepredict(intent_request)
    elif intent_name == 'availablehouses':
        housetype = intent_request['currentIntent']['slots']['housetypesavail']
        location  = intent_request['currentIntent']['slots']['locationavail']
        item_dtl = house_price_dtl(location,housetype)
        #print ("housetype",housetype)
        #print ("location",location)
        #print ("House Pirce",price)
        response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                  "contentType": "SSML",
                  "content": " Hosue Details \n {item_dtls}".format(item_dtls = item_dtl)
                },
            }
        }
        print('result = ' + str(response))
        return response

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)