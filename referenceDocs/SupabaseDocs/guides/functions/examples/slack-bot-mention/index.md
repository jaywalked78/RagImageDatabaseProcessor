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

5.  [Slack Bot responding to mentions](https://supabase.com/docs/guides/functions/examples/slack-bot-mention)

# 

Slack Bot Mention Edge Function

* * *

The Slack Bot Mention Edge Function allows you to process mentions in Slack and respond accordingly.

## Configuring Slack apps[#](#configuring-slack-apps)

For your bot to seamlessly interact with Slack, you'll need to configure Slack Apps:

1.  Navigate to the Slack Apps page.
2.  Under "Event Subscriptions," add the URL of the `slack-bot-mention` function and click to verify the URL.
3.  The Edge function will respond, confirming that everything is set up correctly.
4.  Add `app-mention` in the events the bot will subscribe to.

## Creating the Edge Function[#](#creating-the-edge-function)

Deploy the following code as an Edge function using the CLI:

```
12supabase --project-ref nacho_slacker secrets \set SLACK_TOKEN=<xoxb-0000000000-0000000000-01010101010nacho101010>
```

Here's the code of the Edge Function, you can change the response to handle the text received:

```
12345678910111213141516171819202122232425262728293031323334import { WebClient } from 'https://deno.land/x/slack_web_api@6.7.2/mod.js'const slackBotToken = Deno.env.get('SLACK_TOKEN') ?? ''const botClient = new WebClient(slackBotToken)console.log(`Slack URL verification function up and running!`)Deno.serve(async (req) => {  try {    const reqBody = await req.json()    console.log(JSON.stringify(reqBody, null, 2))    const { token, challenge, type, event } = reqBody    if (type == 'url_verification') {      return new Response(JSON.stringify({ challenge }), {        headers: { 'Content-Type': 'application/json' },        status: 200,      })    } else if (event.type == 'app_mention') {      const { user, text, channel, ts } = event      // Here you should process the text received and return a response:      const response = await botClient.chat.postMessage({        channel: channel,        text: `Hello <@${user}>!`,        thread_ts: ts,      })      return new Response('ok', { status: 200 })    }  } catch (error) {    return new Response(JSON.stringify({ error: error.message }), {      headers: { 'Content-Type': 'application/json' },      status: 500,    })  }})
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/slack-bot-mention.mdx)

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