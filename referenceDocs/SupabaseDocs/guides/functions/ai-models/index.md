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

3.  Guides

5.  [Running AI Models](https://supabase.com/docs/guides/functions/ai-models)

# 

Running AI Models

## 

How to run AI models in Edge Functions.

* * *

[Supabase Edge Runtime](https://github.com/supabase/edge-runtime) has a built-in API for running AI models. You can use this API to generate embeddings, build conversational workflows, and do other AI related tasks in your Edge Functions.

## Setup[#](#setup)

There are no external dependencies or packages to install to enable the API.

You can create a new inference session by doing:

```
1const model = new Supabase.ai.Session('model-name')
```

To get type hints and checks for the API you can import types from `functions-js` at the top of your file:

```
1import 'jsr:@supabase/functions-js/edge-runtime.d.ts'
```

## Running a model inference[#](#running-a-model-inference)

Once the session is instantiated, you can call it with inputs to perform inferences. Depending on the model you run, you may need to provide different options (discussed below).

```
1const output = await model.run(input, options)
```

## How to generate text embeddings[#](#how-to-generate-text-embeddings)

Now let's see how to write an Edge Function using the `Supabase.ai` API to generate text embeddings. Currently, `Supabase.ai` API only supports the [gte-small](https://huggingface.co/Supabase/gte-small) model.

`gte-small` model exclusively caters to English texts, and any lengthy texts will be truncated to a maximum of 512 tokens. While you can provide inputs longer than 512 tokens, truncation may affect the accuracy.

```
12345678910111213const model = new Supabase.ai.Session('gte-small')Deno.serve(async (req: Request) => {  const params = new URL(req.url).searchParams  const input = params.get('input')  const output = await model.run(input, { mean_pool: true, normalize: true })  return new Response(JSON.stringify(output), {    headers: {      'Content-Type': 'application/json',      Connection: 'keep-alive',    },  })})
```

## Using Large Language Models (LLM)[#](#using-large-language-models-llm)

Inference via larger models is supported via [Ollama](https://ollama.com/) and [Mozilla Llamafile](https://github.com/Mozilla-Ocho/llamafile). In the first iteration, you can use it with a self-managed Ollama or [Llamafile server](https://www.docker.com/blog/a-quick-guide-to-containerizing-llamafile-with-docker-for-ai-applications/). We are progressively rolling out support for the hosted solution. To sign up for early access, fill up [this form](https://forms.supabase.com/supabase.ai-llm-early-access).

### Running locally[#](#running-locally)

OllamaMozilla Llamafile

[Install Ollama](https://github.com/ollama/ollama?tab=readme-ov-file#ollama) and pull the Mistral model

```
1ollama pull mistral
```

Run the Ollama server locally

```
1ollama serve
```

Set a function secret called AI\_INFERENCE\_API\_HOST to point to the Ollama server

```
1echo "AI_INFERENCE_API_HOST=http://host.docker.internal:11434" >> supabase/functions/.env
```

Create a new function with the following code

```
1supabase functions new ollama-test
```

```
12345678910111213141516171819202122232425262728293031323334353637import 'jsr:@supabase/functions-js/edge-runtime.d.ts'const session = new Supabase.ai.Session('mistral')Deno.serve(async (req: Request) => {  const params = new URL(req.url).searchParams  const prompt = params.get('prompt') ?? ''  // Get the output as a stream  const output = await session.run(prompt, { stream: true })  const headers = new Headers({    'Content-Type': 'text/event-stream',    Connection: 'keep-alive',  })  // Create a stream  const stream = new ReadableStream({    async start(controller) {      const encoder = new TextEncoder()      try {        for await (const chunk of output) {          controller.enqueue(encoder.encode(chunk.response ?? ''))        }      } catch (err) {        console.error('Stream error:', err)      } finally {        controller.close()      }    },  })  // Return the stream to the user  return new Response(stream, {    headers,  })})
```

Serve the function

```
1supabase functions serve --env-file supabase/functions/.env
```

Execute the function

```
123curl --get "http://localhost:54321/functions/v1/ollama-test" \--data-urlencode "prompt=write a short rap song about Supabase, the Postgres Developer platform, as sung by Nicki Minaj" \-H "Authorization: $ANON_KEY"
```

### Deploying to production[#](#deploying-to-production)

Once the function is working locally, it's time to deploy to production.

Deploy an Ollama or Llamafile server and set a function secret called `AI_INFERENCE_API_HOST` to point to the deployed server

```
1supabase secrets set AI_INFERENCE_API_HOST=https://path-to-your-llm-server/
```

Deploy the Supabase function

```
1supabase functions deploy
```

Execute the function

```
123curl --get "https://project-ref.supabase.co/functions/v1/ollama-test" \ --data-urlencode "prompt=write a short rap song about Supabase, the Postgres Developer platform, as sung by Nicki Minaj" \ -H "Authorization: $ANON_KEY"
```

As demonstrated in the video above, running Ollama locally is typically slower than running it in on a server with dedicated GPUs. We are collaborating with the Ollama team to improve local performance.

In the future, a hosted LLM API, will be provided as part of the Supabase platform. Supabase will scale and manage the API and GPUs for you. To sign up for early access, fill up [this form](https://forms.supabase.com/supabase.ai-llm-early-access).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/ai-models.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2Fw4Rr_1whU-U%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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