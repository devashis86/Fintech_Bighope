import json
import boto3
import csv
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    # TODO implement
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    obj = s3.get_object(Bucket = bucket, Key = key)
    
    print(obj)
    #rows = obj['Body'].read().split('\n')
    rows = obj['Body'].read().strip().split('\n')
    print rows
    sam = map(str.strip,rows)
    print sam
    print 'passed sam'
    dyn = list(sam)
    print 'length as',len(dyn)
    table = dynamodb.Table('house_prcg')
    
    with table.batch_writer() as batch:
        for i in range(1,len(dyn)):
            print i
            batch.put_item(
                Item={
                'OBJECTID':dyn[i].split(',')[0],
                'STYLE_DESC':dyn[i].split(',')[1],
                'YRBLT':dyn[i].split(',')[2],
                'Sale Price':dyn[i].split(',')[3],
                'RMBED':dyn[i].split(',')[4], 
                'FIXBATH':dyn[i].split(',')[5],
                'FIXHALF':dyn[i].split(',')[6],
                'BSMTCAR':dyn[i].split(',')[7],
                'SFLA':dyn[i].split(',')[8],
                'BSMT_DESC':dyn[i].split(',')[9],
                'Street Number':dyn[i].split(',')[10],
                'Street Name':dyn[i].split(',')[11],
                'City':dyn[i].split(',')[12],
                'State':dyn[i].split(',')[13],
                'ZIP':dyn[i].split(',')[14],
                'lat':dyn[i].split(',')[15],
                'long':dyn[i].split(',')[16]
            }
                )
            print 'loop',i,'completed'
        print 'for loop is completed'    
    #print(event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
