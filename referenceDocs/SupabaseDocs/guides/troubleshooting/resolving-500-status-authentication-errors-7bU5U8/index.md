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

# Resolving 500 Status Authentication Errors

Last edited: 2/21/2025

* * *

# Resolving 500 status authentication errors

A 500 error in Auth typically indicates an issue with an external dependency, such as your database or SMTP provider, rather than with Auth itself. This guide will help you explore the Auth logs to identify the underlying cause.

### Prerequisites[#](#prerequisites)

#### Open the log explorer[#](#open-the-log-explorer)

Ensure you have access to the [Dashboard's Log Explorer](https://supabase.com/dashboard/project/_/logs/explorer) and set the time range appropriately:

![image](https://supabase.com/docs/img/troubleshooting/152d65ad-f0ed-47cf-8dcb-1e31c6221e71.png)

#### Improving log readability[#](#improving-log-readability)

Logs are displayed in a table format, which can be challenging to read. Double-clicking on a row will expand it for easier viewing:

![Screenshot 2024-08-14 at 1 15 26 PM](https://github.com/user-attachments/assets/6f4c833c-ae15-41e1-9aa8-48ebd58741a1)

## Section 1: Checking for database-level errors[#](#section-1-checking-for-database-level-errors)

### Query for recent database errors[#](#query-for-recent-database-errors)

Use the following SQL query to check for any recent errors the Auth server encountered while interacting with your database:

```
12345678910111213141516171819select  cast(postgres_logs.timestamp as datetime) as timestamp,  event_message,  parsed.error_severity,  parsed.user_name,  parsed.query,  parsed.detail,  parsed.hint,  parsed.sql_state_code,  parsed.backend_typefrom  postgres_logs  cross join unnest(metadata) as metadata  cross join unnest(metadata.parsed) as parsedwhere  regexp_contains(parsed.error_severity, 'ERROR|FATAL|PANIC')  and regexp_contains(parsed.user_name, 'supabase_auth_admin')order by timestamp desclimit 100;
```

If no results are returned, proceed to Section 2.

### Common database-level errors[#](#common-database-level-errors)

There are few known categories of auth/database level errors:

### Constraint related (sql\_state\_code = 23503 or 23\*)[#](#constraint-related-sqlstatecode--23503-or-23)

If you’ve manually created a foreign key relationship between your tables and those in the `auth` schema, a constraint may prevent the Auth server from updating the `auth.users` table.

#### Solution[#](#solution)

The log will show the name of the constraint. You need `DROP` it:

```
1ALTER TABLE <your table> DROP CONSTRAINT <constraint name>;
```

Alternatively, you can `DROP` and then recreate the constraint with a less restrictive modifier, such as `SET NULL`, `SET DEFAULT`, or `CASCADE`:

```
1234567BEGIN;ALTER TABLE <your table> DROP CONSTRAINT <constraint name>;ALTER TABLE <your table> ADD CONSTRAINT <constraint name> FOREIGN KEY (<column name>)          REFERENCES auth.users (<auth.users column>)          ON DELETE SET NULL;COMMIT;
```

### Ownership related (sql\_state\_code = 42501)[#](#ownership-related-sqlstatecode--42501)

If you see an error like must be owner of..., the supabase\_auth\_admin role may have lost privileges over tables in the auth schema. This often results from faulty migrations by external ORMs (e.g., Prisma) or manual schema modifications.

#### Solution[#](#solution)

Check ownership with this [GitHub Gist](https://gist.github.com/TheOtherBrian1/6aaaa78632b1e371f3b1c790305f0acd). If any objects are owned by the `supabase_admin` role, contact [Support](https://supabase.com/dashboard/support/new). If they're owned by roles other than `supabase_auth_admin` you can change ownership back manually one-by-one:

```
1ALTER <object type (table, function, etc.)> <auth.object_name> OWNER TO supabase_auth_admin;
```

Alternatively, you can run the SQL script in this [GitHub Gist](https://gist.github.com/TheOtherBrian1/4714a333432b80660ff71b136b298fb8) to change all

### Trigger related:[#](#trigger-related)

If errors reference a database function, this indicates a trigger error on one of the auth tables (likely auth.users). If you do not want to keep the trigger/function, you can just quickly drop it, otherwise, continue reading to know how to fix the issue:

```
12345-- delete the trigger with the following SQL:DROP FUNCTION <function name>() CASCADE;-- If you'd prefer, you can drop the trigger alone with the following query:-- DROP TRIGGER <trigger_name> on auth.<table_name>;
```

#### Solutions:[#](#solutions)

Get the function's definition with this query:

```
123select pg_get_functiondef(oid)from pg_procwhere proname = '<FUNCTION NAME>';
```

##### Trigger has insufficient privileges ( sql\_state\_code = 42501)

If the error is related to insufficient privileges, your trigger function is missing a security definer tag, which allows it to access schemas outside of auth. You must `REPLACE` the function with the appropriate security definer settings ([example](https://supabase.com/docs/guides/database/functions?queryGroups=language&language=js#security-definer-vs-invoker))

##### Trigger references a table or column that does not exist (sql\_state\_code = 42P01)

The trigger may be referencing a table or column that no longer exists. In that case do one of the three:

-   make sure the trigger is referencing the table using the right schema, e.g. public, auth, etc.
-   modify the trigger function to reference the appropriate database objects.
-   remove the trigger
-   recreate the database object that the trigger referenced

### Corrupted schema[#](#corrupted-schema)

If you made any customizations to the auth schema, such as adding RLS, modifying table columns, or adding/dropping tables, it can break migrations done by the Auth Server. It's necessary to remove these changes and restore the auth schema to its original form.

## Section 2: Checking Auth level errors[#](#section-2-checking-auth-level-errors)

### Query for Auth errors[#](#query-for-auth-errors)

Run this SQL query in the Log Explorer to find Auth-related errors:

```
123456789101112131415select  cast(metadata.timestamp as datetime) as timestamp,  msg,  event_message,  status,  path,  levelfrom auth_logscross join unnest(metadata) as metadatawhere   -- find all errors   status::INT = 500    OR  regexp_contains(level, 'error|fatal')order by timestamp
```

### Database migration errors[#](#database-migration-errors)

> `running db migrations: Migrator: problem creating schema migrations`

This is a continuation of the "Corrupted Schema" error from the Postgres Section. If you modified structures in the auth schema, such as columns or tables, or added restrictions, such as RLS, Auth will not be able to complete it's migrations. It's necessary to remove those modifications.

If you are running older versions of auth, you may experience a migration bug. If so, checkout this [guide](https://github.com/orgs/supabase/discussions/20722) for a resolution. If it doesn't work, contact Support.

### SMTP errors[#](#smtp-errors)

The logs may contain messages about `gomail`. It means that auth is struggling to communicate with the SMTP provider. This often implies that:

1.  Misconfigured custom domain name with your email provider.
2.  Invalid email port usage.
3.  Rate limiting by the SMTP provider.
4.  SMTP provider downtime.

The log will be able to provide some context for what is occurring, but it is important to check with your external SMTP provider to make sure everything is properly configured.

## Step 3: Checking email templates[#](#step-3-checking-email-templates)

Incomplete or incorrect email templates can also cause 500 errors. If your templates have unclosed variable tags or HTML elements, or use forbidden characters, this might be the issue.

Test a simplified email template in the [Auth Dashboard](https://supabase.com/dashboard/project/_/auth/templates). If the new template works, revise your original template to avoid forbidden characters and ensure all elements/variables are properly closed.

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[500](https://supabase.com/docs/guides/troubleshooting?errorCodes=500)

* * *

### Tags

[authentication](https://supabase.com/docs/guides/troubleshooting?tags=authentication)[smtp](https://supabase.com/docs/guides/troubleshooting?tags=smtp)[database](https://supabase.com/docs/guides/troubleshooting?tags=database)[logs](https://supabase.com/docs/guides/troubleshooting?tags=logs)[error](https://supabase.com/docs/guides/troubleshooting?tags=error)

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