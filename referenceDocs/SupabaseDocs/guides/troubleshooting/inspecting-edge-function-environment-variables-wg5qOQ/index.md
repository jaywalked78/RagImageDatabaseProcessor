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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Inspecting edge function environment variables

Last edited: 2/4/2025

* * *

Sometimes it can be informative to log values from your Edge Functions. This walks you through the process of logging environment variables for inspection, but it can be generalized for all logging.

**Steps:**

1.  enable docker
    
2.  Create a local Supabase project
    

```
1npx supabase init
```

3.  create a .env file in the `supabase` folder

```
1echo "MY_NAME=Some_name" >> ./supabase/.env
```

4.  deploy the newly added secret

```
1npx supabase secrets set --env-file ./supabase/.env --project-ref <PROJECT REF>
```

5.  Run the following CLI command to check secrets:

```
1npx supabase secrets list
```

For security reasons, it is not advised to log secrets, but you can log a truncated version just for the reassurance that they're being updated:

```
1234567891011121314151617//logs the function call and the secretsconsole.log('Hello from Functions!')//custom secretconsole.log('logging custom secret', Deno.env.get('MY_NAME'))// default secretsconsole.log('logging SUPABASE_URL:', Deno.env.get('SUPABASE_URL').slice(0, 15))Deno.serve(async (req) => {  const { name } = await req.json()  const data = {    message: `Hello ${name}!`,  }  return new Response(JSON.stringify(data), { headers: { 'Content-Type': 'application/json' } })})
```

After calling your function, you can check your [edge function logs](https://supabase.com/dashboard/project/_/functions/hello-world/logs?s=logging) to observe the logged values. It should look something like this:

> Note: search filters are case sensitive and must be present in the event message.

![image](https://supabase.com/docs/img/troubleshooting/a360b417-e0cc-4706-8df4-89af63dcdc70.png)

> Note: excessively long JSON logs may be truncated. If this occurs, use the [JSON.stringify()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify) function to convert the JSON object into text. You can then copy and paste the log into a [JSON beautifier.](https://jsonformatter.org/)

## Metadata

* * *

### Products

[Functions](https://supabase.com/docs/guides/troubleshooting?products=functions)[Cli](https://supabase.com/docs/guides/troubleshooting?products=cli)

* * *

### Tags

[logging](https://supabase.com/docs/guides/troubleshooting?tags=logging)[environment](https://supabase.com/docs/guides/troubleshooting?tags=environment)[variables](https://supabase.com/docs/guides/troubleshooting?tags=variables)[secrets](https://supabase.com/docs/guides/troubleshooting?tags=secrets)[docker](https://supabase.com/docs/guides/troubleshooting?tags=docker)

* * *

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