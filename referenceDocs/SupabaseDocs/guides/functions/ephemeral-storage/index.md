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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Guides

5.  [Ephemeral Storage](https://supabase.com/docs/guides/functions/ephemeral-storage)

# 

Ephemeral Storage

## 

Read and write from temporary directory

* * *

Edge Functions provides ephemeral file storage. You can read and write files to the `/tmp` directory.

Ephemeral storage will reset on each function invocation. This means the files you write during an invocation can only be read within the same invocation.

### Use cases[#](#use-cases)

Here are some use cases where ephemeral storage can be useful:

-   Unzip an archive of CSVs and then add them as records to the DB
-   Custom image manipulation workflows (using [`magick-wasm`](https://supabase.com/docs/guides/functions/examples/image-manipulation))

You can use [Background Tasks](https://supabase.com/docs/guides/functions/background-tasks) to handle slow file processing outside of a request.

### How to use[#](#how-to-use)

You can use [Deno File System APIs](https://docs.deno.com/api/deno/file-system) or the [`node:fs` module](https://docs.deno.com/api/node/fs/) to access the `/tmp` path.

### Example[#](#example)

Here is an example of how to write a user-uploaded zip file into temporary storage for further processing.

```
1234567891011121314Deno.serve(async (req) => {  if (req.headers.get('content-type') !== 'application/zip') {    return new Response('file must be a zip file', {      status: 400,    })  }  const uploadId = crypto.randomUUID()  await Deno.writeFile('/tmp/' + uploadId, req.body)  // do something with the written zip file  return new Response('ok')})
```

### Unavailable APIs[#](#unavailable-apis)

Currently, the synchronous APIs (e.g. `Deno.writeFileSync` or `Deno.mkdirSync`) for creating or writing files are not supported.

You can use sync variations of read APIs (e.g. `Deno.readFileSync`).

### Limits[#](#limits)

In the hosted platform, a free project can write up to 256MB of data to ephemeral storage. A paid project can write up to 512MB.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/ephemeral-storage.mdx)

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