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

3.  Working with your database (intermediate)

5.  [Managing enums](https://supabase.com/docs/guides/database/postgres/enums)

# 

Managing Enums in Postgres

* * *

Enums in Postgres are a custom data type. They allow you to define a set of values (or labels) that a column can hold. They are useful when you have a fixed set of possible values for a column.

## Creating enums[#](#creating-enums)

You can define a Postgres Enum using the `create type` statement. Here's an example:

```
123456create type mood as enum (  'happy',  'sad',  'excited',  'calm');
```

In this example, we've created an Enum called "mood" with four possible values.

## When to use enums[#](#when-to-use-enums)

There is a lot of overlap between Enums and foreign keys. Both can be used to define a set of values for a column. However, there are some advantages to using Enums:

-   Performance: You can query a single table instead of finding the value from a lookup table.
-   Simplicity: Generally the SQL is easier to read and write.

There are also some disadvantages to using Enums:

-   Limited Flexibility: Adding and removing values requires modifying the database schema (i.e.: using migrations) rather than adding data to a table.
-   Maintenance Overhead: Enum types require ongoing maintenance. If your application's requirements change frequently, maintaining enums can become burdensome.

In general you should only use Enums when the list of values is small, fixed, and unlikely to change often. Things like "a list of continents" or "a list of departments" are good candidates for Enums.

## Using enums in tables[#](#using-enums-in-tables)

To use the Enum in a table, you can define a column with the Enum type. For example:

```
12345create table person (  id serial primary key,  name text,  current_mood mood);
```

Here, the `current_mood` column can only have values from the "mood" Enum.

### Inserting data with enums[#](#inserting-data-with-enums)

You can insert data into a table with Enum columns by specifying one of the Enum values:

```
1234insert into person  (name, current_mood)values  ('Alice', 'happy');
```

### Querying data with enums[#](#querying-data-with-enums)

When querying data, you can filter and compare Enum values as usual:

```
123select * from person where current_mood = 'sad';
```

## Managing enums[#](#managing-enums)

You can manage your Enums using the `alter type` statement. Here are some examples:

### Updating enum values[#](#updating-enum-values)

You can update the value of an Enum column:

```
123update personset current_mood = 'excited'where name = 'Alice';
```

### Adding enum values[#](#adding-enum-values)

To add new values to an existing Postgres Enum, you can use the `ALTER TYPE` statement. Here's how you can do it:

Let's say you have an existing Enum called `mood`, and you want to add a new value, `content`:

```
1alter type mood add value 'content';
```

### Removing enum values[#](#removing-enum-values)

Even though it is possible, it is unsafe to remove enum values once they have been created. It's better to leave the enum value in place.

Read the [Postgres mailing list](https://www.postgresql.org/message-id/21012.1459434338%40sss.pgh.pa.us) for more information:

There is no `ALTER TYPE DELETE VALUE` in Postgres. Even if you delete every occurrence of an Enum value within a table (and vacuumed away those rows), the target value could still exist in upper index pages. If you delete the `pg_enum` entry you'll break the index.

### Getting a list of enum values[#](#getting-a-list-of-enum-values)

Check your existing Enum values by querying the enum\_range function:

```
1select enum_range(null::mood);
```

## Resources[#](#resources)

-   Official Postgres Docs: [Enumerated Types](https://www.postgresql.org/docs/current/datatype-enum.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/enums.mdx)

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