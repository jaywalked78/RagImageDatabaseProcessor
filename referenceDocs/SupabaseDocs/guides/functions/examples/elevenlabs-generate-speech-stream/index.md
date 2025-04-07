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

5.  [Text To Speech with ElevenLabs](https://supabase.com/docs/guides/functions/examples/elevenlabs-generate-speech-stream)

# 

Streaming Speech with ElevenLabs

## 

Generate and stream speech through Supabase Edge Functions. Store speech in Supabase Storage and cache responses via built-in CDN.

* * *

## Introduction[#](#introduction)

In this tutorial you will learn how to build an edge API to generate, stream, store, and cache speech using Supabase Edge Functions, Supabase Storage, and [ElevenLabs text to speech API](https://elevenlabs.io/text-to-speech).

Find the [example project on GitHub](https://github.com/elevenlabs/elevenlabs-examples/tree/main/examples/text-to-speech/supabase/stream-and-cache-storage).

## Requirements[#](#requirements)

-   An ElevenLabs account with an [API key](https://supabase.com/app/settings/api-keys).
-   A [Supabase](https://supabase.com) account (you can sign up for a free account via [database.new](https://database.new)).
-   The [Supabase CLI](https://supabase.com/docs/guides/local-development) installed on your machine.
-   The [Deno runtime](https://docs.deno.com/runtime/getting_started/installation/) installed on your machine and optionally [setup in your favourite IDE](https://docs.deno.com/runtime/getting_started/setup_your_environment).

## Setup[#](#setup)

### Create a Supabase project locally[#](#create-a-supabase-project-locally)

After installing the [Supabase CLI](https://supabase.com/docs/guides/local-development), run the following command to create a new Supabase project locally:

```
1supabase init
```

### Configure the storage bucket[#](#configure-the-storage-bucket)

You can configure the Supabase CLI to automatically generate a storage bucket by adding this configuration in the `config.toml` file:

```
12345[storage.buckets.audio]public = falsefile_size_limit = "50MiB"allowed_mime_types = ["audio/mp3"]objects_path = "./audio"
```

Upon running `supabase start` this will create a new storage bucket in your local Supabase project. Should you want to push this to your hosted Supabase project, you can run `supabase seed buckets --linked`.

### Configure background tasks for Supabase Edge Functions[#](#configure-background-tasks-for-supabase-edge-functions)

To use background tasks in Supabase Edge Functions when developing locally, you need to add the following configuration in the `config.toml` file:

```
12[edge_runtime]policy = "per_worker"
```

When running with `per_worker` policy, Function won't auto-reload on edits. You will need to manually restart it by running `supabase functions serve`.

### Create a Supabase Edge Function for speech generation[#](#create-a-supabase-edge-function-for-speech-generation)

Create a new Edge Function by running the following command:

```
1supabase functions new text-to-speech
```

If you're using VS Code or Cursor, select `y` when the CLI prompts "Generate VS Code settings for Deno? \[y/N\]"!

### Set up the environment variables[#](#set-up-the-environment-variables)

Within the `supabase/functions` directory, create a new `.env` file and add the following variables:

```
12# Find / create an API key at https://elevenlabs.io/app/settings/api-keysELEVENLABS_API_KEY=your_api_key
```

### Dependencies[#](#dependencies)

The project uses a couple of dependencies:

-   The [@supabase/supabase-js](https://supabase.com/docs/reference/javascript) library to interact with the Supabase database.
-   The ElevenLabs [JavaScript SDK](https://supabase.com/docs/quickstart) to interact with the text-to-speech API.
-   The open-source [object-hash](https://www.npmjs.com/package/object-hash) to generate a hash from the request parameters.

Since Supabase Edge Function uses the [Deno runtime](https://deno.land/), you don't need to install the dependencies, rather you can [import](https://docs.deno.com/examples/npm/) them via the `npm:` prefix.

## Code the Supabase Edge Function[#](#code-the-supabase-edge-function)

In your newly created `supabase/functions/text-to-speech/index.ts` file, add the following code:

```
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455565758596061626364656667686970717273747576777879808182838485868788899091// Setup type definitions for built-in Supabase Runtime APIsimport 'jsr:@supabase/functions-js/edge-runtime.d.ts'import { createClient } from 'jsr:@supabase/supabase-js@2'import { ElevenLabsClient } from 'npm:elevenlabs@1.52.0'import * as hash from 'npm:object-hash'const supabase = createClient(  Deno.env.get('SUPABASE_URL')!,  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!)const client = new ElevenLabsClient({  apiKey: Deno.env.get('ELEVENLABS_API_KEY'),})// Upload audio to Supabase Storage in a background taskasync function uploadAudioToStorage(stream: ReadableStream, requestHash: string) {  const { data, error } = await supabase.storage    .from('audio')    .upload(`${requestHash}.mp3`, stream, {      contentType: 'audio/mp3',    })  console.log('Storage upload result', { data, error })}Deno.serve(async (req) => {  // To secure your function for production, you can for example validate the request origin,  // or append a user access token and validate it with Supabase Auth.  console.log('Request origin', req.headers.get('host'))  const url = new URL(req.url)  const params = new URLSearchParams(url.search)  const text = params.get('text')  const voiceId = params.get('voiceId') ?? 'JBFqnCBsd6RMkjVDRZzb'  const requestHash = hash.MD5({ text, voiceId })  console.log('Request hash', requestHash)  // Check storage for existing audio file  const { data } = await supabase.storage.from('audio').createSignedUrl(`${requestHash}.mp3`, 60)  if (data) {    console.log('Audio file found in storage', data)    const storageRes = await fetch(data.signedUrl)    if (storageRes.ok) return storageRes  }  if (!text) {    return new Response(JSON.stringify({ error: 'Text parameter is required' }), {      status: 400,      headers: { 'Content-Type': 'application/json' },    })  }  try {    console.log('ElevenLabs API call')    const response = await client.textToSpeech.convertAsStream(voiceId, {      output_format: 'mp3_44100_128',      model_id: 'eleven_multilingual_v2',      text,    })    const stream = new ReadableStream({      async start(controller) {        for await (const chunk of response) {          controller.enqueue(chunk)        }        controller.close()      },    })    // Branch stream to Supabase Storage    const [browserStream, storageStream] = stream.tee()    // Upload to Supabase Storage in the background    EdgeRuntime.waitUntil(uploadAudioToStorage(storageStream, requestHash))    // Return the streaming response immediately    return new Response(browserStream, {      headers: {        'Content-Type': 'audio/mpeg',      },    })  } catch (error) {    console.log('error', { error })    return new Response(JSON.stringify({ error: error.message }), {      status: 500,      headers: { 'Content-Type': 'application/json' },    })  }})
```

## Run locally[#](#run-locally)

To run the function locally, run the following commands:

```
1supabase start
```

Once the local Supabase stack is up and running, run the following command to start the function and observe the logs:

```
1supabase functions serve
```

### Try it out[#](#try-it-out)

Navigate to `http://127.0.0.1:54321/functions/v1/text-to-speech?text=hello%20world` to hear the function in action.

Afterwards, navigate to `http://127.0.0.1:54323/project/default/storage/buckets/audio` to see the audio file in your local Supabase Storage bucket.

## Deploy to Supabase[#](#deploy-to-supabase)

If you haven't already, create a new Supabase account at [database.new](https://database.new) and link the local project to your Supabase account:

```
1supabase link
```

Once done, run the following command to deploy the function:

```
1supabase functions deploy
```

### Set the function secrets[#](#set-the-function-secrets)

Now that you have all your secrets set locally, you can run the following command to set the secrets in your Supabase project:

```
1supabase secrets set --env-file supabase/functions/.env
```

## Test the function[#](#test-the-function)

The function is designed in a way that it can be used directly as a source for an `<audio>` element.

```
1234<audio  src="https://${SUPABASE_PROJECT_REF}.supabase.co/functions/v1/text-to-speech?text=Hello%2C%20world!&voiceId=JBFqnCBsd6RMkjVDRZzb"  controls/>
```

You can find an example frontend implementation in the complete code example on [GitHub](https://github.com/elevenlabs/elevenlabs-examples/tree/main/examples/text-to-speech/supabase/stream-and-cache-storage/src/pages/Index.tsx).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/elevenlabs-generate-speech-stream.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F4Roog4PAmZ8%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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