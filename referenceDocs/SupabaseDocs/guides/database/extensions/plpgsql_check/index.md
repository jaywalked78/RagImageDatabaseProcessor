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

5.  [plpgsql\_check: PL/pgSQL Linter](https://supabase.com/docs/guides/database/extensions/plpgsql_check)

# 

plpgsql\_check: PL/pgSQL Linter

* * *

[plpgsql\_check](https://github.com/okbob/plpgsql_check) is a Postgres extension that lints plpgsql for syntax, semantic and other related issues. The tool helps developers to identify and correct errors before executing the code. plpgsql\_check is most useful for developers who are working with large or complex SQL codebases, as it can help identify and resolve issues early in the development cycle.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "plpgsql\_check" and enable the extension.

## API[#](#api)

-   [`plpgsql_check_function( ... )`](https://github.com/okbob/plpgsql_check#active-mode): Scans a function for errors.

`plpgsql_check_function` is highly customizable. For a complete list of available arguments see [the docs](https://github.com/okbob/plpgsql_check#arguments)

## Usage[#](#usage)

To demonstrate `plpgsql_check` we can create a function with a known error. In this case we create a function `some_func`, that references a non-existent column `place.created_at`.

```
12345678910111213141516171819create table place(  x float,  y float);create or replace function public.some_func()  returns void  language plpgsqlas $$declare  rec record;begin  for rec in select * from place  loop    -- Bug: There is no column `created_at` on table `place`    raise notice '%', rec.created_at;  end loop;end;$$;
```

Note that executing the function would not catch the invalid reference error because the `loop` does not execute if no rows are present in the table.

```
12345select public.some_func();  some_func ─────────── (1 row)
```

Now we can use plpgsql\_check's `plpgsql_check_function` function to identify the known error.

```
123456select plpgsql_check_function('public.some_func()');                   plpgsql_check_function------------------------------------------------------------ error:42703:8:RAISE:record "rec" has no field "created_at" Context: SQL expression "rec.created_at"
```

## Resources[#](#resources)

-   Official [`plpgsql_check` documentation](https://github.com/okbob/plpgsql_check)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/plpgsql_check.mdx)

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