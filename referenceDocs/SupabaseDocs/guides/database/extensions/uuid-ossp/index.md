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

Database

1.  [Database](https://supabase.com/docs/guides/database/overview)

3.  Extensions

5.  [uuid-ossp: Unique Identifiers](https://supabase.com/docs/guides/database/extensions/uuid-ossp)

# 

uuid-ossp: Unique Identifiers

* * *

The `uuid-ossp` extension can be used to generate a `UUID`.

## Overview[#](#overview)

A `UUID` is a "Universally Unique Identifier" and it is, for practical purposes, unique. This makes them particularly well suited as Primary Keys. It is occasionally referred to as a `GUID`, which stands for "Globally Unique Identifier".

## Enable the extension[#](#enable-the-extension)

**Note**: Currently `uuid-ossp` extension is enabled by default and cannot be disabled.

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `uuid-ossp` and enable the extension.

## The `uuid` type[#](#the-uuid-type)

Once the extension is enabled, you now have access to a `uuid` type.

## `uuid_generate_v1()`[#](#uuidgeneratev1)

Creates a UUID value based on the combination of computer’s MAC address, current timestamp, and a random value.

UUIDv1 leaks identifiable details, which might make it unsuitable for certain security-sensitive applications.

## `uuid_generate_v4()`[#](#uuidgeneratev4)

Creates UUID values based solely on random numbers. You can also use Postgres's built-in [`gen_random_uuid()`](https://www.postgresql.org/docs/current/functions-uuid.html) function to generate a UUIDv4.

## Examples[#](#examples)

### Within a query[#](#within-a-query)

```
1select uuid_generate_v4();
```

### As a primary key[#](#as-a-primary-key)

Automatically create a unique, random ID in a table:

```
123456create table contacts (  id uuid default uuid_generate_v4(),  first_name text,  last_name text,  primary key (id));
```

## Resources[#](#resources)

-   [Choosing a Postgres Primary Key](https://supabase.com/blog/choosing-a-postgres-primary-key)
-   [The Basics Of Postgres `UUID` Data Type](https://www.postgresqltutorial.com/postgresql-uuid/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/uuid-ossp.mdx)

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