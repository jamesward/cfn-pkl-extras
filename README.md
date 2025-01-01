Pkl CloudFormation Extras
------------------

> Convenient abstractions over [cloudformation-pkl](https://github.com/aws-cloudformation/cloudformation-pkl)

[Check out the PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/index.html)

## Usage

Add the dependency to a `PklProject` file:
```pkl
amends "pkl:Project"

dependencies {
  ["cfn-pkl-extras"] {
    uri = "package://pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras@0.0.4"
  }
}
```

## High-Level Abstractions

### Pattern - Domains

> Register, transfer, and manage domains including DNS records and web redirects

[Domains PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/patterns/Domains.html)

```pkl
import "@cfn-pkl-extras/patterns.pkl"

local domains = new patterns.Domains {
  contact {
    // your contact details
  }

  domains {
    ["foo.com"] {
      records {
        new {
          type = "A"
          values {
            "192.168.0.1"
          }
        }
        new {
          sub = "www"
          type = "CNAME"
          values {
            "asite.com"
          }
        }
      }
    }

    ["bar.com"] {
      redirect {
        to = "https://coolsite.com"
        aliases {
          "www.bar.com"
        }
      }
    }
  }
}
```

Put the resources & outputs in a template with cloudformation-pkl:
```pkl
amends "@cfn/template.pkl"

Resources {
  ...domains.resources
}

Outputs {
  ...domains.outputs
}
```

### Pattern - DNS

> Manage DNS records

[DNS PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/patterns/DNS.html)

```pkl
import "@cfn-pkl-extras/patterns.pkl"

local dns = new patterns.DNS {
  domains {
    ["foo.dev"] {
      new {
        type = "A"
        values {
          "192.168.0.1"
        }
      }
    }
  }
}
```

Put the resources & outputs in a template with cloudformation-pkl:
```pkl
amends "@cfn/template.pkl"

Resources {
  ...dns.resources
}

Outputs {
  ...dns.outputs
}
```

## Lower-Level Abstractions

### Custom Resources

> Create CloudFormation Custom Resources from inline code or a GitHub repo

[CustomResource PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/customResources/CustomResource.html)

Inline Example:
```pkl
import "@cfn-pkl-extras/customResources.pkl"

myCustomResource = new customResources.CustomResource {
  resourceName = "MyCustomResource"
  source = new customResources.Code {
    runtime = "python3.9"
    handler = "index.handler"
    timeout = 900.s
    body = """
      import boto3
      import cfnresponse
      import time

      def handler(event, context):
        response_data = { }
        cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data)
      """
  }
  allow = new customResources.Allow {
    actions {
      // list of allow policy actions
    }
    resource {
      // list of resources to allow access to
    }
  }
  managedPolicyArns {
    // list of managed policy Arns
  }
}

// create instances of the Custom Resource
aResource = myCustomResource.instance(new Mapping {
  ["AProperty"] = "something"
})
```

Repo Example:
```pkl
import "@cfn-pkl-extras/customResources.pkl"
import "@cfn-pkl-extras/route53.pkl"

domainCustomResource = new customResources.CustomResource {
  resourceName = "Domain"
  source = new customResources.Repo {
    runtime = "python3.9"
    handler = "index.handler"
    timeout = 10.s
    gitHubOrgRepo = "jamesward/cfn-domain-resource"
    commit = "70e82a96b63a74bb302201e41365707beecaf0ae"
  }
  managedPolicyArns {
    "arn:aws:iam::aws:policy/AmazonRoute53DomainsFullAccess"
  }
}

// create instances of the Custom Resource
aDomain = domainCustomResource.instance(new Mapping {
  ["DomainName"] = "foo.com"
  ["Contact"] = new route53.Contact {
    // your contact properties
  }
  ["TransferAuthCode"] = "your_transfer_code"
  ["NameServers"] = new {
    // list of your name servers
  }
  ["AutoRenew"] = true
})
```

### Hosted Zones & Domain Records

[route53 PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/route53/index.html)

```pkl
amends "@cfn/template.pkl"
import "@cfn-pkl-extras/route53.pkl"

Resources {
  // Setup the required CustomResources
  ...route53.hostedZoneCustomResource.resources

  ...route53.hostedZone(new route53.DomainName {
    name = "foo.com"
  })

  ...route53.domainRecords("foo.com", new Listing<route53.DomainRecord> {
    new {
      sub = "www"
      type = "CNAME"
      values {
        "asdf.com"
      }
    }
  })
}
```

### Domains

> Register & transfer domain names

[route53 PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/route53/index.html)

```pkl
amends "@cfn/template.pkl"
import "@cfn-pkl-extras/route53.pkl"

Resources {
  // Setup the required CustomResources
  ...route53.domainCustomResource.resources

  ...new route53.Domain {
    domainName = new route53.DomainName { name = "foo.com" }
    contact {
      // your contact details
    }
  }.resources
}
```
