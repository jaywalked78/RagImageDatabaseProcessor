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

# pg\_cron debugging guide

Last edited: 2/21/2025

* * *

This is a general guide for debugging pg\_cron. Below lists issues and how to debug them

# Cannot create/edit/delete cron jobs

Cron jobs can only be modified with the respective SQL functions:

-   Schedule: [cron.schedule](https://supabase.com/docs/guides/database/extensions/pg_cron#delete-data-every-week)
-   Alter: [cron.alter\_job](https://supabase.com/docs/guides/database/extensions/pg_cron#edit-a-job)
-   Delete: [cron.unschedule](https://supabase.com/docs/guides/database/extensions/pg_cron#unschedule-a-job)

If you are trying to make changes, use the cron functions. If the cron functions are inaccessible, contact [Support](https://supabase.com/dashboard/support/new)

  

* * *

# Cron Jobs are not running

> You should consider initiating a software upgrade in the [Infrastructure Settings](https://supabase.com/dashboard/project/_/settings/infrastructure) if your Postgres version is below v15.6.1.122. Upgrading will give you access to pg\_cron v1.6.4+, which has many bug fixes and auto-revive capabilities.

## Debugging steps:[#](#debugging-steps)

### Check to see if "pg\_cron scheduler" is active[#](#check-to-see-if-pgcron-scheduler-is-active)

pg\_cron operates as the `pg_cron scheduler` process within Postgres. Use the below query to check if the worker is active

```
12345678910SELECT  pid as process_id,  usename as database_user,  application_name,  backend_start as when_process_began,  wait_event_type,  state,  query,  backend_typeFROM pg_stat_activity where application_name ilike 'pg_cron scheduler';
```

If the query does not return a row, the worker has died. To revive it, you must go to the [General Settings](https://supabase.com/dashboard/project/_/settings/general) and initiate a fast reboot:

![Screenshot 2024-10-29 at 12 27 24 AM](https://github.com/user-attachments/assets/d7a2956c-08e0-4ebc-be08-d14a2383f36b)  

### Check the `cron.job_run_details` table for more information[#](#check-the-cronjobrundetails-table-for-more-information)

pg\_cron creates logs in its own table `cron.job_run_details"`. The below query checks for issues from the past 5 days :

```
12345678SELECT *FROM cron.job_run_detailsWHERE    (status <> 'succeeded' AND status <> 'running')        AND     start_time > NOW() - INTERVAL '5 days'ORDER BY start_time DESCLIMIT 10;
```

Respond to the errors exposed appropriately.

> Long running jobs may show timeout errors. For jobs that are intended to execute for extended periods, consider wrapping their queries in functions with custom timeouts ([guide](https://supabase.com/docs/guides/database/postgres/timeouts#function-level)).

  

### Check if there are too many cron jobs running concurrently[#](#check-if-there-are-too-many-cron-jobs-running-concurrently)

pg\_cron supports up to 32 concurrent jobs, each using a database connection. If too many jobs are running simultaneously, space them out to prevent connection overload and job failure.

The below queries shows all pg\_cron jobs:

```
12345-- All jobsselect schedule, jobname, command from cron.job;-- Count jobsselect COUNT(*) from cron.job;
```

The below query can be used to find actively querying jobs:

```
12345678910SELECT  pid as process_id,  usename as database_user,  application_name,  backend_start as when_process_began,  wait_event_type,  state,  query,  backend_typeFROM pg_stat_activity where application_name ilike 'pg_cron';
```

You can view your concurrent peak connection usage throughout the day at the bottom of the [Reports Dashboard](https://supabase.com/dashboard/project/_/reports/database)

  

### Check for database strain[#](#check-for-database-strain)

Unfortunately, excessive resource strain can slow down or disrupt jobs.

Go to the [reports page](https://supabase.com/dashboard/project/_/reports/database) (or [Supabase Grafana](https://supabase.com/docs/guides/monitoring-troubleshooting/metrics#deploying-supabase-grafana) if you have it setup), and check for signs of resource exhaustion. If it's clear your database is under pressure, consider upgrading your compute add-on or following the advice from one of the optimization guides:

-   [Connections](https://github.com/orgs/supabase/discussions/27141)
-   [Disk/IO](https://github.com/orgs/supabase/discussions/27003)
-   [Memory](https://github.com/orgs/supabase/discussions/27021)
-   [CPU](https://github.com/orgs/supabase/discussions/27022)

It is important to make sure you are running the latest release of pg\_cron (1.6.4) if you're noticing strain. It is the most robust.

  

### Check the log explorer for more information[#](#check-the-log-explorer-for-more-information)

Although pg\*cron records errors in the `cron.job_run_details` table, in rare cases, more information can be found in the general Postgres logs. You can check the [Log Explorer](https://supabase.com/dashboard/project/*/logs/explorer) for failure events with the following query

```
1234567891011121314151617181920select  cast(postgres_logs.timestamp as datetime) as timestamp,  event_message,  parsed.error_severity,  parsed.user_name,  parsed.query,  parsed.detail,  parsed.hint,  parsed.sql_state_code,  parsed.backend_type,  parsed.application_namefrom  postgres_logs  cross join unnest(metadata) as metadata  cross join unnest(metadata.parsed) as parsedwhere  regexp_contains(parsed.error_severity, 'ERROR|FATAL|PANIC')  and regexp_contains(parsed.application_name, 'pg_cron')order by timestamp desclimit 100;
```

If you're interested in modifying the query, there is an advanced [guide](https://github.com/orgs/supabase/discussions/26224) for navigating the Postgres logs and a general purpose [one](https://supabase.com/docs/guides/platform/advanced-log-filtering) for applying filters.

  

### Create custom logs within cron jobs[#](#create-custom-logs-within-cron-jobs)

If it's still not clear what is occurring you may be able to capture more logs by running the pg\_cron query inside a database function:

```
123456789101112131415161718192021create or replace function log_example()returns voidlanguage plpgsqlas $$begin     -- Logging start of function     raise log 'logging start of cron function call: (%)', (select now());    -- INSERT LOGIC HERE     -- Logging end of function     raise log 'logging end of cron function call: (%)', (select now());    exception     -- Handle exceptions here if needed     when others then         raise exception 'An error occurred in cron function <insert name here>. ERROR MESSAGE: %', sqlerrm;end;$$;
```

You can then search for your custom messages in the [Logs Interface](https://supabase.com/dashboard/project/_/logs/postgres-logs)

  

### Upgrading pg\_cron version[#](#upgrading-pgcron-version)

The current version of pg\*cron on Supabase is 1.6.4. It comes with a [few bug fixes](https://github.com/citusdata/pg_cron/releases/tag/v1.6.4). You should consider upgrading to Postgres v15.6.1.122+ in the [Infrastructure Settings](https://supabase.com/dashboard/project/*/settings/infrastructure) to get the latest extension.

  

### Contacting support and the maintainers[#](#contacting-support-and-the-maintainers)

Although Supabase includes the extension, it is maintained by Citus (a Microsoft subsidiary). You can contact Support for more help, but you should also consider creating an issue in the [pg\_cron repo](https://github.com/citusdata/pg_cron).

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[pg\_cron](https://supabase.com/docs/guides/troubleshooting?tags=pg_cron)[cron](https://supabase.com/docs/guides/troubleshooting?tags=cron)[jobs](https://supabase.com/docs/guides/troubleshooting?tags=jobs)[scheduler](https://supabase.com/docs/guides/troubleshooting?tags=scheduler)[debugging](https://supabase.com/docs/guides/troubleshooting?tags=debugging)

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