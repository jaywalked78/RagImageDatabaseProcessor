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

3.  Going to production

5.  [Scaling](https://supabase.com/docs/guides/storage/production/scaling)

# 

Storage Optimizations

## 

Scaling Storage

* * *

Here are some optimizations that you can consider to improve performance and reduce costs as you start scaling Storage.

## Egress[#](#egress)

If your project has high egress, these optimizations can help reducing it.

#### Resize images[#](#resize-images)

Images typically make up most of your egress. By keeping them as small as possible, you can cut down on egress and boost your application's performance. You can take advantage of our [Image Transformation](https://supabase.com/docs/guides/storage/serving/image-transformations) service to optimize any image on the fly.

#### Set a high cache-control value[#](#set-a-high-cache-control-value)

Using the browser cache can effectively lower your egress since the asset remains stored in the user's browser after the initial download. Setting a high `cache-control` value ensures the asset stays in the user's browser for an extended period, decreasing the need to download it from the server repeatedly. Read more [here](https://supabase.com/docs/guides/storage/cdn/smart-cdn#cache-duration)

#### Limit the upload size[#](#limit-the-upload-size)

You have the option to set a maximum upload size for your bucket. Doing this can prevent users from uploading and then downloading excessively large files. You can control the maximum file size by configuring this option at the [bucket level](https://supabase.com/docs/guides/storage/buckets/creating-buckets).

## Optimize listing objects[#](#optimize-listing-objects)

Once you have a substantial number of objects, you might observe that the `supabase.storage.list()` method starts to slow down. This occurs because the endpoint is quite generic and attempts to retrieve both folders and objects in a single query. While this approach is very useful for building features like the Storage viewer on the Supabase dashboard, it can impact performance with a large number of objects.

If your application doesn't need the entire hierarchy computed you can speed up drastically the query execution for listing your objects by creating a Postgres function as following:

```
1234567891011121314151617181920212223242526272829create or replace function list_objects(    bucketid text,    prefix text,    limits int default 100,    offsets int default 0) returns table (    name text,    id uuid,    updated_at timestamptz,    created_at timestamptz,    last_accessed_at timestamptz,    metadata jsonb) as $$begin    return query SELECT        objects.name,        objects.id,        objects.updated_at,        objects.created_at,        objects.last_accessed_at,        objects.metadata    FROM storage.objects    WHERE objects.name like prefix || '%'    AND bucket_id = bucketid    ORDER BY name ASC    LIMIT limits    OFFSET offsets;end;$$ language plpgsql stable;
```

You can then use the your Postgres function as following:

Using SQL:

```
1select * from list_objects('bucket_id', '', 100, 0);
```

Using the SDK:

```
123456const { data, error } = await supabase.rpc('list_objects', {  bucketid: 'yourbucket',  prefix: '',  limit: 100,  offset: 0,})
```

## Optimizing RLS[#](#optimizing-rls)

When creating RLS policies against the storage tables you can add indexes to the interested columns to speed up the lookup

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/production/scaling.mdx)

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