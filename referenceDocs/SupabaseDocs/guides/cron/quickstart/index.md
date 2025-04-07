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

Cron

1.  [Cron](https://supabase.com/docs/guides/cron)

3.  Getting Started

5.  [Quickstart](https://supabase.com/docs/guides/cron/quickstart)

# 

Quickstart

* * *

Job names are case sensitive and cannot be edited once created.

Attempting to create a second Job with the same name (and case) will overwrite the first Job.

## Schedule a job[#](#schedule-a-job)

DashboardSQL

1.  Go to the [Jobs](https://supabase.com/dashboard/project/_/integrations/cron/jobs) section to schedule your first Job.
2.  Click on `Create job` button or navigate to the new Cron Job form [here](https://supabase.com/dashboard/project/_/integrations/cron/jobs?dialog-shown=true).
3.  Name your Cron Job.
4.  Choose a schedule for your Job by inputting cron syntax (refer to the syntax chart in the form) or natural language.
5.  Input SQL snippet or select a Database function, HTTP request, or Supabase Edge Function.

Cron syntax

You can input seconds for your Job schedule interval as long as you're on Postgres version 15.1.1.61 or later.

## Edit a job[#](#edit-a-job)

DashboardSQL

1.  Go to the [Jobs](https://supabase.com/dashboard/project/_/integrations/cron/jobs) section and find the Job you'd like to edit.
2.  Click on the three vertical dots menu on the right side of the Job and click `Edit cron job`.
3.  Make your changes and then click `Save cron job`.

## Activate/Deactivate a job[#](#activatedeactivate-a-job)

DashboardSQL

1.  Go to the [Jobs](https://supabase.com/dashboard/project/_/integrations/cron/jobs) section and find the Job you'd like to unschedule.
2.  Toggle the `Active`/`Inactive` switch next to Job name.

## Unschedule a job[#](#unschedule-a-job)

DashboardSQL

1.  Go to the [Jobs](https://supabase.com/dashboard/project/_/integrations/cron/jobs) section and find the Job you'd like to delete.
2.  Click on the three vertical dots menu on the right side of the Job and click `Delete cron job`.
3.  Confirm deletion by entering the Job name.

## Inspecting job runs[#](#inspecting-job-runs)

DashboardSQL

1.  Go to the [Jobs](https://supabase.com/dashboard/project/_/integrations/cron/jobs) section and find the Job you want to see the runs of.
2.  Click on the `History` button next to the Job name.

## Examples[#](#examples)

### Delete data every week[#](#delete-data-every-week)

Delete old data every Saturday at 3:30AM (GMT):

```
12345select cron.schedule (  'saturday-cleanup', -- name of the cron job  '30 3 * * 6', -- Saturday at 3:30AM (GMT)  $$ delete from events where event_time < now() - interval '1 week' $$);
```

### Run a vacuum every day[#](#run-a-vacuum-every-day)

Vacuum every day at 3:00AM (GMT):

```
1select cron.schedule('nightly-vacuum', '0 3 * * *', 'VACUUM');
```

### Call a database function every 5 minutes[#](#call-a-database-function-every-5-minutes)

Create a [`hello_world()`](https://supabase.com/docs/guides/database/functions?language=sql#simple-functions) database function and then call it every 5 minutes:

```
1select cron.schedule('call-db-function', '*/5 * * * *', 'SELECT hello_world()');
```

### Call a database stored procedure[#](#call-a-database-stored-procedure)

To use a stored procedure, you can call it like this:

```
1select cron.schedule('call-db-procedure', '*/5 * * * *', 'CALL my_procedure()');
```

### Invoke Supabase Edge Function every 30 seconds[#](#invoke-supabase-edge-function-every-30-seconds)

Make a POST request to a Supabase Edge Function every 30 seconds:

```
1234567891011121314select  cron.schedule(    'invoke-function-every-half-minute',    '30 seconds',    $$    select      net.http_post(          url:='https://project-ref.supabase.co/functions/v1/function-name',          headers:=jsonb_build_object('Content-Type','application/json', 'Authorization', 'Bearer ' || 'YOUR_ANON_KEY'),          body:=jsonb_build_object('time', now() ),          timeout_milliseconds:=5000      ) as request_id;    $$  );
```

This requires the [`pg_net` extension](https://supabase.com/docs/guides/database/extensions/pg_net) to be enabled.

## Caution: Scheduling system maintenance[#](#caution-scheduling-system-maintenance)

Be extremely careful when setting up Jobs for system maintenance tasks as they can have unintended consequences.

For instance, scheduling a command to terminate idle connections with `pg_terminate_backend(pid)` can disrupt critical background processes like nightly backups. Often, there is an existing Postgres setting, such as `idle_session_timeout`, that can perform these common maintenance tasks without the risk.

Reach out to [Supabase Support](https://supabase.com/support) if you're unsure if that applies to your use case.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/cron/quickstart.mdx)

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