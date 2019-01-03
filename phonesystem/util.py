import boto3
import re
import tempfile

# s3://bucketname/key
_S3_PATTERN = re.compile('s3://([^/]+)/(.+)')


def get_file(file):
    filename = str(file)
    m = _S3_PATTERN.match(filename)
    if m:
        bucket = m.group(1)
        key = m.group(2)
        client = boto3.client('s3')
        tempf = tempfile.NamedTemporaryFile()
        filename = tempf.name
        client.download_file(bucket, key, filename)
    with open(filename, 'r') as f:
        return f.read()


def put_file(file, body):
    filename = str(file)
    m = _S3_PATTERN.match(filename)
    if m:
        bucket = m.group(1)
        key = m.group(2)
        client = boto3.client('s3')
        client.put_object(Body=body, Bucket=bucket, Key=key)
    else:
        with open(filename, 'w') as f:
            f.write(body)
            f.close()
