[![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-dark.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-light.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)DOCS](https://supabase.com/docs)

-   [Start](https://supabase.com/docs/guides/getting-started)
-   Products
-   Build
-   Manage
-   Reference
-   Resources

[![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-dark.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)![Supabase wordmark](https://supabase.com/docs/_next/image?url=%2Fdocs%2Fsupabase-light.svg&w=256&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)DOCS](https://supabase.com/docs)

Search docs...

K

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# HTTP status codes

Last edited: 2/3/2025

* * *

The Supabase platform offers several HTTP APIs for each project. These APIs can use the status codes to indicate the state of the project, and the request being processed. The status codes returned for requests can be access via the [logs explorer](https://supabase.com/docs/guides/platform/logs#logs-explorer).

## 2XX success[#](#2xx-success)

2XX status codes indicate that the request was processed successfully.

## 3XX redirects[#](#3xx-redirects)

3XX status codes indicate that the client must initiate another course of action to have the request processed successfully. The most popular usage of 3XX codes is to redirect the client to a different location.

## 4XX client errors[#](#4xx-client-errors)

4XX status codes indicate an issue on the client's end with the request being made. These could include missing or invalid auth information, a malformed request, making too many requests in too short a time period ("rate limiting"), or a network issue on the client's end.

### 402 service restriction[#](#402-service-restriction)

In case the Fair Use Policy is applied, the projects of your organization may be restricted from processing requests. If service restrictions are applied, projects will return a 402 status code together with a description of why the project is restricted. The description can contain one or more of the following codes:

-   `exceeded_*` indicates that the project has continued to exceeded the usage limits of its quota, e.g. `exceed_egress_quota`, `exceed_db_size_quota`.
-   `overdue_payment` indicates that the organization has overdue bills.

You will still have access to your data through the Supabase dashboard when the Fair Use Policy is applied.

See the [Fair Use Policy](https://supabase.com/docs/guides/platform/billing-faq#fair-use-policy) section to learn more about the restrictions and how to remove them.

## 5XX server or project errors[#](#5xx-server-or-project-errors)

5XX status codes indicate that the project was unable to process the request successfully, but not because of an issue with the client's request.

5XX status codes can be the result of the project not having enough [compute](https://supabase.com/docs/guides/platform/compute-add-ons) to process a complex request being made by a client or not being able to keep up with the volume of requests made against the project.

### 54X project errors[#](#54x-project-errors)

54X status codes are custom codes used by the Supabase platform to indicate the state of the project.

#### 540 project paused[#](#540-project-paused)

The project the request was being made against has been paused. The project cannot process requests until it is un-paused by the owner.

Free Plan projects may be paused due to inactivity, on request by the owner, or in rare instances, due to abuse.

#### 544 project API gateway timeout[#](#544-project-api-gateway-timeout)

The request is not completed within the configured time limit.

The timeout limit is set to prevent long-running queries which can cause performance issues, increase latency, and potentially even crash the project.

#### 546 Edge Functions resource limit[#](#546-edge-functions-resource-limit)

Applies only to Edge Functions. Function execution was stopped due to a resource limit (`WORKER_LIMIT`). Edge Function logs should provide which [resource limit](https://supabase.com/docs/guides/functions/limits) was exceeded.

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Related error codes

[402](https://supabase.com/docs/guides/troubleshooting?errorCodes=402)[540](https://supabase.com/docs/guides/troubleshooting?errorCodes=540)[544](https://supabase.com/docs/guides/troubleshooting?errorCodes=544)[546](https://supabase.com/docs/guides/troubleshooting?errorCodes=546)

* * *

### Tags

[HTTP](https://supabase.com/docs/guides/troubleshooting?tags=HTTP)

* * *

### Is this helpful?

No Yes

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)