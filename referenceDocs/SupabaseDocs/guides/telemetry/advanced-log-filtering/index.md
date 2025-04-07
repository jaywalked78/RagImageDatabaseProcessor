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

Telemetry

1.  [Telemetry](https://supabase.com/docs/guides/telemetry)

3.  Logging & observability

5.  [Advanced log filtering](https://supabase.com/docs/guides/telemetry/advanced-log-filtering)

# 

Advanced Log Filtering

* * *

# Querying the logs

## Understanding field references[#](#understanding-field-references)

The log tables are queried with a subset of BigQuery SQL syntax. They all have three columns: `event_message`, `timestamp`, and `metadata`.

| column | description |
| --- | --- |
| timestamp | time event was recorded |
| event\_message | the log's message |
| metadata | information about the event |

The `metadata` column is an array of JSON objects that stores important details about each recorded event. For example, in the Postgres table, the `metadata.parsed.error_severity` field indicates the error level of an event. To work with its values, you need to `unnest` them using a `cross join`.

This approach is commonly used with JSON and array columns, so it might look a bit unfamiliar if you're not used to working with these data types.

```
12345678910select  event_message,  parsed.error_severity,  parsed.user_namefrom  postgres_logs  -- extract first layer  cross join unnest(postgres_logs.metadata) as metadata  -- extract second layer  cross join unnest(metadata.parsed) as parsed;
```

## Expanding results[#](#expanding-results)

Logs returned by queries may be difficult to read in table format. A row can be double-clicked to expand the results into more readable JSON:

![Expanding log results](https://supabase.com/docs/img/guides/platform/expanded-log-results.png)

## Filtering with [regular expressions](https://en.wikipedia.org/wiki/Regular_expression)[#](#filtering-with-regular-expressions)

The Logs use BigQuery Style regular expressions with the [regexp\_contains function](https://cloud.google.com/bigquery/docs/reference/standard-sql/string_functions#regexp_contains). In its most basic form, it will check if a string is present in a specified column.

```
123456select  cast(timestamp as datetime) as timestamp,  event_message,  metadatafrom postgres_logswhere regexp_contains(event_message, 'is present');
```

There are multiple operators that you should consider using:

### Find messages that start with a phrase[#](#find-messages-that-start-with-a-phrase)

`^` only looks for values at the start of a string

```
12-- find only messages that start with connectionregexp_contains(event_message, '^connection')
```

### Find messages that end with a phrase:[#](#find-messages-that-end-with-a-phrase)

`$` only looks for values at the end of the string

```
12-- find only messages that ends with port=12345regexp_contains(event_message, '$port=12345')
```

### Ignore case sensitivity:[#](#ignore-case-sensitivity)

`(?i)` ignores capitalization for all proceeding characters

```
12-- find all event_messages with the word "connection"regexp_contains(event_message, '(?i)COnnecTion')
```

### Wildcards:[#](#wildcards)

`.` can represent any string of characters

```
12-- find event_messages like "hello<anything>world"regexp_contains(event_message, 'hello.world')
```

### Alphanumeric ranges:[#](#alphanumeric-ranges)

`[1-9a-zA-Z]` finds any strings with only numbers and letters

```
12-- find event_messages that contain a number between 1 and 5 (inclusive)regexp_contains(event_message, '[1-5]')
```

### Repeated values:[#](#repeated-values)

`x*` zero or more x `x+` one or more x `x?` zero or one x `x{4,}` four or more x `x{3}` exactly 3 x

```
12-- find event_messages that contains any sequence of 3 digitsregexp_contains(event_message, '[0-9]{3}')
```

### Escaping reserved characters:[#](#escaping-reserved-characters)

`\.` interpreted as period `.` instead of as a wildcard

```
12-- escapes .regexp_contains(event_message, 'hello world\.')
```

### `or` statements:[#](#or-statements)

`x|y` any string with `x` or `y` present

```
12-- find event_messages that have the word 'started' followed by either the word "host" or "authenticated"regexp_contains(event_message, 'started host|authenticated')
```

### `and`/`or`/`not` statements in SQL:[#](#and--or--not-statements-in-sql)

`and`, `or`, and `not` are all native terms in SQL and can be used in conjunction with regular expressions to filter results

```
12345678select  cast(timestamp as datetime) as timestamp,  event_message,  metadatafrom postgres_logswhere  (regexp_contains(event_message, 'connection') and regexp_contains(event_message, 'host'))  or not regexp_contains(event_message, 'received');
```

### Filtering and unnesting example[#](#filtering-and-unnesting-example)

**Filter for Postgres**

```
123456789101112select  cast(postgres_logs.timestamp as datetime) as timestamp,  parsed.error_severity,  parsed.user_name,  event_messagefrom  postgres_logs  cross join unnest(metadata) as metadata  cross join unnest(metadata.parsed) as parsedwhere regexp_contains(parsed.error_severity, 'ERROR|FATAL|PANIC')order by timestamp desclimit 100;
```

## Limitations[#](#limitations)

### Log tables cannot be joined together[#](#log-tables-cannot-be-joined-together)

Each product table operates independently without the ability to join with other log tables. This may change in the future.

### The `with` keyword and subqueries are not supported[#](#the-with-keyword-and-subqueries-are-not-supported)

The parser does not yet support `with` and subquery statements.

### The `ilike` and `similar to` keywords are not supported[#](#the-ilike-and-similar-to-keywords-are-not-supported)

Although `like` and other comparison operators can be used, `ilike` and `similar to` are incompatible with BigQuery's variant of SQL. `regexp_contains` can be used as an alternative.

### The wildcard operator `*` to select columns is not supported[#](#the-wildcard-operator--to-select-columns-is-not-supported)

The log parser is not able to parse the `*` operator for column selection. Instead, you can access all fields from the `metadata` column:

```
12345678select  cast(postgres_logs.timestamp as datetime) as timestamp,  event_message,  metadatafrom  <log_table_name>order by timestamp desclimit 100;
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/telemetry/advanced-log-filtering.mdx)

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