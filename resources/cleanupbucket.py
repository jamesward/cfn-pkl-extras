import boto3
import cfnresponse

def handler(event, context):
    bucket_name = event['ResourceProperties']['BucketName']
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)

    try:
        if event['RequestType'] == 'Delete':
            # Delete all objects including versions
            bucket.object_versions.all().delete()
            bucket.objects.all().delete()

        cfnresponse.send(event, context, cfnresponse.SUCCESS, {})
    except Exception as e:
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
