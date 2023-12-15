import logging
import boto3
from botocore.exceptions import ClientError
import os

s3_client = boto3.client('s3')

def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def list_files(bucket_name):
    files = []
    for fileObk in s3_client.list_objects(Bucket=bucket_name)['Contents']:
        if 'archive' not in fileObk["Key"]:
            files.append(fileObk["Key"])
    return files    