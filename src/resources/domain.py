import boto3
import cfnresponse
import time

d = boto3.client("route53domains")


def to_contact(p):
    return {"FirstName": p["firstName"], "LastName": p["lastName"],
            "ContactType": p.get("type", "PERSON"), "AddressLine1": p["addressLine1"],
            "City": p["city"], "State": p["state"], "CountryCode": p["countryCode"],
            "ZipCode": p["zipCode"], "PhoneNumber": p["phoneNumber"], "Email": p["email"]}


def wait(op_id):
    while True:
        status = d.get_operation_detail(OperationId=op_id)["Status"]
        if status == "SUCCESSFUL":
            return
        if status in ("ERROR", "FAILED"):
            raise Exception("operation %s: %s" % (op_id, status))
        time.sleep(15)


def handler(event, context):
    try:
        if event["RequestType"] == "Delete":
            cfnresponse.send(event, context, cfnresponse.SUCCESS, {},
                             physicalResourceId=event.get("PhysicalResourceId"))
            return
        p = event["ResourceProperties"]
        name = p["DomainName"]
        contact = to_contact(p["Contact"])
        ns = p.get("NameServers") or []
        auth = p.get("TransferAuthCode")
        auto = str(p.get("AutoRenew", "true")).lower() == "true"
        years = int(p.get("DurationInYears", 1))
        owned = name in [x["DomainName"] for x in d.list_domains()["Domains"]]
        detail = d.get_domain_detail(DomainName=name) if owned else None
        pending = (not owned) and any(
            o["Status"] == "IN_PROGRESS" and o["Type"] == "TRANSFER_IN_DOMAIN"
            and o["DomainName"] == name for o in d.list_operations()["Operations"])
        if detail is None and not pending:
            if event["RequestType"] == "Update":
                # No longer in the account (e.g. expired); don't re-register.
                cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, physicalResourceId=name)
                return
            if auth:
                d.transfer_domain(DomainName=name, AuthCode=auth, DurationInYears=years,
                    AutoRenew=auto, AdminContact=contact, RegistrantContact=contact,
                    TechContact=contact,
                    **({"Nameservers": [{"Name": n} for n in ns]} if ns else {}))
            else:
                op = d.register_domain(DomainName=name, DurationInYears=years, AutoRenew=auto,
                    AdminContact=contact, RegistrantContact=contact, TechContact=contact,
                    PrivacyProtectAdminContact=True, PrivacyProtectRegistrantContact=True,
                    PrivacyProtectTechContact=True)["OperationId"]
                wait(op)
                if ns:
                    d.update_domain_nameservers(DomainName=name,
                        Nameservers=[{"Name": n} for n in ns])
        elif detail is not None:
            roles = ("AdminContact", "RegistrantContact", "TechContact")
            if any(detail.get(r, {}).get(k) != v for r in roles for k, v in contact.items()):
                d.update_domain_contact(DomainName=name, AdminContact=contact,
                    RegistrantContact=contact, TechContact=contact)
            if auto != detail.get("AutoRenew", False):
                (d.enable_domain_auto_renew if auto else d.disable_domain_auto_renew)(DomainName=name)
            if ns and set(ns) != {n["Name"] for n in detail.get("Nameservers", [])}:
                d.update_domain_nameservers(DomainName=name,
                    Nameservers=[{"Name": n} for n in ns])
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, physicalResourceId=name)
    except Exception as e:
        print("Error:", e)
        cfnresponse.send(event, context, cfnresponse.FAILED, {"Error": str(e)})
