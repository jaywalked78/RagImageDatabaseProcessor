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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  More

5.  [Migrating within Supabase](https://supabase.com/docs/guides/platform/migrating-within-supabase)

7.  [Restore Dashboard backup](https://supabase.com/docs/guides/platform/migrating-within-supabase/dashboard-restore)

# 

Restore Dashboard backup

## 

Learn how to restore your dashboard backup to a new Supabase project

* * *

## Before you begin[#](#before-you-begin)

Install Postgres and psql

Create and configure a new project

## Things to keep in mind[#](#things-to-keep-in-mind)

Here are some things that are not stored directly in your database and will require you to re-create or setup on the new project:

-   Edge Functions
-   Auth Settings and API keys
-   Realtime settings
-   Database extensions and settings
-   Read Replicas

Here is a non-exhaustive list of items that are commonly asked about and will be migrated with your backup restoration:

-   Database triggers
-   Database functions

## Restore backup[#](#restore-backup)

1

### Get the new database connection string

Go to the [project page](https://supabase.com/dashboard/project/_/) and click the "**Connect**" button at the top of the page for the connection string.

Use the Session pooler connection string by default. If your ISP supports IPv6, use the direct connection string.

Session pooler connection string:

```
1postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

Direct connection string:

```
1postgresql://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.com:5432/postgres
```

2

### Get the database password

It can take a few minutes for the database password reset to take effect. Especially if multiple password resets are done.

Reset the password in the [Database Settings](https://supabase.com/dashboard/project/_/settings/database).

Replace `[YOUR-PASSWORD]` in the connection string with the database password.

3

### Get the backup file path

Get the relative file path of the downloaded backup file.

If the restore is done in the same directory as the downloaded backup, the file path would look like this:

`./backup_name.backup`

4

### Verify the backup file format

The backup file will be gzipped with a .gz extension. You will need to unzip the file to look like this:

`backup_name.backup`

5

### Restore your backup

```
1psql -d [CONNECTION_STRING] -f /file/path
```

Replace `[CONNECTION_STRING]` with connection string from Steps 1 & 2.

Replace `/file/path` with the file path from Step 3.

Run the command with the replaced values to restore the backup to your new project.

## Migrate storage objects to new project's S3 storage[#](#migrate-storage-objects-to-new-projects-s3-storage)

After restoring the backup, the buckets and files metadata will show up in the dashboard of the new project. However, the storage files stored in the S3 buckets would not be present.

Use the following Google Colab script provided below to migrate your downloaded storage objects to your new project's S3 buckets.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/PLyn/supabase-storage-migrate/blob/main/Supabase_Storage_migration.ipynb)

This method requires uploading to Google Colab and then to the S3 buckets. This could add significant upload time if there are large storage objects.

## Common errors with the backup restore process[#](#common-errors-with-the-backup-restore-process)

"**object already exists**" "**constraint x for relation y already exists**" "**Many other variations of errors**"

These errors are expected when restoring to a new Supabase project. The backup from the dashboard is a full dump which contains the CREATE commands for all schemas. This is by design as the full dump allows you to rebuild the entire database from scratch even outside of Supabase.

One side effect of this method is that a new Supabase project has these commands already applied to schemas like storage and auth. The errors from this are not an issue because it skips to the next command to run. Another side effect of this is that all triggers will run during the restoration process which is not ideal but generally is not a problem.

There are circumstances where this method can fail and if it does, you should reach out to Supabase support for help.

"**psql: error: connection to server at "aws-0-us-east-1.pooler.supabase.com" (44.216.29.125), port 5432 failed: received invalid response to GSSAPI negotiation:**"

You are possibly using psql and Postgres version 15 or lower. Completely remove the Postgres installation and install the latest version as per the instructions above to resolve this issue.

"**psql: error: connection to server at "aws-0-us-east-1.pooler.supabase.com" (44.216.29.125), port 5432 failed: error received from server in SCRAM exchange: Wrong password**"

If the database password was reset, it may take a few minutes for it to reflect. Try again after a few minutes if you did a password reset.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/migrating-within-supabase/dashboard-restore.mdx)

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