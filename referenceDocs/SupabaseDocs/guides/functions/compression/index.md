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

# 

Handling Compressed Requests

## 

Handling Gzip compressed requests.

* * *

To decompress Gzip bodies, you can use `gunzipSync` from the `node:zlib` API to decompress and then read the body.

```
123456789101112131415161718192021222324252627282930313233import { gunzipSync } from 'node:zlib'Deno.serve(async (req) => {  try {    // Check if the request body is gzip compressed    const contentEncoding = req.headers.get('content-encoding')    if (contentEncoding !== 'gzip') {      return new Response('Request body is not gzip compressed', {        status: 400,      })    }    // Read the compressed body    const compressedBody = await req.arrayBuffer()    // Decompress the body    const decompressedBody = gunzipSync(new Uint8Array(compressedBody))    // Convert the decompressed body to a string    const decompressedString = new TextDecoder().decode(decompressedBody)    const data = JSON.parse(decompressedString)    // Process the decompressed body as needed    console.log(`Received: ${JSON.stringify(data)}`)    return new Response('ok', {      headers: { 'Content-Type': 'text/plain' },    })  } catch (error) {    console.error('Error:', error)    return new Response('Error processing request', { status: 500 })  }})
```

Edge functions have a runtime memory limit of 150MB. Overly large compressed payloads may result in an out-of-memory error.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/compression.mdx)

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