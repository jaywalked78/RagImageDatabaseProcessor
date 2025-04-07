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

AI & Vectors

1.  [AI & Vectors](https://supabase.com/docs/guides/ai)

3.  JavaScript Examples

5.  [OpenAI completions using Edge Functions](https://supabase.com/docs/guides/ai/examples/openai)

# 

Generating OpenAI GPT3 completions

## 

Generate GPT text completions using OpenAI and Supabase Edge Functions.

* * *

OpenAI provides a [completions API](https://platform.openai.com/docs/api-reference/completions) that allows you to use their generative GPT models in your own applications.

OpenAI's API is intended to be used from the server-side. Supabase offers Edge Functions to make it easy to interact with third party APIs like OpenAI.

## Setup Supabase project[#](#setup-supabase-project)

If you haven't already, [install the Supabase CLI](https://supabase.com/docs/guides/cli) and initialize your project:

```
1supabase init
```

## Create edge function[#](#create-edge-function)

Scaffold a new edge function called `openai` by running:

```
1supabase functions new openai
```

A new edge function will now exist under `./supabase/functions/openai/index.ts`.

We'll design the function to take your user's query (via POST request) and forward it to OpenAI's API.

```
1234567891011121314151617181920212223import OpenAI from 'https://deno.land/x/openai@v4.24.0/mod.ts'Deno.serve(async (req) => {  const { query } = await req.json()  const apiKey = Deno.env.get('OPENAI_API_KEY')  const openai = new OpenAI({    apiKey: apiKey,  })  // Documentation here: https://github.com/openai/openai-node  const chatCompletion = await openai.chat.completions.create({    messages: [{ role: 'user', content: query }],    // Choose model from here: https://platform.openai.com/docs/models    model: 'gpt-3.5-turbo',    stream: false,  })  const reply = chatCompletion.choices[0].message.content  return new Response(reply, {    headers: { 'Content-Type': 'text/plain' },  })})
```

Note that we are setting `stream` to `false` which will wait until the entire response is complete before returning. If you wish to stream GPT's response word-by-word back to your client, set `stream` to `true`.

## Create OpenAI key[#](#create-openai-key)

You may have noticed we were passing `OPENAI_API_KEY` in the Authorization header to OpenAI. To generate this key, go to [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys) and create a new secret key.

After getting the key, copy it into a new file called `.env.local` in your `./supabase` folder:

```
1OPENAI_API_KEY=your-key-here
```

## Run locally[#](#run-locally)

Serve the edge function locally by running:

```
1supabase functions serve --env-file ./supabase/.env.local --no-verify-jwt
```

Notice how we are passing in the `.env.local` file.

Use cURL or Postman to make a POST request to [http://localhost:54321/functions/v1/openai](http://localhost:54321/functions/v1/openai).

```
123curl -i --location --request POST http://localhost:54321/functions/v1/openai \  --header 'Content-Type: application/json' \  --data '{"query":"What is Supabase?"}'
```

You should see a GPT response come back from OpenAI!

## Deploy[#](#deploy)

Deploy your function to the cloud by running:

```
12supabase functions deploy --no-verify-jwt openaisupabase secrets set --env-file ./supabase/.env.local
```

## Go deeper[#](#go-deeper)

If you're interesting in learning how to use this to build your own ChatGPT, read [the blog post](https://supabase.com/blog/chatgpt-supabase-docs) and check out the video:

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/ai/examples/openai.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F29p8kIqyU_Y%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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