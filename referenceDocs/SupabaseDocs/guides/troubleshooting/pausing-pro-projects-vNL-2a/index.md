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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Pausing Pro-Projects

Last edited: 2/12/2025

* * *

Pro-Projects at the moment cannot be paused. However, [You are allowed to have two free organizations](https://supabase.com/docs/guides/platform/billing-on-supabase#free-plan) that can support one active project each and an unlimited amount of paused ones.

If a project is under 500MB, you can [transfer it to be under a free organization](https://supabase.com/docs/guides/platform/project-transfer). Afterwards, you can initiate a pause.

Alternatively, you can download a [daily backup](https://supabase.com/dashboard/project/_/database/backups/scheduled) of just your database for archiving. You can also manually download a .SQL file of your database and storage buckets by following this [guide](https://supabase.com/docs/guides/platform/migrating-and-upgrading-projects#migrate-your-project).

You can also download your storage buckets with the [Supabase CLI:](https://supabase.com/docs/guides/cli/getting-started?queryGroups=platform&platform=npx)

```
123456789npx supabase login# link to your projectnpx supabase linknpx supabase init# will download files to current foldernpx supabase storage cp -r ss://bucket . --experimental
```

## Metadata

* * *

### Products

[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Cli](https://supabase.com/docs/guides/troubleshooting?products=cli)[Storage](https://supabase.com/docs/guides/troubleshooting?products=storage)

* * *

### Tags

[pause](https://supabase.com/docs/guides/troubleshooting?tags=pause)[projects](https://supabase.com/docs/guides/troubleshooting?tags=projects)[backup](https://supabase.com/docs/guides/troubleshooting?tags=backup)[storage](https://supabase.com/docs/guides/troubleshooting?tags=storage)

* * *

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