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

Storage

1.  [Storage](https://supabase.com/docs/guides/storage)

3.  Security

5.  [Access Control](https://supabase.com/docs/guides/storage/security/access-control)

# 

Storage Access Control

* * *

Supabase Storage is designed to work perfectly with Postgres [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) (RLS).

You can use RLS to create [Security Access Policies](https://www.postgresql.org/docs/current/sql-createpolicy.html) that are incredibly powerful and flexible, allowing you to restrict access based on your business needs.

## Access policies[#](#access-policies)

By default Storage does not allow any uploads to buckets without RLS policies. You selectively allow certain operations by creating RLS policies on the `storage.objects` table.

You can find the documentation for the storage schema [here](https://supabase.com/docs/guides/storage/schema/design) , and to simplify the process of crafting your policies, you can utilize these [helper functions](https://supabase.com/docs/guides/storage/schema/helper-functions) .

The RLS policies required for different operations are documented [here](https://supabase.com/docs/reference/javascript/storage-createbucket)

For example, the only RLS policy required for [uploading](https://supabase.com/docs/reference/javascript/storage-from-upload) objects is to grant the `INSERT` permission to the `storage.objects` table.

To allow overwriting files using the `upsert` functionality you will need to additionally grant `SELECT` and `UPDATE` permissions.

## Policy examples[#](#policy-examples)

An easy way to get started would be to create RLS policies for `SELECT`, `INSERT`, `UPDATE`, `DELETE` operations and restrict the policies to meet your security requirements. For example, one can start with the following `INSERT` policy:

```
12345create policy "policy_name"ON storage.objectsfor insert with check (  true);
```

and modify it to only allow authenticated users to upload assets to a specific bucket by changing it to:

```
12345create policy "policy_name"on storage.objects for insert to authenticated with check (    -- restrict bucket    bucket_id = 'my_bucket_id');
```

This example demonstrates how you would allow authenticated users to upload files to a folder called `private` inside `my_bucket_id`:

```
12345678create policy "Allow authenticated uploads"on storage.objectsfor insertto authenticatedwith check (  bucket_id = 'my_bucket_id' and  (storage.foldername(name))[1] = 'private');
```

This example demonstrates how you would allow authenticated users to upload files to a folder called with their `users.id` inside `my_bucket_id`:

```
12345678create policy "Allow authenticated uploads"on storage.objectsfor insertto authenticatedwith check (  bucket_id = 'my_bucket_id' and  (storage.foldername(name))[1] = (select auth.uid()::text));
```

Allow a user to access a file that was previously uploaded by the same user:

```
1234create policy "Individual user Access"on storage.objects for selectto authenticatedusing ( (select auth.uid()) = owner_id::uuid );
```

* * *

## Bypassing access controls[#](#bypassing-access-controls)

If you exclusively use Storage from trusted clients, such as your own servers, and need to bypass the RLS policies, you can use the `service key` in the `Authorization` header. Service keys entirely bypass RLS policies, granting you unrestricted access to all Storage APIs.

Remember you should not share the service key publicly.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/security/access-control.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F4ERX__Y908k%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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