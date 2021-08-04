import os
import boto3
import botocore

def _generate_client_ressource():
    S3_API_KEY_ID = os.environ['S3_API_KEY_ID']
    S3_API_ACCESS_KEY = os.environ['S3_API_ACCESS_KEY']

    try:
        S3_URL_ENDPOINT = os.environ['S3_URL_ENDPOINT'] 
        S3_URL_ENDPOINT = str(S3_URL_ENDPOINT)
    except:
        S3_URL_ENDPOINT = ""
    
    if S3_URL_ENDPOINT == "":
        # AWS S3
        s3_client = boto3.client("s3", aws_access_key_id  = S3_API_KEY_ID, aws_secret_access_key  = S3_API_ACCESS_KEY)
        s3_ressource = boto3.resource( 's3', aws_access_key_id  = S3_API_KEY_ID, aws_secret_access_key  = S3_API_ACCESS_KEY)
    else:
        # Using custom S3 service !
        s3_client = boto3.client("s3", endpoint_url = S3_URL_ENDPOINT, aws_access_key_id  = S3_API_KEY_ID, aws_secret_access_key  = S3_API_ACCESS_KEY)
        s3_ressource = boto3.resource( 's3', endpoint_url = S3_URL_ENDPOINT, aws_access_key_id  = S3_API_KEY_ID, aws_secret_access_key  = S3_API_ACCESS_KEY)

    return s3_client, s3_ressource


def push_string_s3_file(string_to_push, file_key):
    S3_BUCKET = os.environ['S3_BUCKET']
    s3_client, s3_ressource = _generate_client_ressource()
    s3_client.put_object(Body=string_to_push, Bucket=S3_BUCKET, Key=file_key)
    return

def does_key_exists(file_key):
    S3_BUCKET = os.environ['S3_BUCKET']
    s3_client, s3_ressource = _generate_client_ressource()
    try:
        s3_ressource.Object(S3_BUCKET, file_key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            # Something else has gone wrong.
            return False
    else:
        return True


def get_content(file_key):
    S3_BUCKET = os.environ['S3_BUCKET']
    s3_client, s3_ressource = _generate_client_ressource()
    try:
        return s3_client.get_object(Bucket=S3_BUCKET, Key=file_key)['Body'].read().decode()
    except:
        return None
		

def delete_key(file_key):
    S3_BUCKET = os.environ['S3_BUCKET']
    s3_client, s3_ressource = _generate_client_ressource()
    try:
        s3_ressource.Object(S3_BUCKET, file_key).delete()
        return True
    except:
        return False

def list_files_prefix(prefix, extract_date = False):
    res = []
    s3_client, s3_ressource = _generate_client_ressource()
    iterator_s3 = s3_client.list_objects_v2(Bucket = os.environ['S3_BUCKET'], Prefix = prefix)

    if 'Contents' in iterator_s3:
        for key_i in iterator_s3['Contents']:
            if (extract_date):
                node = {}
                node['created_at'] = key_i['LastModified']
                node['path'] = key_i['Key']
                res.append(node)
            else:
                res.append(key_i['Key'])

    return res
