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

3.  Configuration, optimization, and testing

5.  [Database configuration](https://supabase.com/docs/guides/database/postgres/configuration)

# 

Database configuration

## 

Updating the default configuration for your Postgres database.

* * *

Postgres provides a set of sensible defaults for you database size. In some cases, these defaults can be updated. We do not recommend changing these defaults unless you know what you're doing.

## Timeouts[#](#timeouts)

See the [Timeouts](https://supabase.com/docs/guides/database/postgres/timeouts) section.

## Statement optimization[#](#statement-optimization)

All Supabase projects come with the [`pg_stat_statements`](https://www.postgresql.org/docs/current/pgstatstatements.html) extension installed, which tracks planning and execution statistics for all statements executed against it. These statistics can be used in order to diagnose the performance of your project.

This data can further be used in conjunction with the [`explain`](https://www.postgresql.org/docs/current/using-explain.html) functionality of Postgres to optimize your usage.

## Managing timezones[#](#managing-timezones)

Every Supabase database is set to UTC timezone by default. We strongly recommend keeping it this way, even if your users are in a different location. This is because it makes it much easier to calculate differences between timezones if you adopt the mental model that everything in your database is in UTC time.

### Change timezone[#](#change-timezone)

SQL

```
12alter database postgresset timezone to 'America/New_York';
```

### Full list of timezones[#](#full-list-of-timezones)

Get a full list of timezones supported by your database. This will return the following columns:

-   `name`: Time zone name
-   `abbrev`: Time zone abbreviation
-   `utc_offset`: Offset from UTC (positive means east of Greenwich)
-   `is_dst`: True if currently observing daylight savings

SQL

```
123select name, abbrev, utc_offset, is_dstfrom pg_timezone_names()order by name;
```

### Search for a specific timezone[#](#search-for-a-specific-timezone)

Use `ilike` (case insensitive search) to find specific timezones.

SQL

```
123select *from pg_timezone_names()where name ilike '%york%';
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/configuration.mdx)

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