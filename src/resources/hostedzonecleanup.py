import boto3
import cfnresponse

route53 = boto3.client("route53")


# On stack delete, empty the hosted zone of everything except the NS/SOA records
# so CloudFormation can then delete the AWS::Route53::HostedZone (Route 53 won't
# delete a zone that still has other records, e.g. an ACM validation CNAME).
def handler(event, context):
    try:
        if event["RequestType"] == "Delete":
            hosted_zone_id = event["ResourceProperties"]["HostedZoneId"]
            paginator = route53.get_paginator("list_resource_record_sets")
            for page in paginator.paginate(HostedZoneId=hosted_zone_id):
                for record in page["ResourceRecordSets"]:
                    if record["Type"] not in ("NS", "SOA"):
                        route53.change_resource_record_sets(
                            HostedZoneId=hosted_zone_id,
                            ChangeBatch={"Changes": [
                                {"Action": "DELETE", "ResourceRecordSet": record}
                            ]},
                        )
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                         physicalResourceId=event.get("PhysicalResourceId")
                         or event["LogicalResourceId"])
    except Exception as e:
        print("Error:", e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
