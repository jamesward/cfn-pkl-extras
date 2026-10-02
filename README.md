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
    uri = "package://pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras@0.1.6"
  }
}
```

## High-Level Template for Domains & DNS

> Register, transfer, and manage domains including DNS records and web redirects

[PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/template/)

```pkl
amends "@cfn-pkl-extras/template.pkl"

contact {
  firstName = "Joe"
  lastName = "Bob"
  type = "PERSON"
  addressLine1 = "PO Box 123"
  city = "Anywhere"
  state = "CA"
  countryCode = "US"
  zipCode = "93444"
  phoneNumber = "+1.3035551212"
  email = "joe@bob.com"
}

registeredDomains {
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

externalDomains {
  ["foo.dev"] {
    records {
      new {
        sub = "www"
        type = "CNAME"
        values {
          "foo.herokudns.com"
        }
      }
    }
    redirect {
      to = "https://www.foo.dev"
      preservePath = true
    }
  }
}
```

### Multiple Independent Redirects

`redirect` remains available for backwards compatibility. Use `redirects` to add independent hostname redirects under the same apex domain; each entry receives its own ACM certificate, CloudFront function, distribution, and DNS records.

```pkl
registeredDomains {
  ["example.com"] {
    redirect {
      to = "https://www.example.net"
      aliases { "www.example.com" }
    }
    redirects {
      new patterns.BasicRedirect {
        sub = "mcp"
        to = "https://mcp.example.net/server"
        // Subdomain redirects automatically use a CNAME, preserving an
        // existing CNAME logical resource during migration.
        preserveQuery = true
        preserveMethods = true
        pathMappings {
          new patterns.RedirectPathMapping {
            paths {
              "/.well-known/oauth-protected-resource"
              "/.well-known/oauth-protected-resource/"
            }
            to = "https://mcp.example.net/.well-known/oauth-protected-resource/server"
          }
        }
      }
    }
  }
}
```

POST uses 307/308 as before. Set `preserveMethods = true` to use 307/308 for every non-GET/HEAD method, preserving request methods and bodies.

## Lower-Level Abstractions

### Custom Resources

> Create CloudFormation Custom Resources backed by the published [cfn-extras-resource](https://github.com/jamesward/cfn-extras-resource) Lambda artifact

[CustomResource PklDoc](https://jamesward.github.io/cfn-pkl-extras/pkg.pkl-lang.org/github.com/jamesward/cfn-pkl-extras/cfn-pkl-extras/current/customResources/CustomResource.html)

Every custom resource uses the same public, versioned artifact from cfn-extras-resource (Lambda self-managed S3 storage, so there's nothing to build or upload). Each resource just picks its `handler`. The available handlers are listed in the [cfn-extras-resource README](https://github.com/jamesward/cfn-extras-resource#resources); for example `cfn_extras.domain.handler`, `cfn_extras.connection_lookup.handler`, `cfn_extras.hosted_zone.handler`, `cfn_extras.sdk_call.handler`, `cfn_extras.trigger_build.handler` and `cfn_extras.cleanup_bucket.handler`.

Example: the Domain resource. `route53.Domain` (below) wraps this for you.
```pkl
import "@cfn-pkl-extras/customResources.pkl"

local domainCustomResource = new customResources.CustomResource {
  resourceName = "Domain"
  handler = "cfn_extras.domain.handler"
  timeout = 600.s
  managedPolicyArns {
    "arn:aws:iam::aws:policy/AmazonRoute53DomainsFullAccess"
  }
}

// The Lambda and IAM role, then one CustomResource per instance
domainResources = domainCustomResource.resources
aDomain = domainCustomResource.instance(new Mapping {
  ["DomainName"] = "foo.com"
  ["AutoRenew"] = true
})
```

Example: call one AWS SDK method, like CDK's `AwsCustomResource`.
```pkl
import "@cfn-pkl-extras/customResources.pkl"

local sdkCall = customResources.sdkCall(new Listing {
  new customResources.Allow {
    actions { "ssm:GetParameter" }
    resource { "*" }
  }
})

sdkResources = sdkCall.resources
parameter = sdkCall.instance(new Mapping {
  ["Service"] = "ssm"
  ["Action"] = "get_parameter"
  ["Parameters"] = new Mapping { ["Name"] = "/my/parameter" }
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
