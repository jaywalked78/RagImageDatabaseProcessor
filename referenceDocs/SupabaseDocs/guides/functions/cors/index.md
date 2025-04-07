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

3.  Examples

5.  [CORS support for invoking from the browser](https://supabase.com/docs/guides/functions/cors)

# 

CORS (Cross-Origin Resource Sharing) support for Invoking from the browser

* * *

To invoke edge functions from the browser, you need to handle [CORS Preflight](https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request) requests.

See the [example on GitHub](https://github.com/supabase/supabase/blob/master/examples/edge-functions/supabase/functions/browser-with-cors/index.ts).

### Recommended setup[#](#recommended-setup)

We recommend adding a `cors.ts` file within a [`_shared` folder](https://supabase.com/docs/guides/functions/quickstart#organizing-your-edge-functions) which makes it easy to reuse the CORS headers across functions:

```
1234export const corsHeaders = {  'Access-Control-Allow-Origin': '*',  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',}
```

You can then import and use the CORS headers within your functions:

```
123456789101112131415161718192021222324252627import { corsHeaders } from '../_shared/cors.ts'console.log(`Function "browser-with-cors" up and running!`)Deno.serve(async (req) => {  // This is needed if you're planning to invoke your function from a browser.  if (req.method === 'OPTIONS') {    return new Response('ok', { headers: corsHeaders })  }  try {    const { name } = await req.json()    const data = {      message: `Hello ${name}!`,    }    return new Response(JSON.stringify(data), {      headers: { ...corsHeaders, 'Content-Type': 'application/json' },      status: 200,    })  } catch (error) {    return new Response(JSON.stringify({ error: error.message }), {      headers: { ...corsHeaders, 'Content-Type': 'application/json' },      status: 400,    })  }})
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/cors.mdx)

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