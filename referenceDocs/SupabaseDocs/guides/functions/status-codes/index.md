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

5.  [Status codes](https://supabase.com/docs/guides/functions/status-codes)

# 

Status codes

## 

Edge Functions can return following status codes.

* * *

## 2XX Success[#](#2xx-success)

A successful Edge Function Response

## 3XX Redirect[#](#3xx-redirect)

The Edge Function has responded with a `Response.redirect` [API docs](https://developer.mozilla.org/en-US/docs/Web/API/Response/redirect_static)

## 4XX Client Errors[#](#4xx-client-errors)

### 401 Unauthorized[#](#401-unauthorized)

If the Edge Function has `Verify JWT` option enabled, but the request was made with an invalid JWT.

### 404 Not Found[#](#404-not-found)

Requested Edge Function was not found.

### 405 Method Not Allowed[#](#405-method-not-allowed)

Edge Functions only support these HTTP methods: 'POST', 'GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'

## 5XX Server Errors[#](#5xx-server-errors)

### 500 Internal Server Error[#](#500-internal-server-error)

Edge Function threw an uncaught exception (`WORKER_ERROR`). Check Edge Function logs to find the cause.

### 503 Service Unavailable[#](#503-service-unavailable)

Edge Function failed to start (`BOOT_ERROR`). Check Edge Function logs to find the cause.

### 504 Gateway Timeout[#](#504-gateway-timeout)

Edge Function didn't respond before the [request idle timeout](https://supabase.com/docs/guides/functions/limits).

### 546 Resource Limit (Custom Error Code)[#](#546-resource-limit-custom-error-code)

Edge Function execution was stopped due to a resource limit (`WORKER_LIMIT`). Edge Function logs should provide which [resource limit](https://supabase.com/docs/guides/functions/limits) was exceeded.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/status-codes.mdx)

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