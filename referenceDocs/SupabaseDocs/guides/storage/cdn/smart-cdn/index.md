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

3.  CDN

5.  [Smart CDN](https://supabase.com/docs/guides/storage/cdn/smart-cdn)

# 

Smart CDN

* * *

With Smart CDN caching enabled, the asset metadata in your database is synchronized to the edge. This automatically revalidates the cache when the asset is changed or deleted.

Moreover, the Smart CDN achieves a greater cache hit rate by shielding the origin server from asset requests that remain unchanged, even when different query strings are used in the URL.

Smart CDN caching is automatically enabled for [Pro Plan and above](https://supabase.com/pricing).

## Cache duration[#](#cache-duration)

When Smart CDN is enabled, the asset is cached on the CDN for as long as possible. You can still control how long assets are stored in the browser using the [`cacheControl`](https://supabase.com/docs/reference/javascript/storage-from-upload) option when uploading a file. Smart CDN caching works with all types of storage operations including signed URLs.

When a file is updated or deleted, the CDN cache is automatically invalidated to reflect the change (including transformed images). It can take **up to 60 seconds** for the CDN cache to be invalidated as the asset metadata has to propagate across all the data-centers around the globe.

When an asset is invalidated at the CDN level, browsers may not update its cache. This is where cache eviction comes into play.

## Cache eviction[#](#cache-eviction)

Even when an asset is marked as invalidated at the CDN level, browsers may not refresh their cache for that asset.

If you have assets that undergo frequent updates, it is advisable to upload the new asset to a different path. This approach ensures that you always have the most up-to-date asset accessible.

If you anticipate that your asset might be deleted, it's advisable to set a shorter browser Time-to-Live (TTL) value using the `cacheControl` option. The default TTL is typically set to 1 hour, which is generally a reasonable default value.

## Bypassing cache[#](#bypassing-cache)

If you need to ensure assets refresh directly from the origin server and bypass the cache, you can achieve this by adding a unique query string to the URL.

For instance, you can use a URL like `/storage/v1/object/sign/profile-pictures/cat.jpg?version=1` with a long browser cache (e.g., 1 year). To update the picture, increment the version query parameter in the URL, like `/storage/v1/object/sign/profile-pictures/cat.jpg?version=2`. The CDN will recognize it as a new object and fetch the updated version from the origin.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/cdn/smart-cdn.mdx)

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