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

5.  [CAPTCHA support with Cloudflare Turnstile](https://supabase.com/docs/guides/functions/examples/cloudflare-turnstile)

# 

CAPTCHA support with Cloudflare Turnstile

* * *

[Cloudflare Turnstile](https://www.cloudflare.com/products/turnstile/) is a friendly, free CAPTCHA replacement, and it works seamlessly with Supabase Edge Functions to protect your forms. [View on GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/cloudflare-turnstile).

## Setup[#](#setup)

-   Follow these steps to set up a new site: [https://developers.cloudflare.com/turnstile/get-started/](https://developers.cloudflare.com/turnstile/get-started/)
-   Add the Cloudflare Turnstile widget to your site: [https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/](https://developers.cloudflare.com/turnstile/get-started/client-side-rendering/)

## Code[#](#code)

Create a new function in your project:

```
1supabase functions new cloudflare-turnstile
```

And add the code to the `index.ts` file:

```
1234567891011121314151617181920212223242526272829303132333435363738import { corsHeaders } from '../_shared/cors.ts'console.log('Hello from Cloudflare Trunstile!')function ips(req: Request) {  return req.headers.get('x-forwarded-for')?.split(/\s*,\s*/)}Deno.serve(async (req) => {  // This is needed if you're planning to invoke your function from a browser.  if (req.method === 'OPTIONS') {    return new Response('ok', { headers: corsHeaders })  }  const { token } = await req.json()  const clientIps = ips(req) || ['']  const ip = clientIps[0]  // Validate the token by calling the  // "/siteverify" API endpoint.  let formData = new FormData()  formData.append('secret', Deno.env.get('CLOUDFLARE_SECRET_KEY') ?? '')  formData.append('response', token)  formData.append('remoteip', ip)  const url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'  const result = await fetch(url, {    body: formData,    method: 'POST',  })  const outcome = await result.json()  console.log(outcome)  if (outcome.success) {    return new Response('success', { headers: corsHeaders })  }  return new Response('failure', { headers: corsHeaders })})
```

## Deploy the server-side validation Edge Functions[#](#deploy-the-server-side-validation-edge-functions)

-   [https://developers.cloudflare.com/turnstile/get-started/server-side-validation/](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/)

```
12supabase functions deploy cloudflare-turnstilesupabase secrets set CLOUDFLARE_SECRET_KEY=your_secret_key
```

## Invoke the function from your site[#](#invoke-the-function-from-your-site)

```
123const { data, error } = await supabase.functions.invoke('cloudflare-turnstile', {  body: { token },})
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/cloudflare-turnstile.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FOwW0znboh60%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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