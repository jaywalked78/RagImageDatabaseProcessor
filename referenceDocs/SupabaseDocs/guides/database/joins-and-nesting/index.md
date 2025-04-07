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

3.  Working with your database (basics)

5.  [Querying joins and nested tables](https://supabase.com/docs/guides/database/joins-and-nesting)

# 

Querying Joins and Nested tables

* * *

The data APIs automatically detect relationships between Postgres tables. Since Postgres is a relational database, this is a very common scenario.

## One-to-many joins[#](#one-to-many-joins)

Let's use an example database that stores `orchestral_sections` and `instruments`:

TablesSQL

**Orchestral sections**

| `id` | `name` |
| --- | --- |
| 1 | strings |
| 2 | woodwinds |

**Instruments**

| `id` | `name` | `section_id` |
| --- | --- | --- |
| 1 | violin | 1 |
| 2 | viola | 1 |
| 3 | flute | 2 |
| 4 | oboe | 2 |

The APIs will automatically detect relationships based on the foreign keys:

JavaScriptDartSwiftKotlinPythonGraphQLURL

```
12345const { data, error } = await supabase.from('orchestral_sections').select(`  id,  name,  instruments ( id, name )`)
```

### TypeScript types for joins[#](#typescript-types-for-joins)

`supabase-js` always returns a `data` object (for success), and an `error` object (for unsuccessful requests).

These helper types provide the result types from any query, including nested types for database joins.

Given the following schema with a relation between orchestral sections and instruments:

```
12345678910create table orchestral_sections (  "id" serial primary key,  "name" text);create table instruments (  "id" serial primary key,  "name" text,  "section_id" int references "orchestral_sections");
```

We can get the nested `SectionsWithInstruments` type like this:

```
123456789101112131415import { QueryResult, QueryData, QueryError } from '@supabase/supabase-js'const sectionsWithInstrumentsQuery = supabase.from('orchestral_sections').select(`  id,  name,  instruments (    id,    name  )`)type SectionsWithInstruments = QueryData<typeof sectionsWithInstrumentsQuery>const { data, error } = await sectionsWithInstrumentsQueryif (error) throw errorconst sectionsWithInstruments: SectionsWithInstruments = data
```

## Many-to-many joins[#](#many-to-many-joins)

The data APIs will detect many-to-many joins. For example, if you have a database which stored teams of users (where each user could belong to many teams):

```
123456789101112131415create table users (  "id" serial primary key,  "name" text);create table teams (  "id" serial primary key,  "team_name" text);create table members (  "user_id" int references users,  "team_id" int references teams,  primary key (user_id, team_id));
```

In these cases you don't need to explicitly define the joining table (members). If we wanted to fetch all the teams and the members in each team:

JavaScriptDartSwiftKotlinPythonGraphQLURL

```
12345const { data, error } = await supabase.from('teams').select(`  id,  team_name,  users ( id, name )`)
```

## Specifying the `ON` clause for joins with multiple foreign keys[#](#specifying-the-on-clause-for-joins-with-multiple-foreign-keys)

For example, if you have a project that tracks when employees check in and out of work shifts:

```
123456789101112131415161718192021-- Employeescreate table users (  "id" serial primary key,  "name" text);-- Badge scanscreate table scans (  "id" serial primary key,  "user_id" int references users,  "badge_scan_time" timestamp);-- Work shiftscreate table shifts (  "id" serial primary key,  "user_id" int references users,  "scan_id_start" int references scans, -- clocking in  "scan_id_end" int references scans, -- clocking out  "attendance_status" text);
```

In this case, you need to explicitly define the join because the joining column on `shifts` is ambiguous as they are both referencing the `scans` table.

To fetch all the `shifts` with `scan_id_start` and `scan_id_end` related to a specific `scan`, use the following syntax:

JavaScriptDartSwiftKotlinPythonGraphQL

```
123456789101112131415const { data, error } = await supabase.from('shifts').select(  `    *,    start_scan:scans!scan_id_start (      id,      user_id,      badge_scan_time    ),   end_scan:scans!scan_id_end (     id,     user_id,     badge_scan_time    )  `)
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/joins-and-nesting.mdx)

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