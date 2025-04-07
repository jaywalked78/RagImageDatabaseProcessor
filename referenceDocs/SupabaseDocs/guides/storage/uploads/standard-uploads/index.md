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

3.  Uploads

5.  [Standard Uploads](https://supabase.com/docs/guides/storage/uploads/standard-uploads)

# 

Standard Uploads

## 

Learn how to upload files to Supabase Storage.

* * *

## Uploading[#](#uploading)

The standard file upload method is ideal for small files that are not larger than 6MB.

It uses the traditional `multipart/form-data` format and is simple to implement using the supabase-js SDK. Here's an example of how to upload a file using the standard upload method:

Though you can upload up to 5GB files using the standard upload method, we recommend using [TUS Resumable Upload](https://supabase.com/docs/guides/storage/uploads/resumable-uploads) for uploading files greater than 6MB in size for better reliability.

JavaScriptDartSwiftKotlinPython

```
1234567891011121314import { createClient } from '@supabase/supabase-js'// Create Supabase clientconst supabase = createClient('your_project_url', 'your_supabase_api_key')// Upload file using standard uploadasync function uploadFile(file) {  const { data, error } = await supabase.storage.from('bucket_name').upload('file_path', file)  if (error) {    // Handle error  } else {    // Handle success  }}
```

## Overwriting files[#](#overwriting-files)

When uploading a file to a path that already exists, the default behavior is to return a `400 Asset Already Exists` error. If you want to overwrite a file on a specific path you can set the `upsert` options to `true` or using the `x-upsert` header.

JavaScriptDartSwiftKotlinPython

```
123456// Create Supabase clientconst supabase = createClient('your_project_url', 'your_supabase_api_key')await supabase.storage.from('bucket_name').upload('file_path', file, {  upsert: true,})
```

We do advise against overwriting files when possible, as our Content Delivery Network will take sometime to propagate the changes to all the edge nodes leading to stale content. Uploading a file to a new path is the recommended way to avoid propagation delays and stale content.

## Content type[#](#content-type)

By default, Storage will assume the content type of an asset from the file extension. If you want to specify the content type for your asset, pass the `contentType` option during upload.

JavaScriptDartSwiftKotlinPython

```
123456// Create Supabase clientconst supabase = createClient('your_project_url', 'your_supabase_api_key')await supabase.storage.from('bucket_name').upload('file_path', file, {  contentType: 'image/jpeg',})
```

## Concurrency[#](#concurrency)

When two or more clients upload a file to the same path, the first client to complete the upload will succeed and the other clients will receive a `400 Asset Already Exists` error. If you provide the `x-upsert` header the last client to complete the upload will succeed instead.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/uploads/standard-uploads.mdx)

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