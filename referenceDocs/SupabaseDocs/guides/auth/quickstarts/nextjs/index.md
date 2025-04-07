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

Auth

1.  Auth

3.  Getting Started

5.  [Next.js](https://supabase.com/docs/guides/auth/quickstarts/nextjs)

# 

Use Supabase Auth with Next.js

## 

Learn how to configure Supabase Auth for the Next.js App Router.

* * *

1

### Create a new Supabase project

Head over to [database.new](https://database.new) and create a new Supabase project.

Your new database has a table for storing your users. You can see that this table is currently empty by running some SQL in the [SQL Editor](https://supabase.com/dashboard/project/_/sql/new).

```
1select * from auth.users;
```

2

### Create a Next.js app

Use the `create-next-app` command and the `with-supabase` template, to create a Next.js app pre-configured with:

-   [Cookie-based Auth](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)
-   [TypeScript](https://www.typescriptlang.org/)
-   [Tailwind CSS](https://tailwindcss.com/)

[See GitHub repo](https://github.com/vercel/next.js/tree/canary/examples/with-supabase)

```
1npx create-next-app -e with-supabase
```

3

### Declare Supabase Environment Variables

Rename `.env.local.example` to `.env.local` and populate with [your project's URL and Anon Key](https://supabase.com/dashboard/project/_/settings/api).

```
12NEXT_PUBLIC_SUPABASE_URL=your-project-url  NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

4

### Start the app

Start the development server, go to [http://localhost:3000](http://localhost:3000) in a browser, and you should see the contents of `app/page.tsx`.

To sign up a new user, navigate to [http://localhost:3000/sign-up](http://localhost:3000/sign-up), and click `Sign up`. _NOTE: .env.example must be renamed to .env.local before this route becomes available_

```
1npm run dev
```

## Learn more[#](#learn-more)

-   [Setting up Server-Side Auth for Next.js](https://supabase.com/docs/guides/auth/server-side/nextjs) for a Next.js deep dive
-   [Supabase Auth docs](https://supabase.com/docs/guides/auth#authentication) for more Supabase authentication methods

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/quickstarts/nextjs.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)