from flask import Flask, request
from app_service import AppService
import json
import boto3
import base64
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "arn:aws:secretsmanager:eu-west-1:207618842124:secret:k8s_test-d1idXZ"
    region_name = "eu-west-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.


    get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    # Your code goes here.
    db_clust_arn = 'arn:aws:rds:eu-west-1:207618842124:cluster:test'

    db_secret_arn = 'arn:aws:secretsmanager:eu-west-1:207618842124:secret:k8s_test-d1idXZ'

    rds_data = boto3.client('rds-data')

    response = rds_data.execute_statement(
	    resourceArn = db_clust_arn, 
	    secretArn = db_secret_arn, 
	    database = secret['host'],
	    sql = 'select * from tutorials',
	    parameters = {'username':secret['username'],'password':secret['password']}



    return response
app = Flask(__name__)
appService = AppService();


@app.route('/')
def home():
    msg = get_secret()
    return msg


@app.route('/api/tasks')
def tasks():
    return appService.get_tasks()


@app.route('/api/task', methods=['POST'])
def create_task():
    request_data = request.get_json()
    task = request_data['task']
    return appService.create_task(task)


@app.route('/api/task', methods=['PUT'])
def update_task():
    request_data = request.get_json()
    return appService.update_task(request_data['task'])


@app.route('/api/task/<int:id>', methods=['DELETE'])
def delete_task(id):
    return appService.delete_task(id)

# Use this code snippet in your app.
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/
