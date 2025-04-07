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

# Certain operations are too complex to perform directly using the client libraries.

Last edited: 2/21/2025

* * *

**Solution** In cases where operations are overly complex or not feasible to implement directly using the client libraries, it might be beneficial to leverage stored functions within your database.

Follow these steps to create and run a stored function:

**Create the Stored Function:**

Go to the [SQL query editor](https://supabase.com/dashboard/project/_/sql/new) on your database dashboard. Run the following SQL script to create a stored function tailored to your specific complex query:

```
12345678910111213141516DROP FUNCTION IF EXISTS get_my_complex_query;CREATE FUNCTION get_my_complex_query(parameter INT)RETURNS TABLE (column1 INTEGER, column2 VARCHAR, column3 DATE) AS$$BEGIN    RETURN QUERY    SELECT t1.column1, t1.column2, t2.column3    FROM "TableName1" AS t1    INNER JOIN "TableName2" AS t2 ON t1.column = t2.column    INNER JOIN "TableName3" AS t3 ON t2.another_column = t3.another_column    LEFT JOIN "TableName4" AS t4 ON t3.some_column = t4.some_column    WHERE t2.column = parameter    AND t3.column_name = 'some_value';END;$$LANGUAGE plpgsql VOLATILE;
```

**Call the Stored Function:**

Use the supabase.rpc method to call the stored function from your application code. Replace "get\_my\_complex\_query" with the appropriate function name and provide the necessary parameters:

```
1234567supabase.rpc("get_my_complex_query", { parameter: 1 })  .then(response => {    // Handle the response  })  .catch(error => {    // Handle errors  });
```

**Further Resources:**

For more information on Postgres database functions, refer to the following resource: [Supabase Stored Procedures](https://supabase.com/docs/guides/database/functions#quick-demo)

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[stored](https://supabase.com/docs/guides/troubleshooting?tags=stored)[function](https://supabase.com/docs/guides/troubleshooting?tags=function)[complex](https://supabase.com/docs/guides/troubleshooting?tags=complex)

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