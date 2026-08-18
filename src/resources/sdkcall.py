import boto3
import cfnresponse


# Flatten a nested response into dot-notation keys, e.g.
# {"A": {"B": "x"}} -> {"A.B": "x"}. CloudFormation custom-resource Fn::GetAtt
# does a flat key lookup (it can't traverse nested JSON), so the dot key becomes
# the attribute name: Fn::GetAtt [Resource, "A.B"].
def flatten(obj, prefix, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten(v, prefix + k + ".", out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            flatten(v, prefix + str(i) + ".", out)
    else:
        out[prefix[:-1]] = obj if isinstance(obj, str) else str(obj)


def dig(obj, path):
    for part in path.split("."):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def handler(event, context):
    try:
        if event["RequestType"] == "Delete":
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                             physicalResourceId=event.get("PhysicalResourceId"))
            return
        props = event["ResourceProperties"]
        client = boto3.client(props["Service"])
        response = getattr(client, props["Action"])(**props.get("Parameters", {}))
        response.pop("ResponseMetadata", None)
        data = {}
        flatten(response, "", data)
        id_path = props.get("PhysicalResourceIdPath")
        physical_id = dig(response, id_path) if id_path \
            else event.get("PhysicalResourceId") or event["LogicalResourceId"]
        cfnresponse.send(event, context, cfnresponse.SUCCESS, data,
                         physicalResourceId=str(physical_id))
    except Exception as e:
        print("Error:", e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
