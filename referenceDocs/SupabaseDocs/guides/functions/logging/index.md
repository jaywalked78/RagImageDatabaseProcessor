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

3.  Debugging

5.  [Logging](https://supabase.com/docs/guides/functions/logging)

# 

Logging

## 

How to access logs for your Edge Functions.

* * *

Logs are provided for each function invocation, locally and in hosted environments.

## How to access logs[#](#how-to-access-logs)

### Hosted[#](#hosted)

You can access both tools from the [Functions section](https://supabase.com/dashboard/project/_/functions) of the Dashboard. Select your function from the list, and click `Invocations` or `Logs`:

-   **Invocations**: shows the Request and Response for each execution. You can see the headers, body, status code, and duration of each invocation. You can also filter the invocations by date, time, or status code.
-   **Logs**: shows any platform events, uncaught exceptions, and custom log events. You can see the timestamp, level, and message of each log event. You can also filter the log events by date, time, or level.

![Function invocations.](https://supabase.com/docs/img/guides/functions/function-logs.png)

### Local[#](#local)

When [developing locally](https://supabase.com/docs/guides/functions/local-development) you will see error messages and console log statements printed to your local terminal window.

## Events that get logged[#](#events-that-get-logged)

-   **Uncaught exceptions**: Uncaught exceptions thrown by a function during execution are automatically logged. You can see the error message and stack trace in the Logs tool.
-   **Custom log events**: You can use `console.log`, `console.error`, and `console.warn` in your code to emit custom log events. These events also appear in the Logs tool.
-   **Boot and Shutdown Logs**: The Logs tool extends its coverage to include logs for the boot and shutdown of functions.

A custom log message can contain up to 10,000 characters. A function can log up to 100 events within a 10 second period.

Here is an example of how to use custom logs events in your function:

```
1234567891011121314151617181920212223Deno.serve(async (req) => {  try {    const { name } = await req.json()    if (!name) {      console.warn('Empty name provided')    }    const data = {      message: `Hello ${name || 'Guest'}!`, // Provide a default value if name is empty    }    console.log(`Name: ${name}`)    return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } })  } catch (error) {    console.error(`Error processing request: ${error.message}`)    return new Response(JSON.stringify({ error: 'Internal Server Error' }), {      status: 500,      headers: { 'Content-Type': 'application/json' },    })  }})
```

## Logging tips[#](#logging-tips)

### Logging request headers[#](#logging-request-headers)

When debugging Edge Functions, a common mistake is to try to log headers to the developer console via code like this:

```
123456789101112Deno.serve(async (req) => {  const headers = JSON.stringify(req.headers)  console.log(`Request headers: ${headers}`)  // OR  console.log(`Request headers: ${JSON.stringify(req.headers)}`)  return new Response('ok', {    headers: {      'Content-Type': 'application/json',    },    status: 200,  })})
```

Both attempts will give as output the string `"{}"`, even though retrieving the value using `request.headers.get("Your-Header-Name")` will indeed give you the correct value. This behavior mirrors that of browsers.

The reason behind this behavior is that [Headers](https://developer.mozilla.org/en-US/docs/Web/API/Headers) objects don't store headers in JavaScript properties that can be enumerated. As a result, neither the developer console nor the JSON stringifier can properly interpret the names and values of the headers. Essentially, it's not an empty object, but rather an opaque one.

However, `Headers` objects are iterable. You can utilize this feature to craft a couple of succinct one-liners for debugging and printing headers.

### Convert headers into an object with `Object.fromEntries`:[#](#convert-headers-into-an-object-with-objectfromentries-)

You can use `Object.fromEntries` which is a call to convert the headers into an object:

```
1234567891011Deno.serve(async (req) => {  let headersObject = Object.fromEntries(req.headers)  let requestHeaders = JSON.stringify(headersObject, null, 2)  console.log(`Request headers: ${requestHeaders}`)  return new Response('ok', {    headers: {      'Content-Type': 'application/json',    },    status: 200,  })})
```

This results in something like:

```
12345678910111213141516171819Request headers: {    "accept": "*/*",    "accept-encoding": "gzip",    "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN1cGFuYWNobyIsInJvbGUiOiJhbm9uIiwieW91IjoidmVyeSBzbmVha3ksIGh1aD8iLCJpYXQiOjE2NTQ1NDA5MTYsImV4cCI6MTk3MDExNjkxNn0.cwBbk2tq-fUcKF1S0jVKkOAG2FIQSID7Jjvff5Do99Y",    "cdn-loop": "cloudflare; subreqs=1",    "cf-ew-via": "15",    "cf-ray": "8597a2fcc558a5d7-GRU",    "cf-visitor": "{\"scheme\":\"https\"}",    "cf-worker": "supabase.co",    "content-length": "20",    "content-type": "application/x-www-form-urlencoded",    "host": "edge-runtime.supabase.com",    "my-custom-header": "abcd",    "user-agent": "curl/8.4.0",    "x-deno-subhost": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsImtpZCI6InN1cGFiYXNlIn0.eyJkZXBsb3ltZW50X2lkIjoic3VwYW5hY2hvX2M1ZGQxMWFiLTFjYmUtNDA3NS1iNDAxLTY3ZTRlZGYxMjVjNV8wMDciLCJycGNfcm9vdCI6Imh0dHBzOi8vc3VwYWJhc2Utb3JpZ2luLmRlbm8uZGV2L3YwLyIsImV4cCI6MTcwODYxMDA4MiwiaWF0IjoxNzA4NjA5MTgyfQ.-fPid2kEeEM42QHxWeMxxv2lJHZRSkPL-EhSH0r_iV4",    "x-forwarded-host": "edge-runtime.supabase.com",    "x-forwarded-port": "443",    "x-forwarded-proto": "https"}
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/logging.mdx)

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