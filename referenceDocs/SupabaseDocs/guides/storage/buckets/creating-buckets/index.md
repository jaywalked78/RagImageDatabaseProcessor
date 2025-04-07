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

3.  Buckets

5.  [Creating Buckets](https://supabase.com/docs/guides/storage/buckets/creating-buckets)

# 

Creating Buckets

* * *

You can create a bucket using the Supabase Dashboard. Since storage is interoperable with your Postgres database, you can also use SQL or our client libraries. Here we create a bucket called "avatars":

JavaScriptDashboardSQLDartSwiftPython

```
12345// Use the JS library to create a bucket.const { data, error } = await supabase.storage.createBucket('avatars', {  public: true, // default: false})
```

[Reference.](https://supabase.com/docs/reference/javascript/storage-createbucket)

## Restricting uploads[#](#restricting-uploads)

When creating a bucket you can add additional configurations to restrict the type or size of files you want this bucket to contain. For example, imagine you want to allow your users to upload only images to the `avatars` bucket and the size must not be greater than 1MB.

You can achieve the following by providing: `allowedMimeTypes` and `maxFileSize`

```
1234567// Use the JS library to create a bucket.const { data, error } = await supabase.storage.createBucket('avatars', {  public: true,  allowedMimeTypes: ['image/*'],  fileSizeLimit: '1MB',})
```

If an upload request doesn't meet the above restrictions it will be rejected.

For more information check [File Limits](https://supabase.com/docs/guides/storage/uploads/file-limits) Section.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/buckets/creating-buckets.mdx)

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