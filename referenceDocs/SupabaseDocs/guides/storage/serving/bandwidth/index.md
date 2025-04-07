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

3.  Serving

5.  [Bandwidth & Storage Egress](https://supabase.com/docs/guides/storage/serving/bandwidth)

# 

Bandwidth & Storage Egress

## 

Bandwidth & Storage Egress

* * *

## Bandwidth & Storage egress[#](#bandwidth--storage-egress)

Free Plan Organizations in Supabase have a limit of 5 GB of bandwidth. This limit is calculated by the sum of all the data transferred from the Supabase servers to the client. This includes all the data transferred from the database, storage, and functions.

### Checking Storage egress requests in Logs Explorer:[#](#checking-storage-egress-requests-in-logs-explorer)

We have a template query that you can use to get the number of requests for each object in [Logs Explorer](https://supabase.com/dashboard/project/_/logs/explorer/templates).

```
12345678910111213select  r.method as http_verb,  r.path as filepath,  count(*) as num_requestsfrom  edge_logs  cross join unnest(metadata) as m  cross join unnest(m.request) as r  cross join unnest(r.headers) as hwhere (path like '%storage/v1/object/%' or path like '%storage/v1/render/%') and r.method = 'GET'group by r.path, r.methodorder by num_requests desclimit 100;
```

Example of the output:

```
12345678910[    {"filepath":"/storage/v1/object/sign/large%20bucket/20230902_200037.gif",    "http_verb":"GET",    "num_requests":100    },    {"filepath":"/storage/v1/object/public/demob/Sports/volleyball.png",    "http_verb":"GET",    "num_requests":168    }]
```

### Calculating egress:[#](#calculating-egress)

If you already know the size of those files, you can calculate the egress by multiplying the number of requests by the size of the file. You can also get the size of the file with the following cURL:

```
1curl -s -w "%{size_download}\n" -o /dev/null "https://my_project.supabase.co/storage/v1/object/large%20bucket/20230902_200037.gif"
```

This will return the size of the file in bytes. For this example, let's say that `20230902_200037.gif` has a file size of 3 megabytes and `volleyball.png` has a file size of 570 kilobytes.

Now, we have to sum all the egress for all the files to get the total egress:

```
123100 * 3MB = 300MB168 * 570KB = 95.76MBTotal Egress = 395.76MB
```

You can see that these values can get quite large, so it's important to keep track of the egress and optimize the files.

### Optimizing egress:[#](#optimizing-egress)

If you are on the Pro Plan, you can use the [Supabase Image Transformations](https://supabase.com/docs/guides/storage/image-transformations) to optimize the images and reduce the egress.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/storage/serving/bandwidth.mdx)

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