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

5.  [Integrating with Postgres](https://supabase.com/docs/guides/functions/connect-to-postgres)

# 

Connecting directly to Postgres

## 

Connecting to Postgres from Edge Functions.

* * *

Connect to your Postgres database from an Edge Function by using the `supabase-js` client. You can also use other Postgres clients like [Deno Postgres](https://deno.land/x/postgres)

## Using supabase-js[#](#using-supabase-js)

The `supabase-js` client is a great option for connecting to your Supabase database since it handles authorization with Row Level Security, and it automatically formats your response as JSON.

```
123456789101112131415161718192021222324import { createClient } from 'jsr:@supabase/supabase-js@2'Deno.serve(async (req) => {  try {    const supabase = createClient(      Deno.env.get('SUPABASE_URL') ?? '',      Deno.env.get('SUPABASE_ANON_KEY') ?? '',      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }    )    const { data, error } = await supabase.from('countries').select('*')    if (error) {      throw error    }    return new Response(JSON.stringify({ data }), {      headers: { 'Content-Type': 'application/json' },      status: 200,    })  } catch (err) {    return new Response(String(err?.message ?? err), { status: 500 })  }})
```

## Using a Postgres client[#](#using-a-postgres-client)

Because Edge Functions are a server-side technology, it's safe to connect directly to your database using any popular Postgres client. This means you can run raw SQL from your Edge Functions.

Here is how you can connect to the database using Deno Postgres driver and run raw SQL.

Check out the [full example](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/postgres-on-the-edge).

```
123456789101112131415161718192021222324252627282930313233343536373839import * as postgres from 'https://deno.land/x/postgres@v0.17.0/mod.ts'// Get the connection string from the environment variable "SUPABASE_DB_URL"const databaseUrl = Deno.env.get('SUPABASE_DB_URL')!// Create a database pool with three connections that are lazily establishedconst pool = new postgres.Pool(databaseUrl, 3, true)Deno.serve(async (_req) => {  try {    // Grab a connection from the pool    const connection = await pool.connect()    try {      // Run a query      const result = await connection.queryObject`SELECT * FROM animals`      const animals = result.rows // [{ id: 1, name: "Lion" }, ...]      // Encode the result as pretty printed JSON      const body = JSON.stringify(        animals,        (key, value) => (typeof value === 'bigint' ? value.toString() : value),        2      )      // Return the response with the correct content type header      return new Response(body, {        status: 200,        headers: { 'Content-Type': 'application/json; charset=utf-8' },      })    } finally {      // Release the connection back into the pool      connection.release()    }  } catch (err) {    console.error(err)    return new Response(String(err?.message ?? err), { status: 500 })  }})
```

## Using Drizzle[#](#using-drizzle)

You can use Drizzle together with [Postgres.js](https://github.com/porsager/postgres). Both can be loaded directly from npm:

```
1234567{  "imports": {    "drizzle-orm": "npm:drizzle-orm@0.29.1",    "drizzle-orm/": "npm:/drizzle-orm@0.29.1/",    "postgres": "npm:postgres@3.4.3"  }}
```

```
1234567891011121314import { drizzle } from 'drizzle-orm/postgres-js'import postgres from 'postgres'import { countries } from '../_shared/schema.ts'const connectionString = Deno.env.get('SUPABASE_DB_URL')!Deno.serve(async (_req) => {  // Disable prefetch as it is not supported for "Transaction" pool mode  const client = postgres(connectionString, { prepare: false })  const db = drizzle(client)  const allCountries = await db.select().from(countries)  return Response.json(allCountries)})
```

You can find the full example on [GitHub](https://github.com/thorwebdev/edgy-drizzle).

## SSL connections[#](#ssl-connections)

Deployed edge functions are pre-configured to use SSL for connections to the Supabase database. You don't need to add any extra configurations.

If you want to use SSL connections during local development, follow these steps:

-   Download the SSL certificate from [Database settings](https://supabase.com/dashboard/project/_/settings/database)
    
-   In your [local .env file](https://supabase.com/docs/guides/functions/secrets), add these two variables:
    

```
12SSL_CERT_FILE=/path/to/cert.crt # set the path to the downloaded certDENO_TLS_CA_STORE=mozilla,system
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/connect-to-postgres.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2Fcl7EuF1-RsY%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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