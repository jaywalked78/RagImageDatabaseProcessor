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

# High latency with supabase client

Last edited: 2/4/2025

* * *

## Describe the bug[#](#describe-the-bug)

Querying a table using the Supabase client is much slower than querying against the Postgres database directly.

## To reproduce[#](#to-reproduce)

1.  Execute the below DDL statements.

```
123456789101112131415161718192021222324252627282930-- Create tableCREATE TABLE your_table_name (    id UUID PRIMARY KEY,    column1 TEXT,    column2 INT,    column3 BOOLEAN);-- Insert statementsINSERT INTO your_table_name (id, column1, column2, column3) VALUES    (uuid_generate_v4(), 'value1', 10, TRUE),    (uuid_generate_v4(), 'value2', 20, FALSE),    (uuid_generate_v4(), 'value3', 15, TRUE),    (uuid_generate_v4(), 'value4', 8, FALSE),    (uuid_generate_v4(), 'value5', 25, TRUE),    (uuid_generate_v4(), 'value6', 12, FALSE),    (uuid_generate_v4(), 'value7', 18, TRUE),    (uuid_generate_v4(), 'value8', 30, FALSE),    (uuid_generate_v4(), 'value9', 22, TRUE),    (uuid_generate_v4(), 'value10', 5, FALSE),    (uuid_generate_v4(), 'value11', 17, TRUE),    (uuid_generate_v4(), 'value12', 9, FALSE),    (uuid_generate_v4(), 'value13', 14, TRUE),    (uuid_generate_v4(), 'value14', 28, FALSE),    (uuid_generate_v4(), 'value15', 11, TRUE),    (uuid_generate_v4(), 'value16', 7, FALSE),    (uuid_generate_v4(), 'value17', 19, TRUE),    (uuid_generate_v4(), 'value18', 26, FALSE),    (uuid_generate_v4(), 'value19', 16, TRUE),    (uuid_generate_v4(), 'value20', 21, FALSE);
```

2.  Run the following script (you may need to `pip install psycopg[binary]` in addition to Supabase client.

```
123456789101112131415161718192021222324252627282930313233343536373839import timefrom supabase import Client, create_clientimport psycopgdef psycop_call(): #user_ids: list[str]):    user="YOUR_SUPABASE_USER"    password="YOUR_SUPABASE_PASSWORD"    host="SUPABASE_HOST"    port=5432    database="postgres"    with psycopg.connect(f"host={host} port={port} dbname={database} user={user} password={password}") as conn:        # Open a cursor to perform database operations        results = []        with conn.cursor() as cur:            start = time.time()            # Execute a command: this creates a new table            cur.execute("SELECT * FROM public.your_table_name")            cur.fetchall()            for record in cur:                results.append(record)            stop = time.time()            return (stop - start)def supabase_call():    supabase: Client = create_client("SUPABASE_URL", "SUPBASE_SERVICE_ROLE_KEY")    start = time.time()    result = supabase.table("your_table_name").select("*").execute()    stop = time.time()    return (stop - start)if __name__ == "__main__":    ref = psycop_call()    sup = supabase_call()    print(f"postgres: {ref}, supabase: {sup}, ratio: {sup/ref}")
```

3.  You will see that the Supabase client takes longer to execute the same query, especially for smaller tables or queries returning just one row.

## Expected behavior[#](#expected-behavior)

The overhead from PostgREST shouldn't be higher than a few milliseconds at max. 60-70 ms is way too high. This is particular deceiving because one can run the query on the SQL Editor page and it reports the same time as the direct Postgres query, which is not what actually happens.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)

* * *

### Tags

[latency](https://supabase.com/docs/guides/troubleshooting?tags=latency)[client](https://supabase.com/docs/guides/troubleshooting?tags=client)[performance](https://supabase.com/docs/guides/troubleshooting?tags=performance)

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