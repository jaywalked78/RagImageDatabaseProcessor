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

REST API

1.  [REST API](https://supabase.com/docs/guides/api)

3.  [Using the Data APIs](https://supabase.com/docs/guides/api/data-apis)

5.  [Using custom schemas](https://supabase.com/docs/guides/api/using-custom-schemas)

# 

Using Custom Schemas

* * *

By default, your database has a `public` schema which is automatically exposed on data APIs.

## Creating custom schemas[#](#creating-custom-schemas)

You can create your own custom schema/s by running the following SQL, substituting `myschema` with the name you want to use for your schema:

```
1CREATE SCHEMA myschema;
```

## Exposing custom schemas[#](#exposing-custom-schemas)

You can expose custom database schemas - to do so you need to follow these steps:

1.  Go to [API settings](https://supabase.com/dashboard/project/_/settings/api) and add your custom schema to "Exposed schemas".
2.  Run the following SQL, substituting `myschema` with your schema name:

```
1234567GRANT USAGE ON SCHEMA myschema TO anon, authenticated, service_role;GRANT ALL ON ALL TABLES IN SCHEMA myschema TO anon, authenticated, service_role;GRANT ALL ON ALL ROUTINES IN SCHEMA myschema TO anon, authenticated, service_role;GRANT ALL ON ALL SEQUENCES IN SCHEMA myschema TO anon, authenticated, service_role;ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA myschema GRANT ALL ON TABLES TO anon, authenticated, service_role;ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA myschema GRANT ALL ON ROUTINES TO anon, authenticated, service_role;ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA myschema GRANT ALL ON SEQUENCES TO anon, authenticated, service_role;
```

Now you can access these schemas from data APIs:

JavaScriptDartcURL

```
123456789// Initialize the JS clientimport { createClient } from '@supabase/supabase-js'const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, { db: { schema: 'myschema' } })// Make a requestconst { data: todos, error } = await supabase.from('todos').select('*')// You can also change the target schema on a per-query basisconst { data: todos, error } = await supabase.schema('myschema').from('todos').select('*')
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/api/using-custom-schemas.mdx)

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