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

# RLS Simplified

Last edited: 2/21/2025

* * *

### Basic summary[#](#basic-summary)

Row-Level Security (RLS) Policy: A `WHERE` or `CHECK` condition applied automatically to database queries

Key features:

-   Applies without being explicitly added to each query, which makes it good for policing row access from unknown entities, such as those leveraging the anon or authenticated roles.
-   Can be set for specific actions (e.g., SELECT, INSERT)
-   Can target particular database roles (e.g., "anon", "authenticated")

Contrast with regular conditions:

-   Regular conditions: Apply to all roles and must be added manually to each query
-   RLS policies: Applied automatically to specified actions and roles

## Hands on walk-through for conditions[#](#hands-on-walk-through-for-conditions)

### USING:[#](#using)

The `USING` keyword inspects the value of row to see if it should be made visible to the query.

When you SELECT, UPDATE, or DELETE, you have to use a WHERE statement to search for specific rows:

```
12345678910111213-- selectselect *from some_tablewhere id = 5;-- updateupdate some_tableset id = 6where id = 5;-- deletedelete from some_tablewhere id = 6;
```

Even when you don't use a WHERE statement, there's still an implicit one:

```
12-- ...your queryWHERE true;
```

The `USING` clause appends more to the WHERE statement:

```
123456789101112131415-- Your Using conditionUSING (  (select auth.uid()) = user_id);-- Your query without RLS:SELECT * FROM some_tableWHERE id = 5 OR id = 6;-- Your query after RLSSELECT * FROM some_tableWHERE  (id = 5 OR id = 6)    AND  (select auth.uid()) = user_id) -- <--- added by the USING clause;
```

### WITH CHECK:[#](#with-check)

Let's say you have a profile table. Well, you don't want user's to be able to modify their user\_id when they make an insert, do you?

The `WITH CHECK` condition inspects values that are being added or modified. For INSERT you'd use it by itself. There's no need for a using clause:

```
123456789101112131415161718-- Allow users to add to table, but make sure their user_id matches the one in their JWT:create policy "Allow user to add posts"on "public"."posts"as PERMISSIVEfor INSERTto authenticatedwith check(  (select auth.uid()) = user_id);-- Example: failing insertINSERT INTO postsVALUES (<false id>, <comment>);-- Example: successful insertINSERT INTO postsVALUES (<real id>, <comment>);
```

INSERTs do not rely on WHERE clauses, but they can have constraints. In this case, the RLS acts as a CHECK constraint against a column, e.g.:

```
12ALTER TABLE table_nameADD CONSTRAINT constraint_name CHECK (condition);
```

What distinguishes it from normal `CHECK` constraints is that it is only activate for certain roles or methods.

### UPDATEs:[#](#updates)

UPDATE both filters for rows to change and then adds new values to the table, so it requires both USING and WITH CHECK conditions:

```
1234567891011create policy "Allow user to edit their stuff"on "public"."<SOME TABLE NAME>"as RESTRICTIVEfor UPDATEto authenticatedusing (  (select auth.uid()) = user_id)with check(  (select auth.uid()) = user_id);
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Tags

[rls](https://supabase.com/docs/guides/troubleshooting?tags=rls)[sql](https://supabase.com/docs/guides/troubleshooting?tags=sql)[policy](https://supabase.com/docs/guides/troubleshooting?tags=policy)

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