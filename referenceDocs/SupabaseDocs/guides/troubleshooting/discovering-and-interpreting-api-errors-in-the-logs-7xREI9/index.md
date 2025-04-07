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

# Discovering and Interpreting API Errors in the Logs

Last edited: 2/21/2025

* * *

> A complimentary [guide](https://github.com/orgs/supabase/discussions/26224) was made for the Postgres logs

# Navigating the API logs:

The Database API is powered by a [PostgREST web-server](https://postgrest.org/en/v12/), recording every request to the API Edge Network logs. To precisely navigate them, use the [Log Explorer](https://supabase.com/dashboard/project/_/logs/explorer). These logs are managed through [Logflare](https://supabase.com/blog/supabase-logs-self-hosted) and can be queried with a subset of BigQuery SQL syntax.

The log table that contains API requests is `edge_logs`.

Notably, it contains:

| field | description |
| --- | --- |
| event\_message | the log's message |
| timestamp | time event was recorded |
| request metadata | metadata about the REST request |
| response metadata | metadata about the REST response |

The request and response columns are arrays in the metadata field and must be unnested. This is done with a `cross join`.

**Unnesting example**

```
1234567891011select  -- the event message does not require unnesting  event_message,  -- unnested status_code column from metadata.response field  status_codefrom  edge_logs  -- Unpack data stored in the 'metadata' field  cross join unnest(metadata) as metadata  -- After unpacking the 'metadata' field, extract the 'response' field from it  cross join unnest(response) as response;
```

The most useful fields for debugging are:

> NOTE: not every field is included below. For a full list, check the API Edge field reference in the [Log Explorer](https://supabase.com/dashboard/project/_/logs/explorer)

## Request object[#](#request-object)

### Cloudflare geographic data:[#](#cloudflare-geographic-data)

**Suggested use cases:**

-   Detecting abuse from a specific region
-   Detecting activity spikes from certain regions

| Column | Description | Sample value |
| --- | --- | --- |
| request.cf.city | Requester's city | Munich |
| request.cf.country | Requester's country | [DE](https://www.iso.org/iso-3166-country-codes.html) |
| request.cf.continent | Requester's continent | EU |
| request.cf.region | Requester's region | Bavaria |
| request.cf.latitudex | Requester's latitude | 48.10840 |
| request.cf.longitude | Requester's longitude | 11.61020 |
| request.cf.timezone | Requester's timezone | Europe/Berlin |

**Unnesting example:**

```
12345678910select  cityfrom  edge_logs-- Unpack 'metadata' fieldcross join unnest(metadata) AS metadata-- unpack 'request' from 'metadata'cross join unnest(request) AS request;-- unpack 'cf' from 'request'cross join unnest(cf) AS cf;
```

### IP and browser/environment data:[#](#ip-and-browserenvironment-data)

**Suggested use cases:**

-   Detecting request behavior from IP
-   Detecting abuse by IP
-   Detecting errors by user\_agent

| Column | Description | Sample value |
| --- | --- | --- |
| request.headers.cf\_connecting\_ip | Requester's IP | 80.81.18.138 |
| request.headers.user\_agent | Requester's browser or app environment | Mozilla/5.0 (Linux; Android 11; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 |

**Unnesting example:**

```
12345678910select  cf_connecting_ipfrom  edge_logs-- Unpack 'metadata' fieldcross join unnest(metadata) AS metadata-- unpack 'request' from 'metadata'cross join unnest(request) AS request;-- unpack 'headers' from 'request'cross join unnest(headers) AS headers;
```

### Query type and formatting data:[#](#query-type-and-formatting-data)

**Suggested use cases:**

-   identify problematic queries
-   identify unusual behavior by authenticated users

| Column | Description | Sample value |
| --- | --- | --- |
| request.method | Request Method (PATCH, GET, PUT...) | GET |
| request.url | Request URL, which contains the PostgREST formatted query | [https://yuhplfrsdxxxtldakizi.supabase.co/rest/v1/users?select=username&id=eq.63b6190e-214f-4b8a-b72d-3af6e1921411&limit=1](https://yuhplfrsdxxxtldakizi.supabase.co/rest/v1/users?select=username&id=eq.63b6190e-214f-4b8a-b72d-3af6e1921411&limit=1) |
| request.sb.auth\_users | authenticated user's ID | 63b6190e-214f-4b8a-b72d-3af6e1921411 |

**Unnesting example:**

```
123456789101112select  method,  url,  auth_usersfrom  edge_logs-- Unpack 'metadata' fieldcross join unnest(metadata) AS metadata-- unpack 'request' from 'metadata'cross join unnest(request) AS request;-- unpack 'sb' from 'request'cross join unnest(sb) AS sb;
```

## Response object[#](#response-object)

### Status code:[#](#status-code)

**Suggested use cases:**

-   detect success/errors

| Column | Description | Sample value |
| --- | --- | --- |
| response.status\_code | Response status code (200, 404, 500...) | 404 |

**Unnesting example:**

```
12345678select  status_codefrom  edge_logs  -- Unpack 'metadata' field  cross join unnest(metadata) as metadata  -- unpack 'response' from 'metadata'  cross join unnest(response) as response;
```

# Finding errors

### API level errors[#](#api-level-errors)

The `metadata.request.url` contains PostgREST formatted queries.

For example, the following call to the JS client:

```
1let { data: countries, error } = await supabase.from('countries').select('name')
```

translates to calling the following endpoint:

```
1https://<project ref>.supabase.co/rest/v1/countries?select=name
```

You can use regex ([Advanced Regex Guide](https://github.com/orgs/supabase/discussions/22640)) to find the objects related to your query. Try isolating by:

-   function names
-   column names
-   table names
-   query methods (select, insert, ...)

Example:

```
12345678910111213141516171819select  cast(timestamp as datetime) as timestamp,  status_code,  url,  event_messagefrom edge_logscross join unnest(metadata) as metadatacross join unnest(response) AS request;cross join unnest(response) AS response;where  -- find all errors  status_code >= 400    and  -- find queries featuring the a specific <table_name> and <column_name>  (    regexp_contains(url, '<table_name>')    and    regexp_contains(event_message, '<column_name1>|<column_name2>')  )
```

PostgREST has an [error reference table](https://postgrest.org/en/v12/references/errors.html) that you can use to interpret status codes.

### Database-level errors[#](#database-level-errors)

However, some errors that are reported through the Database API occur at the Postgres level. If it is not clear which error occurred you should reference the timestamp of the error and try to see if you can find it in the Postgres logs.

```
1234567891011121314151617181920212223242526select  cast(postgres_logs.timestamp as datetime) as timestamp,  error_severity,  user_name,  query,  detail,  sql_state_code,  event_messagefrom postgres_logs  cross join unnest(metadata) as metadata  cross join unnest(metadata.parsed) as parsedwhere  -- filter only for error events  regexp_contains(parsed.error_severity, 'ERROR|FATAL|PANIC')    and  -- All DB API requests are registered as the authenticator role  parsed.user_name = 'authenticator'    and  -- find failed queries featuring the function <function_name>  regexp_contains(parsed.query, '<function_name>')    and  -- limit the time of the search to be around the time of the failed API requestpostgres_logs.timestamp between '2024-04-15 10:50:00' AND '2024-04-15 10:50:27'order by timestamp desclimit 100;
```

Like PostgREST, Postgres has a [reference table](https://www.postgresql.org/docs/current/errcodes-appendix.html) for interpreting error codes.

## PostgREST server and Cloudflare errors[#](#postgrest-server-and-cloudflare-errors)

In some cases, errors may emerge because of Cloudflare or PostgREST server errors. For 500 and above errors, you may want to check your [PostgREST](https://supabase.com/dashboard/project/_/logs/postgrest-logs) logs and the [Cloudflare docs.](https://developers.cloudflare.com/support/troubleshooting/cloudflare-errors/troubleshooting-cloudflare-5xx-errors/#error-502-bad-gateway-or-error-504-gateway-timeout))

# Practical examples:

**Find All Errors:**

```
123456789101112131415select  cast(timestamp as datetime) as timestamp,  status_code,  event_message,  pathfrom  edge_logs  cross join unnest(metadata) as metadata  cross join unnest(response) as response  cross join unnest(request) as requestwhere  -- find all errors  status_code >= 400  and regexp_contains(path, '^/rest/v1/');-- only look at DB API
```

**Group errors by path and code:**

```
123456789101112131415select  status_code,  path,  count(path) as reoccurrence_per_pathfrom  edge_logs  cross join unnest(metadata) as metadata  cross join unnest(response) as response  cross join unnest(request) as requestwhere  -- find all errors  status_code >= 400  and regexp_contains(path, '^/rest/v1/') -- only look at DB APIgroup by path, status_codeorder by reoccurrence_per_path;
```

**Find requests by region:**

```
1234567891011121314select  path,  region,  count(region) as region_countfrom  edge_logs  cross join unnest(metadata) as metadata  cross join unnest(request) as request  cross join unnest(cf) as cfwhere  -- only look at DB API  regexp_contains(path, '^/rest/v1/')group by region, pathorder by requester_region_count;
```

**Find total requests by IP:**

```
12345678910111213select  cf_connecting_ip as ip,  count(cf_connecting_ip) as ip_countfrom  edge_logs  cross join unnest(metadata) as metadata  cross join unnest(request) as request  cross join unnest(headers) as headers  cross join unnest(cf) as cf  cross join unnest(response) as responsewhere regexp_contains(path, '^/auth/v1/')group by iporder by ip_count;
```

**Search frequented query paths by authenticated user:**

```
1234567891011121314select  -- only available for front-end clients  auth_users,  path,  count(auth_users) as ip_countfrom  edge_logs  cross join unnest(metadata) as metadata  cross join unnest(request) as request  cross join unnest(sb) as sbwhere  -- only look at DB API  regexp_contains(path, '^/rest/v1/')group by auth_users, path;
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[logs](https://supabase.com/docs/guides/troubleshooting?tags=logs)[api](https://supabase.com/docs/guides/troubleshooting?tags=api)[errors](https://supabase.com/docs/guides/troubleshooting?tags=errors)[postgrest](https://supabase.com/docs/guides/troubleshooting?tags=postgrest)[cloudflare](https://supabase.com/docs/guides/troubleshooting?tags=cloudflare)

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