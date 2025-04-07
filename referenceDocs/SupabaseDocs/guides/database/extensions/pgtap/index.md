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

5.  [pgTAP: Unit Testing](https://supabase.com/docs/guides/database/extensions/pgtap)

# 

pgTAP: Unit Testing

* * *

`pgTAP` is a unit testing extension for Postgres.

## Overview[#](#overview)

Let's cover some basic concepts:

-   Unit tests: allow you to test small parts of a system (like a database table!).
-   TAP: stands for [Test Anything Protocol](http://testanything.org/). It is an framework which aims to simplify the error reporting during testing.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `pgtap` and enable the extension.

## Testing tables[#](#testing-tables)

```
1234567begin;select plan( 1 );select has_table( 'profiles' );select * from finish();rollback;
```

API:

-   [`has_table()`](https://pgtap.org/documentation.html#has_table): Tests whether or not a table exists in the database
-   [`has_index()`](https://pgtap.org/documentation.html#has_index): Checks for the existence of a named index associated with the named table.
-   [`has_relation()`](https://pgtap.org/documentation.html#has_relation): Tests whether or not a relation exists in the database.

## Testing columns[#](#testing-columns)

```
12345678begin;select plan( 2 );select has_column( 'profiles', 'id' ); -- test that the "id" column exists in the "profiles" tableselect col_is_pk( 'profiles', 'id' ); -- test that the "id" column is a primary keyselect * from finish();rollback;
```

API:

-   [`has_column()`](https://pgtap.org/documentation.html#has_column): Tests whether or not a column exists in a given table, view, materialized view or composite type.
-   [`col_is_pk()`](https://pgtap.org/documentation.html#col_is_pk): Tests whether the specified column or columns in a table is/are the primary key for that table.

## Testing RLS policies[#](#testing-rls-policies)

```
1234567891011121314begin;select plan( 1 );select policies_are(  'public',  'profiles',  ARRAY [    'Profiles are public', -- Test that there is a policy called  "Profiles are public" on the "profiles" table.    'Profiles can only be updated by the owner'  -- Test that there is a policy called  "Profiles can only be updated by the owner" on the "profiles" table.  ]);select * from finish();rollback;
```

API:

-   [`policies_are()`](https://pgtap.org/documentation.html#policies_are): Tests that all of the policies on the named table are only the policies that should be on that table.
-   [`policy_roles_are()`](https://pgtap.org/documentation.html#policy_roles_are): Tests whether the roles to which policy applies are only the roles that should be on that policy.
-   [`policy_cmd_is()`](https://pgtap.org/documentation.html#policy_cmd_is): Tests whether the command to which policy applies is same as command that is given in function arguments.

You can also use the `results_eq()` method to test that a Policy returns the correct data:

```
123456789101112begin;select plan( 1 );select results_eq(    'select * from profiles()',    $$VALUES ( 1, 'Anna'), (2, 'Bruce'), (3, 'Caryn')$$,    'profiles() should return all users');select * from finish();rollback;
```

API:

-   [`results_eq()`](https://pgtap.org/documentation.html#results_eq)
-   [`results_ne()`](https://pgtap.org/documentation.html#results_ne)

## Testing functions[#](#testing-functions)

```
1234567891011prepare hello_expr as select 'hello'begin;select plan(3);-- You'll need to create a hello_world and is_even functionselect function_returns( 'hello_world', 'text' );                   -- test if the function "hello_world" returns textselect function_returns( 'is_even', ARRAY['integer'], 'boolean' );  -- test if the function "is_even" returns a booleanselect results_eq('select * from hello_world()', 'hello_expr');          -- test if the function "hello_world" returns "hello"select * from finish();rollback;
```

API:

-   [`function_returns()`](https://pgtap.org/documentation.html#function_returns): Tests that a particular function returns a particular data type
-   [`is_definer()`](https://pgtap.org/documentation.html#is_definer): Tests that a function is a security definer (that is, a `setuid` function).

## Resources[#](#resources)

-   Official [`pgTAP` documentation](https://pgtap.org/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pgtap.mdx)

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