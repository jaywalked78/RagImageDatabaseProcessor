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

3.  Third-Party Tools

5.  [Sending Emails with Resend](https://supabase.com/docs/guides/functions/examples/send-emails)

# 

Sending Emails

* * *

Sending emails from Edge Functions using the [Resend API](https://resend.com/).

### Prerequisites[#](#prerequisites)

To get the most out of this guide, you’ll need to:

-   [Create an API key](https://resend.com/api-keys)
-   [Verify your domain](https://resend.com/domains)

Make sure you have the latest version of the [Supabase CLI](https://supabase.com/docs/guides/cli#installation) installed.

### 1\. Create Supabase function[#](#1-create-supabase-function)

Create a new function locally:

```
1supabase functions new resend
```

Store the `RESEND_API_KEY` in your `.env` file.

### 2\. Edit the handler function[#](#2-edit-the-handler-function)

Paste the following code into the `index.ts` file:

```
12345678910111213141516171819202122232425262728const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')const handler = async (_request: Request): Promise<Response> => {  const res = await fetch('https://api.resend.com/emails', {    method: 'POST',    headers: {      'Content-Type': 'application/json',      Authorization: `Bearer ${RESEND_API_KEY}`,    },    body: JSON.stringify({      from: 'onboarding@resend.dev',      to: 'delivered@resend.dev',      subject: 'hello world',      html: '<strong>it works!</strong>',    }),  })  const data = await res.json()  return new Response(JSON.stringify(data), {    status: 200,    headers: {      'Content-Type': 'application/json',    },  })}Deno.serve(handler)
```

### 3\. Deploy and send email[#](#3-deploy-and-send-email)

Run function locally:

```
12supabase startsupabase functions serve --no-verify-jwt --env-file .env
```

Test it: [http://localhost:54321/functions/v1/resend](http://localhost:54321/functions/v1/resend)

Deploy function to Supabase:

```
1supabase functions deploy resend --no-verify-jwt
```

When you deploy to Supabase, make sure that your `RESEND_API_KEY` is set in [Edge Function Secrets Management](https://supabase.com/dashboard/project/_/settings/functions)

Open the endpoint URL to send an email:

### 4\. Try it yourself[#](#4-try-it-yourself)

Find the complete example on [GitHub](https://github.com/resendlabs/resend-supabase-edge-functions-example).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/send-emails.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FQf7XvL1fjvo%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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