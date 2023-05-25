from datetime import datetime, time
import json
import uuid
import boto3
import requests
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    records = event['Records']
    for record in records:
        bucket = record['s3']['bucket']['name']
        location = s3_client.get_bucket_location(Bucket=bucket)['LocationConstraint']
        key = record['s3']['object']['key']

        result = carnet_analyze_image(f'https://{bucket}.s3.{location}.amazonaws.com/{key}')

        if result is not None:
            save_to_db(result, 'carnetResponseDB')
        else:
            result = rekognition_analyze_image(bucket, key)
            save_to_db(result, 'rekogintionAnalysesDB')

    return {"statusCode": 200, "body": "OK"}


def carnet_analyze_image(image_url):
    response = requests.post('https://carnet.ai/recognize-url', data=image_url)
    status_code = response.status_code

    if status_code == 200:
        json_data = response.json()
        print(json_data)
        return json_data
    elif status_code == 429:
        print("Bad API response: 429. Retrying after half a second...")
        time.sleep(0.5)
        return None
    elif status_code == 500:
        err = "Image doesn't contain a car"
        if response.json()['error'] == err:
            print(err)
        else:
            print(f"Bad API response: {status_code}")
        return None
    else:
        print(f"Bad API response: {status_code}")
        return None


def rekognition_analyze_image(bucket, key):
    client = boto3.client('rekognition')
    return client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': key
            }
        },
        MaxLabels=10,
        MinConfidence=70
    )


def save_to_db(data, db_name):
    current_time = datetime.now().isoformat()

    record = {
        'id': {
            'S': str(uuid.uuid4())
        },
        'created': {
            'S': current_time
        },
        'updated': {
            'S': current_time
        },
        'data': {
            'S': json.dumps(data)
        }
    }

    try:
        dynamodb.put_item(TableName=db_name, Item=record)
    except ClientError as e:
        print(e.response['Error']['Message'])
        raise e
    return
