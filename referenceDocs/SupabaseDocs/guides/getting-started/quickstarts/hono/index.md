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

Getting Started

1.  [Start with Supabase](https://supabase.com/docs/guides/getting-started)

3.  Framework Quickstarts

5.  [Hono](https://supabase.com/docs/guides/getting-started/quickstarts/hono)

# 

Use Supabase with Hono

## 

Learn how to create a Supabase project, add some sample data to your database, secure it with auth, and query the data from a Hono app.

* * *

1

### Create a Hono app

Bootstrap the Hono example app from the Supabase Samples using the CLI.

```
1npx supabase@latest bootstrap hono
```

2

### Install the Supabase client library

The `package.json` file in the project includes the necessary dependencies, including `@supabase/supabase-js` and `@supabase/ssr` to help with server-side auth.

```
1npm install
```

3

### Set up the required environment variables

Copy the `.env.example` file to `.env` and update the values with your Supabase project URL and anon key.

Lastly, [enable anonymous sign-ins](https://supabase.com/dashboard/project/_/settings/auth) in the Auth settings.

###### Project URL

Loading...

###### Anon key

Loading...

```
1cp .env.example .env
```

4

### Start the app

Start the app, go to [http://localhost:5173](http://localhost:5173).

Learn how [server side auth](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=hono) works with Hono.

```
1npm run dev
```

## Next steps[#](#next-steps)

-   Learn how [server side auth](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=hono) works with Hono.
-   [Insert more data](https://supabase.com/docs/guides/database/import-data) into your database
-   Upload and serve static files using [Storage](https://supabase.com/docs/guides/storage)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/hono.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)