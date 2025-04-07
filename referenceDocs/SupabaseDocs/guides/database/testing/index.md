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

5.  [Testing your database](https://supabase.com/docs/guides/database/testing)

# 

Testing Your Database

* * *

To ensure that queries return the expected data, RLS policies are correctly applied and etc., we encourage you to write automated tests. There are essentially two approaches to testing:

-   Firstly, you can write tests that interface with a Supabase client instance (same way you use Supabase client in your application code) in the programming language(s) you use in your application and using your favorite testing framework.
    
-   Secondly, you can test through the Supabase CLI, which is a more low-level approach where you write tests in SQL.
    

# Testing using the Supabase CLI

You can use the Supabase CLI to test your database. The minimum required version of the CLI is [v1.11.4](https://github.com/supabase/cli/releases). To get started:

-   [Install the Supabase CLI](https://supabase.com/docs/guides/cli) on your local machine

## Creating a test[#](#creating-a-test)

Create a tests folder inside the `supabase` folder:

```
1mkdir -p ./supabase/tests/database
```

Create a new file with the `.sql` extension which will contain the test.

```
1touch ./supabase/tests/database/hello_world.test.sql
```

## Writing tests[#](#writing-tests)

All `sql` files use [pgTAP](https://supabase.com/docs/guides/database/extensions/pgtap) as the test runner.

Let's write a simple test to check that our `auth.users` table has an ID column. Open `hello_world.test.sql` and add the following code:

```
123456789101112begin;select plan(1); -- only one statement to runSELECT has_column(    'auth',    'users',    'id',    'id should exist');select * from finish();rollback;
```

## Running tests[#](#running-tests)

To run the test, you can use:

```
1supabase test db
```

This will produce the following output:

```
12345$ supabase test dbsupabase/tests/database/hello_world.test.sql .. okAll tests successful.Files=1, Tests=1,  1 wallclock secs ( 0.01 usr  0.00 sys +  0.04 cusr  0.02 csys =  0.07 CPU)Result: PASS
```

## More resources[#](#more-resources)

-   [Testing RLS policies](https://supabase.com/docs/guides/database/extensions/pgtap#testing-rls-policies)
-   [pgTAP extension](https://supabase.com/docs/guides/database/extensions/pgtap)
-   Official [pgTAP documentation](https://pgtap.org/)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/testing.mdx)

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