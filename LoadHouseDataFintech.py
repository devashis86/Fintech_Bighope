import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')




def csv_reader(event, context):
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key =    event['Records'][0]['s3']['object']['key']
    
    obj = s3.get_object(Bucket=bucket , Key=key)
    
    rows = obj['Body'].read().split('\n')
    
    #print('rows', rows)
    
    table = dynamodb.Table('house_price_final')
    
    row_num = 0
    
    with table.batch_writer() as batch:
        for row in rows:
            if row_num == 0:
                pass
            else:
                #print(row.split(',')[0])
                batch.put_item(Item={
                    'object_id':row.split(',')[0],
                    'house_style':row.split(',')[1],
                    'yrblt':row.split(',')[2],
					'bedrooms':row.split(',')[3],
					'fullbath':row.split(',')[4],
					'halfbath':row.split(',')[5],
					'garage':row.split(',')[6],
					'house_condn':row.split(',')[7],
					'basement':row.split(',')[8],
					'roof_desc':row.split(',')[9],
					'sfla':row.split(',')[10],
					'house_type':row.split(',')[11],
					'owner_name':row.split(',')[12],
					'city':row.split(',')[13],
					'house_no':row.split(',')[14],
					'house_street':row.split(',')[15],
					'zipcode':row.split(',')[16],
					'saleprice':row.split(',')[17],
					'predict_sale_price':row.split(',')[18],
                })
            row_num = row_num + 1
    
    #print(event)