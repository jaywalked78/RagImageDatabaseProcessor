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

5.  [Ownership](https://supabase.com/docs/guides/storage/security/ownership)

# 

Ownership

* * *

When creating new buckets or objects in Supabase Storage, an owner is automatically assigned to the bucket or object. The owner is the user who created the resource and the value is derived from the `sub` claim in the JWT. We store the `owner` in the `owner_id` column.

When using the `service_key` to create a resource, the owner will not be set and the resource will be owned by anyone. This is also the case when you are creating Storage resources via the Dashboard.

The Storage schema has 2 fields to represent ownership: `owner` and `owner_id`. `owner` is deprecated and will be removed. Use `owner_id` instead.

## Access control[#](#access-control)

By itself, the ownership of a resource does not provide any access control. However, you can enforce the ownership by implementing access control against storage resources scoped to their owner.

For example, you can implement a policy where only the owner of an object can delete it. To do this, check the `owner_id` field of the object and compare it with the `sub` claim of the JWT:

```
1234567create policy "User can delete their own objects"on storage.objectsfor deleteto authenticatedusing (    owner_id = (select auth.uid()));
```

The use of RLS policies is just one way to enforce access control. You can also implement access control in your server code by following the same pattern.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/security/ownership.mdx)

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