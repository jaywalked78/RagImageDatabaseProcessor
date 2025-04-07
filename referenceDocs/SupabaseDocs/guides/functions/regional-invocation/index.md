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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Platform

5.  [Regional invocations](https://supabase.com/docs/guides/functions/regional-invocation)

# 

Regional Invocations

## 

How to execute an Edge Function in a particular region.

* * *

Edge Functions are executed in the region closest to the user making the request. This helps to reduce network latency and provide faster responses to the user.

However, if your Function performs lots of database or storage operations, invoking the Function in the same region as your database may provide better performance. Some situations where this might be helpful include:

-   Bulk adding and editing records in your database
-   Uploading files

Supabase provides an option to specify the region when invoking the Function.

## Using the `x-region` header[#](#using-the-x-region-header)

Use the `x-region` HTTP header when calling an Edge Function to determine where the Function should be executed:

cURLJavaScript

```
123456# https://supabase.com/docs/guides/functions/deploy#invoking-remote-functionscurl --request POST 'https://<project_ref>.supabase.co/functions/v1/hello-world' \  --header 'Authorization: Bearer ANON_KEY' \  --header 'Content-Type: application/json' \  --header 'x-region: eu-west-3' \  --data '{ "name":"Functions" }'
```

You can verify the execution region by looking at the `x-sb-edge-region` HTTP header in the response. You can also find it as metadata in [Edge Function Logs](https://supabase.com/docs/guides/functions/logging).

## Available regions[#](#available-regions)

These are the currently supported region values you can provide for `x-region` header.

-   `ap-northeast-1`
-   `ap-northeast-2`
-   `ap-south-1`
-   `ap-southeast-1`
-   `ap-southeast-2`
-   `ca-central-1`
-   `eu-central-1`
-   `eu-west-1`
-   `eu-west-2`
-   `eu-west-3`
-   `sa-east-1`
-   `us-east-1`
-   `us-west-1`
-   `us-west-2`

## Using the client library[#](#using-the-client-library)

You can also specify the region when invoking a Function using the Supabase client library:

```
1234567const { createClient, FunctionRegion } = require('@supabase/supabase-js')const { data: ret, error } = await supabase.functions.invoke('my-function-name', {  headers: { 'Content-Type': 'application/json' },  method: 'GET',  body: {},  region: FunctionRegion.UsEast1,})
```

## Handling regional outages[#](#handling-regional-outages)

If you explicitly specify the region via `x-region` header, requests **will NOT** be automatically re-routed to another region and you should consider temporarily changing regions during the outage.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/regional-invocation.mdx)

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