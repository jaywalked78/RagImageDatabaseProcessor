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

5.  [Upstash Redis](https://supabase.com/docs/guides/functions/examples/upstash-redis)

# 

Upstash Redis

* * *

A Redis counter example that stores a [hash](https://redis.io/commands/hincrby/) of function invocation count per region. Find the code on [GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions/supabase/functions/upstash-redis-counter).

## Redis database setup[#](#redis-database-setup)

Create a Redis database using the [Upstash Console](https://console.upstash.com/) or [Upstash CLI](https://github.com/upstash/cli).

Select the `Global` type to minimize the latency from all edge locations. Copy the `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` to your .env file.

You'll find them under **Details > REST API > .env**.

```
1cp supabase/functions/upstash-redis-counter/.env.example supabase/functions/upstash-redis-counter/.env
```

## Code[#](#code)

Make sure you have the latest version of the [Supabase CLI installed](https://supabase.com/docs/guides/cli#installation).

Create a new function in your project:

```
1supabase functions new upstash-redis-counter
```

And add the code to the `index.ts` file:

```
12345678910111213141516171819202122232425262728293031323334import { Redis } from 'https://deno.land/x/upstash_redis@v1.19.3/mod.ts'console.log(`Function "upstash-redis-counter" up and running!`)Deno.serve(async (_req) => {  try {    const redis = new Redis({      url: Deno.env.get('UPSTASH_REDIS_REST_URL')!,      token: Deno.env.get('UPSTASH_REDIS_REST_TOKEN')!,    })    const deno_region = Deno.env.get('DENO_REGION')    if (deno_region) {      // Increment region counter      await redis.hincrby('supa-edge-counter', deno_region, 1)    } else {      // Increment localhost counter      await redis.hincrby('supa-edge-counter', 'localhost', 1)    }    // Get all values    const counterHash: Record<string, number> | null = await redis.hgetall('supa-edge-counter')    const counters = Object.entries(counterHash!)      .sort(([, a], [, b]) => b - a) // sort desc      .reduce((r, [k, v]) => ({ total: r.total + v, regions: { ...r.regions, [k]: v } }), {        total: 0,        regions: {},      })    return new Response(JSON.stringify({ counters }), { status: 200 })  } catch (error) {    return new Response(JSON.stringify({ error: error.message }), { status: 200 })  }})
```

## Run locally[#](#run-locally)

```
12supabase startsupabase functions serve --no-verify-jwt --env-file supabase/functions/upstash-redis-counter/.env
```

Navigate to [http://localhost:54321/functions/v1/upstash-redis-counter](http://localhost:54321/functions/v1/upstash-redis-counter).

## Deploy[#](#deploy)

```
12supabase functions deploy upstash-redis-counter --no-verify-jwtsupabase secrets set --env-file supabase/functions/upstash-redis-counter/.env
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/upstash-redis.mdx)

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