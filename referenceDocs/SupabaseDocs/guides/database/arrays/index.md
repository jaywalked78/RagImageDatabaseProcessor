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

3.  Working with your database (basics)

5.  [Working with arrays](https://supabase.com/docs/guides/database/arrays)

# 

Working With Arrays

* * *

Postgres supports flexible [array types](https://www.postgresql.org/docs/12/arrays.html). These arrays are also supported in the Supabase Dashboard and in the JavaScript API.

## Create a table with an array column[#](#create-a-table-with-an-array-column)

Create a test table with a text array (an array of strings):

DashboardSQL

1.  Go to the [Table editor](https://supabase.com/dashboard/project/_/editor) page in the Dashboard.
2.  Click **New Table** and create a table with the name `arraytest`.
3.  Click **Save**.
4.  Click **New Column** and create a column with the name `textarray`, type `text`, and select **Define as array**.
5.  Click **Save**.

## Insert a record with an array value[#](#insert-a-record-with-an-array-value)

DashboardSQLJavaScriptSwiftPython

1.  Go to the [Table editor](https://supabase.com/dashboard/project/_/editor) page in the Dashboard.
2.  Select the `arraytest` table.
3.  Click **Insert row** and add `["Harry", "Larry", "Moe"]`.
4.  Click **Save.**

## View the results[#](#view-the-results)

DashboardSQL

1.  Go to the [Table editor](https://supabase.com/dashboard/project/_/editor) page in the Dashboard.
2.  Select the `arraytest` table.

You should see:

```
123| id  | textarray               || --- | ----------------------- || 1   | ["Harry","Larry","Moe"] |
```

## Query array data[#](#query-array-data)

Postgres uses 1-based indexing (e.g., `textarray[1]` is the first item in the array).

SQLJavaScriptSwift

To select the first item from the array and get the total length of the array:

```
1SELECT textarray[1], array_length(textarray, 1) FROM arraytest;
```

returns:

```
123| textarray | array_length || --------- | ------------ || Harry     | 3            |
```

## Resources[#](#resources)

-   [Supabase JS Client](https://github.com/supabase/supabase-js)
-   [Supabase - Get started for free](https://supabase.com)
-   [Postgres Arrays](https://www.postgresql.org/docs/15/arrays.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/arrays.mdx)

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