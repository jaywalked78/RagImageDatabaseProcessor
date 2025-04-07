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

Telemetry

1.  [Telemetry](https://supabase.com/docs/guides/telemetry)

3.  Logging & observability

5.  [Sentry integration](https://supabase.com/docs/guides/telemetry/sentry-monitoring)

# 

Sentry integration

## 

Integrate Sentry to monitor errors from a Supabase client

* * *

You can use [Sentry](https://sentry.io/welcome/) to monitor errors thrown from a Supabase JavaScript client. Install the [Supabase Sentry integration](https://github.com/supabase-community/sentry-integration-js) to get started.

The Sentry integration supports browser, Node, and edge environments.

## Installation[#](#installation)

Install the Sentry integration using your package manager:

npmyarnpnpm

```
1npm install @supabase/sentry-js-integration
```

## Use[#](#use)

If you are using Sentry JavaScript SDK v7, reference [`supabase-community/sentry-integration-js` repository](https://github.com/supabase-community/sentry-integration-js/blob/master/README-7v.md) instead.

To use the Supabase Sentry integration, add it to your `integrations` list when initializing your Sentry client.

You can supply either the Supabase Client constructor or an already-initiated instance of a Supabase Client.

With constructorWith instance

```
1234567891011121314import * as Sentry from '@sentry/browser'import { SupabaseClient } from '@supabase/supabase-js'import { supabaseIntegration } from '@supabase/sentry-js-integration'Sentry.init({  dsn: SENTRY_DSN,  integrations: [    supabaseIntegration(SupabaseClient, Sentry, {      tracing: true,      breadcrumbs: true,      errors: true,    }),  ],})
```

All available configuration options are available in our [`supabase-community/sentry-integration-js` repository](https://github.com/supabase-community/sentry-integration-js/blob/master/README.md#options).

## Deduplicating spans[#](#deduplicating-spans)

If you're already monitoring HTTP errors in Sentry, for example with the HTTP, Fetch, or Undici integrations, you will get duplicate spans for Supabase calls. You can deduplicate the spans by skipping them in your other integration:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445import * as Sentry from '@sentry/browser'import { SupabaseClient } from '@supabase/supabase-js'import { supabaseIntegration } from '@supabase/sentry-js-integration'Sentry.init({  dsn: SENTRY_DSN,  integrations: [    supabaseIntegration(SupabaseClient, Sentry, {      tracing: true,      breadcrumbs: true,      errors: true,    }),    // @sentry/browser    Sentry.browserTracingIntegration({      shouldCreateSpanForRequest: (url) => {        return !url.startsWith(`${SUPABASE_URL}/rest`)      },    }),    // or @sentry/node    Sentry.httpIntegration({      tracing: {        ignoreOutgoingRequests: (url) => {          return url.startsWith(`${SUPABASE_URL}/rest`)        },      },    }),    // or @sentry/node with Fetch support    Sentry.nativeNodeFetchIntegration({      ignoreOutgoingRequests: (url) => {        return url.startsWith(`${SUPABASE_URL}/rest`)      },    }),    // or @sentry/WinterCGFetch for Next.js Middleware & Edge Functions    Sentry.winterCGFetchIntegration({      breadcrumbs: true,      shouldCreateSpanForRequest: (url) => {        return !url.startsWith(`${SUPABASE_URL}/rest`)      },    }),  ],})
```

## Example Next.js configuration[#](#example-nextjs-configuration)

See this example for a setup with Next.js to cover browser, server, and edge environments. First, run through the [Sentry Next.js wizard](https://docs.sentry.io/platforms/javascript/guides/nextjs/#install) to generate the base Next.js configuration. Then add the Supabase Sentry Integration to all your `Sentry.init` calls with the appropriate filters.

BrowserServerMiddleware & EdgeInstrumentation

```
12345678910111213141516171819202122232425import * as Sentry from '@sentry/nextjs'import { SupabaseClient } from '@supabase/supabase-js'import { supabaseIntegration } from '@supabase/sentry-js-integration'Sentry.init({  dsn: SENTRY_DSN,  integrations: [    supabaseIntegration(SupabaseClient, Sentry, {      tracing: true,      breadcrumbs: true,      errors: true,    }),    Sentry.browserTracingIntegration({      shouldCreateSpanForRequest: (url) => {        return !url.startsWith(`${process.env.NEXT_PUBLIC_SUPABASE_URL}/rest`)      },    }),  ],  // Adjust this value in production, or use tracesSampler for greater control  tracesSampleRate: 1,  // Setting this option to true will print useful information to the console while you're setting up Sentry.  debug: true,})
```

Afterwards, build your application (`npm run build`) and start it locally (`npm run start`). You will now see the transactions being logged in the terminal when making supabase-js requests.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/telemetry/sentry-monitoring.mdx)

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