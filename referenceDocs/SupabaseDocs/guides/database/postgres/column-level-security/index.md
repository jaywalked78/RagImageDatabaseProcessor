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

3.  Access and security

5.  [Column Level Security](https://supabase.com/docs/guides/database/postgres/column-level-security)

# 

Column Level Security

* * *

PostgreSQL's [Row Level Security (RLS)](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) gives you granular control over who can access rows of data. However, it doesn't give you control over which columns they can access within rows. Sometimes you want to restrict access to specific columns in your database. Column Level Privileges allows you to do just that.

This is an advanced feature. We do not recommend using column-level privileges for most users. Instead, we recommend using RLS policies in combination with a dedicated table for handling user roles.

Restricted roles cannot use the wildcard operator (`*`) on the affected table. Instead of using `SELECT * FROM <restricted_table>;` or its API equivalent, you must specify the column names explicitly.

## Policies at the row level[#](#policies-at-the-row-level)

Policies in Row Level Security (RLS) are used to restrict access to rows in a table. Think of them like adding a `WHERE` clause to every query.

For example, let's assume you have a `posts` table with the following columns:

-   `id`
-   `user_id`
-   `title`
-   `content`
-   `created_at`
-   `updated_at`

You can restrict updates to just the user who created it using [RLS](https://supabase.com/docs/guides/auth#row-level-security), with the following policy:

```
123create policy "Allow update for owners" on posts forupdate  using ((select auth.uid()) = user_id);
```

However, this gives the post owner full access to update the row, including all of the columns.

## Privileges at the column level[#](#privileges-at-the-column-level)

To restrict access to columns, you can use [Privileges](https://www.postgresql.org/docs/current/ddl-priv.html).

There are two types of privileges in Postgres:

1.  **table-level**: Grants the privilege on all columns in the table.
2.  **column-level** Grants the privilege on a specific column in the table.

You can have both types of privileges on the same table. If you have both, and you revoke the column-level privilege, the table-level privilege will still be in effect.

By default, our table will have a table-level `UPDATE` privilege, which means that the `authenticated` role can update all the columns in the table.

```
123456789revokeupdate  on table public.postsfrom  authenticated;grantupdate  (title, content) on table public.posts to authenticated;
```

In the above example, we are revoking the table-level `UPDATE` privilege from the `authenticated` role and granting a column-level `UPDATE` privilege on just the `title` and `content` columns.

If we want to restrict access to updating the `title` column:

```
12345revokeupdate  (title) on table public.postsfrom  authenticated;
```

This time, we are revoking the column-level `UPDATE` privilege of the `title` column from the `authenticated` role. We didn't need to revoke the table-level `UPDATE` privilege because it's already revoked.

## Manage column privileges in the Dashboard[#](#manage-column-privileges-in-the-dashboard)

You can view and edit the privileges in the [Supabase Studio](https://supabase.com/dashboard/project/_/database/column-privileges).

![Column level privileges](https://supabase.com/docs/img/guides/privileges/column-level-privileges-2.png)

## Manage column privileges in migrations[#](#manage-column-privileges-in-migrations)

While you can manage privileges directly from the Dashboard, as your project grows you may want to manage them in your migrations. Read about database migrations in the [Local Development](https://supabase.com/docs/guides/deployment/database-migrations) guide.

1

### Create a migration file

To get started, generate a [new migration](https://supabase.com/docs/reference/cli/supabase-migration-new) to store the SQL needed to create your table along with row and column-level privileges.

```
1supabase migration new create_posts_table
```

2

### Add the SQL to your migration file

This creates a new migration: supabase/migrations/<timestamp> \_create\_posts\_table.sql.

To that file, add the SQL to create this `posts` table with row and column-level privileges.

```
123456789101112131415161718192021create tableposts (id bigint primary key generated always as identity,user_id text,title text,content text,created_at timestamptz default now()updated_at timestamptz default now());-- Add row-level securitycreate policy "Allow update for owners" on posts forupdateusing ((select auth.uid()) = user_id);-- Add column-level securityrevokeupdate(title) on table public.postsfromauthenticated;
```

## Considerations when using column-level privileges[#](#considerations-when-using-column-level-privileges)

-   If you turn off a column privilege you won't be able to use that column at all.
-   All operations (insert, update, delete) as well as using `select *` will fail.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/column-level-security.mdx)

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