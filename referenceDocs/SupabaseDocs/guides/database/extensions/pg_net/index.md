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

5.  [pg\_net: Async Networking](https://supabase.com/docs/guides/database/extensions/pg_net)

# 

pg\_net: Async Networking

* * *

The pg\_net API is in beta. Functions signatures may change.

[pg\_net](https://github.com/supabase/pg_net/) enables Postgres to make asynchronous HTTP/HTTPS requests in SQL. It differs from the [`http`](https://supabase.com/docs/guides/database/extensions/http) extension in that it is asynchronous by default. This makes it useful in blocking functions (like triggers).

It eliminates the need for servers to continuously poll for database changes and instead allows the database to proactively notify external resources about significant events.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "pg\_net" and enable the extension.

## `http_get`[#](#httpget)

Creates an HTTP GET request returning the request's ID. HTTP requests are not started until the transaction is committed.

### Signature [#](#get-signature)

This is a Postgres [SECURITY DEFINER](https://supabase.com/docs/guides/database/postgres/row-level-security#use-security-definer-functions) function.

```
1234567891011121314151617net.http_get(    -- url for the request    url text,    -- key/value pairs to be url encoded and appended to the `url`    params jsonb default '{}'::jsonb,    -- key/values to be included in request headers    headers jsonb default '{}'::jsonb,    -- the maximum number of milliseconds the request may take before being canceled    timeout_milliseconds int default 2000)    -- request_id reference    returns bigint    strict    volatile    parallel safe    language plpgsql
```

### Usage [#](#get-usage)

```
1234567select    net.http_get('https://news.ycombinator.com')    as request_id;request_id----------         1(1 row)
```

## `http_post`[#](#httppost)

Creates an HTTP POST request with a JSON body, returning the request's ID. HTTP requests are not started until the transaction is committed.

The body's character set encoding matches the database's `server_encoding` setting.

### Signature [#](#post-signature)

This is a Postgres [SECURITY DEFINER](https://supabase.com/docs/guides/database/postgres/row-level-security#use-security-definer-functions) function

```
123456789101112131415161718net.http_post(    -- url for the request    url text,    -- body of the POST request    body jsonb default '{}'::jsonb,    -- key/value pairs to be url encoded and appended to the `url`    params jsonb default '{}'::jsonb,    -- key/values to be included in request headers    headers jsonb default '{"Content-Type": "application/json"}'::jsonb,    -- the maximum number of milliseconds the request may take before being canceled    timeout_milliseconds int default 2000)    -- request_id reference    returns bigint    volatile    parallel safe    language plpgsql
```

### Usage [#](#post-usage)

```
123456789select    net.http_post(        url:='https://httpbin.org/post',        body:='{"hello": "world"}'::jsonb    ) as request_id;request_id----------         1(1 row)
```

## `http_delete`[#](#httpdelete)

Creates an HTTP DELETE request, returning the request's ID. HTTP requests are not started until the transaction is committed.

### Signature [#](#post-signature)

This is a Postgres [SECURITY DEFINER](https://supabase.com/docs/guides/database/postgres/row-level-security#use-security-definer-functions) function

```
123456789101112131415161718net.http_delete(    -- url for the request    url text,    -- key/value pairs to be url encoded and appended to the `url`    params jsonb default '{}'::jsonb,    -- key/values to be included in request headers    headers jsonb default '{}'::jsonb,    -- the maximum number of milliseconds the request may take before being canceled    timeout_milliseconds int default 2000)    -- request_id reference    returns bigint    strict    volatile    parallel safe    language plpgsql    security definer
```

### Usage [#](#delete-usage)

```
1234567select    net.http_delete(        'https://dummy.restapiexample.com/api/v1/delete/2'    ) as request_id;----------         1(1 row)
```

## Analyzing responses[#](#analyzing-responses)

Waiting requests are stored in the `net.http_request_queue` table. Upon execution, they are deleted.

```
123456789CREATE UNLOGGED TABLE    net.http_request_queue (        id bigint NOT NULL DEFAULT nextval('net.http_request_queue_id_seq'::regclass),        method text NOT NULL,        url text NOT NULL,        headers jsonb NOT NULL,        body bytea NULL,        timeout_milliseconds integer NOT NULL    )
```

Once a response is returned, by default, it is stored for 6 hours in the `net._http_response` table.

```
1234567891011CREATE UNLOGGED TABLE    net._http_response (        id bigint NULL,        status_code integer NULL,        content_type text NULL,        headers jsonb NULL,        content text NULL,        timed_out boolean NULL,        error_msg text NULL,        created timestamp with time zone NOT NULL DEFAULT now()    )
```

The responses can be observed with the following query:

```
1select * from net._http_response;
```

The data can also be observed in the `net` schema with the [Supabase Dashboard's SQL Editor](https://supabase.com/dashboard/project/_/editor)

## Debugging requests[#](#debugging-requests)

### Inspecting request data[#](#inspecting-request-data)

The [Postman Echo API](https://documenter.getpostman.com/view/5025623/SWTG5aqV) returns a response with the same body and content as the request. It can be used to inspect the data being sent.

Sending a post request to the echo API

```
12345select    net.http_post(        url := 'https://postman-echo.com/post',        body := '{"key1": "value", "key2": 5}'::jsonb    ) as request_id;
```

Inspecting the echo API response content to ensure it contains the right body

```
123456select    "content"from net._http_responsewhere id = <request_id>-- returns information about the request-- including the body sent: {"key": "value", "key": 5}
```

Alternatively, by wrapping a request in a [database function](https://supabase.com/docs/guides/database/functions), sent row data can be logged or returned for inspection and debugging.

```
12345678910111213141516171819202122232425262728293031323334create or replace function debugging_example (row_id int)returns jsonb as $$declare    -- Store payload data    row_data_var jsonb;begin    -- Retrieve row data and convert to JSON    select to_jsonb("<example_table>".*) into row_data_var    from "<example_table>"    where "<example_table>".id = row_id;    -- Initiate HTTP POST request to URL    perform        net.http_post(            url := 'https://postman-echo.com/post',            -- Use row data as payload            body := row_data_var        ) as request_id;    -- Optionally Log row data or other data for inspection in Supabase Dashboard's Postgres Logs    raise log 'Logging an entire row as JSON (%)', row_data_var;    -- return row data to inspect    return row_data_var;-- Handle exceptions here if neededexception    when others then        raise exception 'An error occurred: %', SQLERRM;end;$$ language plpgsql;-- calling functionselect debugging_example(<row_id>);
```

### Inspecting failed requests[#](#inspecting-failed-requests)

Finds all failed requests

```
12345select  *from net._http_responsewhere "status_code" >= 400 or "error_msg" is not nullorder by "created" desc;
```

## Configuration[#](#configuration)

##### Must be on pg\_net v0.12.0 or above to reconfigure

Supabase supports reconfiguring pg\*net starting from v0.12.0+. For the latest release, initiate a Postgres upgrade in the [Infrastructure Settings](https://supabase.com/dashboard/project/*/settings/infrastructure).

The extension is configured to reliably execute up to 200 requests per second. The response messages are stored for only 6 hours to prevent needless buildup. The default behavior can be modified by rewriting config variables.

### Get current settings[#](#get-current-settings)

```
12345select  "name",  "setting"from pg_settingswhere "name" like 'pg_net%';
```

### Alter settings[#](#alter-settings)

Change variables:

```
12alter role "postgres" set pg_net.ttl to '24 hours';alter role "postgres" set pg_net.batch_size to 500;
```

Then reload the settings and restart the `pg_net` background worker with:

```
1select net.worker_restart();
```

## Examples[#](#examples)

### Invoke a Supabase Edge Function[#](#invoke-a-supabase-edge-function)

Make a POST request to a Supabase Edge Function with auth header and JSON body payload:

```
123456select    net.http_post(        url:='https://project-ref.supabase.co/functions/v1/function-name',        headers:='{"Content-Type": "application/json", "Authorization": "Bearer <YOUR_ANON_KEY>"}'::jsonb,        body:='{"name": "pg_net"}'::jsonb    ) as request_id;
```

### Call an endpoint every minute with [pg\_cron](https://supabase.com/docs/guides/database/extensions/pgcron)[#](#call-an-endpoint-every-minute-with-pgcron)

The pg\_cron extension enables Postgres to become its own cron server. With it you can schedule regular calls with up to a minute precision to endpoints.

```
12345678910111213select cron.schedule(	'cron-job-name',	'* * * * *', -- Executes every minute (cron syntax)	$$	    -- SQL query	    select "net"."http_post"(            -- URL of Edge function            url:='https://project-ref.supabase.co/functions/v1/function-name',            headers:='{"Authorization": "Bearer <YOUR_ANON_KEY>"}'::jsonb,            body:='{"name": "pg_net"}'::jsonb	    ) as "request_id";	$$);
```

### Execute pg\_net in a trigger[#](#execute-pgnet-in-a-trigger)

Make a call to an external endpoint when a trigger event occurs.

```
123456789101112131415161718192021222324-- function called by triggercreate or replace function <function_name>()    returns trigger    language plpgSQLas $$begin    -- calls pg_net function net.http_post    -- sends request to postman API    perform "net"."http_post"(      'https://postman-echo.com/post'::text,      jsonb_build_object(        'old_row', to_jsonb(old.*),        'new_row', to_jsonb(new.*)      ),      headers:='{"Content-Type": "application/json"}'::jsonb    ) as request_id;    return new;END $$;-- trigger for table updatecreate trigger <trigger_name>    after update on <table_name>    for each row    execute function <function_name>();
```

### Send multiple table rows in one request[#](#send-multiple-table-rows-in-one-request)

```
12345678910111213with "selected_table_rows" as (    select        -- Converts all the rows into a JSONB array        jsonb_agg(to_jsonb(<table_name>.*)) as JSON_payload    from <table_name>    -- good practice to LIMIT the max amount of rows)select    net.http_post(        url := 'https://postman-echo.com/post'::text,        body := JSON_payload    ) AS request_idFROM "selected_table_rows";
```

More examples can be seen on the [Extension's GitHub page](https://github.com/supabase/pg_net/)

## Limitations[#](#limitations)

-   To improve speed and performance, the requests and responses are stored in [unlogged tables](https://pgpedia.info/u/unlogged-table.html), which are not preserved during a crash or unclean shutdown.
-   By default, response data is saved for only 6 hours
-   Can only make POST requests with JSON data. No other data formats are supported
-   Intended to handle at most 200 requests per second. Increasing the rate can introduce instability
-   Does not have support for PATCH/PUT requests
-   Can only work with one database at a time. It defaults to the `postgres` database.

## Resources[#](#resources)

-   Source code: [github.com/supabase/pg\_net](https://github.com/supabase/pg_net/)
-   Official Docs: [github.com/supabase/pg\_net](https://github.com/supabase/pg_net/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_net.mdx)

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