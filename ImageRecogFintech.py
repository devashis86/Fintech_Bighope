import boto3
from decimal import Decimal
import json
import urllib

print('Loading function')

rekognition = boto3.client('rekognition')

def lambda_handler(event, context):

    # Get the object from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))

  
    response=rekognition.detect_text(Image={'S3Object':{'Bucket':bucket,'Name':key}})

                        
    textDetections=response['TextDetections']
    print response
    print 'Detected text'

    dt=[]
    for text1 in textDetections:
            if text1['Type'] == 'WORD':
                dt.append (text1['DetectedText'])

    print dt

    v_street_no = dt[0]
    v_street_name=dt[1]
    v_city_name=dt[2]
    v_state_name = dt[3]
    v_zip_cd=dt[4]
    
    print(v_street_no)
    print(v_street_name)
    print(v_city_name)
    print(v_state_name)
    print(v_zip_cd)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('house_price_final')        

    dd_response = table.get_item(
            Key={
                'zipcode':v_zip_cd,
                'house_no': v_street_no#,
                #'house_street': v_street_name,
                #'city':v_city_name
            }
        )
    print("getitem executed")
    print(dd_response)        
    
    item = dd_response['Item']
    psp = item['predict_sale_price']
    
    print("The Predicted Sale Price of the House")
    print(psp)