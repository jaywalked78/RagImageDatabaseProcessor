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

5.  [Speech Transcription with ElevenLabs](https://supabase.com/docs/guides/functions/examples/elevenlabs-transcribe-speech)

# 

Transcription Telegram Bot

## 

Build a Telegram bot that transcribes audio and video messages in 99 languages using TypeScript with Deno in Supabase Edge Functions.

* * *

## Introduction[#](#introduction)

In this tutorial you will learn how to build a Telegram bot that transcribes audio and video messages in 99 languages using TypeScript and the ElevenLabs Scribe model via the [speech to text API](https://elevenlabs.io/speech-to-text).

To check out what the end result will look like, you can test out the [t.me/ElevenLabsScribeBot](https://t.me/ElevenLabsScribeBot)

Find the [example project on GitHub](https://github.com/elevenlabs/elevenlabs-examples/tree/main/examples/speech-to-text/telegram-transcription-bot).

## Requirements[#](#requirements)

-   An ElevenLabs account with an [API key](https://supabase.com/app/settings/api-keys).
-   A [Supabase](https://supabase.com) account (you can sign up for a free account via [database.new](https://database.new)).
-   The [Supabase CLI](https://supabase.com/docs/guides/local-development) installed on your machine.
-   The [Deno runtime](https://docs.deno.com/runtime/getting_started/installation/) installed on your machine and optionally [setup in your favourite IDE](https://docs.deno.com/runtime/getting_started/setup_your_environment).
-   A [Telegram](https://telegram.org) account.

## Setup[#](#setup)

### Register a Telegram bot[#](#register-a-telegram-bot)

Use the [BotFather](https://t.me/BotFather) to create a new Telegram bot. Run the `/newbot` command and follow the instructions to create a new bot. At the end, you will receive your secret bot token. Note it down securely for the next step.

![BotFather](https://supabase.com/docs/img/guides/functions/elevenlabs/bot-father.png)

### Create a Supabase project locally[#](#create-a-supabase-project-locally)

After installing the [Supabase CLI](https://supabase.com/docs/guides/local-development), run the following command to create a new Supabase project locally:

```
1supabase init
```

### Create a database table to log the transcription results[#](#create-a-database-table-to-log-the-transcription-results)

Next, create a new database table to log the transcription results:

```
1supabase migrations new init
```

This will create a new migration file in the `supabase/migrations` directory. Open the file and add the following SQL:

```
1234567891011121314CREATE TABLE IF NOT EXISTS transcription_logs (  id BIGSERIAL PRIMARY KEY,  file_type VARCHAR NOT NULL,  duration INTEGER NOT NULL,  chat_id BIGINT NOT NULL,  message_id BIGINT NOT NULL,  username VARCHAR,  transcript TEXT,  language_code VARCHAR,  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,  error TEXT);ALTER TABLE transcription_logs ENABLE ROW LEVEL SECURITY;
```

### Create a Supabase Edge Function to handle Telegram webhook requests[#](#create-a-supabase-edge-function-to-handle-telegram-webhook-requests)

Next, create a new Edge Function to handle Telegram webhook requests:

```
1supabase functions new scribe-bot
```

If you're using VS Code or Cursor, select `y` when the CLI prompts "Generate VS Code settings for Deno? \[y/N\]"!

### Set up the environment variables[#](#set-up-the-environment-variables)

Within the `supabase/functions` directory, create a new `.env` file and add the following variables:

```
12345678# Find / create an API key at https://elevenlabs.io/app/settings/api-keysELEVENLABS_API_KEY=your_api_key# The bot token you received from the BotFather.TELEGRAM_BOT_TOKEN=your_bot_token# A random secret chosen by you to secure the function.FUNCTION_SECRET=random_secret
```

### Dependencies[#](#dependencies)

The project uses a couple of dependencies:

-   The open-source [grammY Framework](https://grammy.dev/) to handle the Telegram webhook requests.
-   The [@supabase/supabase-js](https://supabase.com/docs/reference/javascript) library to interact with the Supabase database.
-   The ElevenLabs [JavaScript SDK](https://supabase.com/docs/quickstart) to interact with the speech-to-text API.

Since Supabase Edge Function uses the [Deno runtime](https://deno.land/), you don't need to install the dependencies, rather you can [import](https://docs.deno.com/examples/npm/) them via the `npm:` prefix.

## Code the Telegram bot[#](#code-the-telegram-bot)

In your newly created `scribe-bot/index.ts` file, add the following code:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127128import { Bot, webhookCallback } from 'https://deno.land/x/grammy@v1.34.0/mod.ts'import 'jsr:@supabase/functions-js/edge-runtime.d.ts'import { createClient } from 'jsr:@supabase/supabase-js@2'import { ElevenLabsClient } from 'npm:elevenlabs@1.50.5'console.log(`Function "elevenlabs-scribe-bot" up and running!`)const elevenLabsClient = new ElevenLabsClient({  apiKey: Deno.env.get('ELEVENLABS_API_KEY') || '',})const supabase = createClient(  Deno.env.get('SUPABASE_URL') || '',  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || '')async function scribe({  fileURL,  fileType,  duration,  chatId,  messageId,  username,}: {  fileURL: string  fileType: string  duration: number  chatId: number  messageId: number  username: string}) {  let transcript: string | null = null  let languageCode: string | null = null  let errorMsg: string | null = null  try {    const sourceFileArrayBuffer = await fetch(fileURL).then((res) => res.arrayBuffer())    const sourceBlob = new Blob([sourceFileArrayBuffer], {      type: fileType,    })    const scribeResult = await elevenLabsClient.speechToText.convert({      file: sourceBlob,      model_id: 'scribe_v1',      tag_audio_events: false,    })    transcript = scribeResult.text    languageCode = scribeResult.language_code    // Reply to the user with the transcript    await bot.api.sendMessage(chatId, transcript, {      reply_parameters: { message_id: messageId },    })  } catch (error) {    errorMsg = error.message    console.log(errorMsg)    await bot.api.sendMessage(chatId, 'Sorry, there was an error. Please try again.', {      reply_parameters: { message_id: messageId },    })  }  // Write log to Supabase.  const logLine = {    file_type: fileType,    duration,    chat_id: chatId,    message_id: messageId,    username,    language_code: languageCode,    error: errorMsg,  }  console.log({ logLine })  await supabase.from('transcription_logs').insert({ ...logLine, transcript })}const telegramBotToken = Deno.env.get('TELEGRAM_BOT_TOKEN')const bot = new Bot(telegramBotToken || '')const startMessage = `Welcome to the ElevenLabs Scribe Bot\\! I can transcribe speech in 99 languages with super high accuracy\\!    \nTry it out by sending or forwarding me a voice message, video, or audio file\\!    \n[Learn more about Scribe](https://elevenlabs.io/speech-to-text) or [build your own bot](https://elevenlabs.io/docs/cookbooks/speech-to-text/telegram-bot)\\!  `bot.command('start', (ctx) => ctx.reply(startMessage.trim(), { parse_mode: 'MarkdownV2' }))bot.on([':voice', ':audio', ':video'], async (ctx) => {  try {    const file = await ctx.getFile()    const fileURL = `https://api.telegram.org/file/bot${telegramBotToken}/${file.file_path}`    const fileMeta = ctx.message?.video ?? ctx.message?.voice ?? ctx.message?.audio    if (!fileMeta) {      return ctx.reply('No video|audio|voice metadata found. Please try again.')    }    // Run the transcription in the background.    EdgeRuntime.waitUntil(      scribe({        fileURL,        fileType: fileMeta.mime_type!,        duration: fileMeta.duration,        chatId: ctx.chat.id,        messageId: ctx.message?.message_id!,        username: ctx.from?.username || '',      })    )    // Reply to the user immediately to let them know we received their file.    return ctx.reply('Received. Scribing...')  } catch (error) {    console.error(error)    return ctx.reply(      'Sorry, there was an error getting the file. Please try again with a smaller file!'    )  }})const handleUpdate = webhookCallback(bot, 'std/http')Deno.serve(async (req) => {  try {    const url = new URL(req.url)    if (url.searchParams.get('secret') !== Deno.env.get('FUNCTION_SECRET')) {      return new Response('not allowed', { status: 405 })    }    return await handleUpdate(req)  } catch (err) {    console.error(err)  }})
```

## Deploy to Supabase[#](#deploy-to-supabase)

If you haven't already, create a new Supabase account at [database.new](https://database.new) and link the local project to your Supabase account:

```
1supabase link
```

### Apply the database migrations[#](#apply-the-database-migrations)

Run the following command to apply the database migrations from the `supabase/migrations` directory:

```
1supabase db push
```

Navigate to the [table editor](https://supabase.com/dashboard/project/_/editor) in your Supabase dashboard and you should see and empty `transcription_logs` table.

![Empty table](https://supabase.com/docs/img/guides/functions/elevenlabs/supa-empty-table.png)

Lastly, run the following command to deploy the Edge Function:

```
1supabase functions deploy --no-verify-jwt scribe-bot
```

Navigate to the [Edge Functions view](https://supabase.com/dashboard/project/_/functions) in your Supabase dashboard and you should see the `scribe-bot` function deployed. Make a note of the function URL as you'll need it later, it should look something like `https://<project-ref>.functions.supabase.co/scribe-bot`.

![Edge Function deployed](https://supabase.com/docs/img/guides/functions/elevenlabs/supa-edge-function-deployed.png)

### Set up the webhook[#](#set-up-the-webhook)

Set your bot's webhook URL to `https://<PROJECT_REFERENCE>.functions.supabase.co/telegram-bot` (Replacing `<...>` with respective values). In order to do that, run a GET request to the following URL (in your browser, for example):

```
1https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook?url=https://<PROJECT_REFERENCE>.supabase.co/functions/v1/scribe-bot?secret=<FUNCTION_SECRET>
```

Note that the `FUNCTION_SECRET` is the secret you set in your `.env` file.

![Set webhook](https://supabase.com/docs/img/guides/functions/elevenlabs/set-webhook.png)

### Set the function secrets[#](#set-the-function-secrets)

Now that you have all your secrets set locally, you can run the following command to set the secrets in your Supabase project:

```
1supabase secrets set --env-file supabase/functions/.env
```

## Test the bot[#](#test-the-bot)

Finally you can test the bot by sending it a voice message, audio or video file.

![Test the bot](https://supabase.com/docs/img/guides/functions/elevenlabs/test-bot.png)

After you see the transcript as a reply, navigate back to your table editor in the Supabase dashboard and you should see a new row in your `transcription_logs` table.

![New row in table](https://supabase.com/docs/img/guides/functions/elevenlabs/supa-new-row.png)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/elevenlabs-transcribe-speech.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FCE4iPp7kd7Q%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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