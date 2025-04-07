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

Platform

1.  [Platform](https://supabase.com/docs/guides/platform)

3.  More

5.  [Manage your usage](https://supabase.com/docs/guides/platform/manage-your-usage)

7.  [Storage Image Transformations](https://supabase.com/docs/guides/platform/manage-your-usage/storage-image-transformations)

# 

Manage Storage Image Transformations usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the number of distinct images transformed during the billing period, regardless of how many transformations each image undergoes. We refer to these images as "origin" images.

### Example[#](#example)

With these four transformations applied to `image-1.jpg` and `image-2.jpg`, the origin images count is 2.

```
123456supabase.storage.from('bucket').createSignedUrl('image-1.jpg', 60000, {  transform: {    width: 200,    height: 200,  },})
```

```
123456supabase.storage.from('bucket').createSignedUrl('image-2.jpg', 60000, {  transform: {    width: 400,    height: 300,  },})
```

```
123456supabase.storage.from('bucket').createSignedUrl('image-2.jpg', 60000, {  transform: {    width: 600,    height: 250,  },})
```

```
123456supabase.storage.from('bucket').download('image-2.jpg', {  transform: {    width: 800,    height: 300,  },})
```

## How charges are calculated[#](#how-charges-are-calculated)

Storage Image Transformations are billed using Package pricing, with each package representing 1000 origin images. If your usage falls between two packages, you are billed for the next whole package.

### Example[#](#example)

For simplicity, let's assume a package size of 1,000 and a charge of $5 per package with no quota.

| Origin Images | Packages Billed | Costs |
| --- | --- | --- |
| 999 | 1 | $5 |
| 1,000 | 1 | $5 |
| 1,001 | 2 | $10 |
| 1,500 | 2 | $10 |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Storage Image Transformations" on your invoice.

## Pricing[#](#pricing)

$5 per 1,000 origin images. You are only charged for usage exceeding your subscription plan's quota.

The count resets at the start of each billing cycle.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Pro | 100 | $5 per 1,000 origin images |
| Team | 100 | $5 per 1,000 origin images |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's number of origin images for the billing cycle is within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Image Transformations | 74 origin images | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's number of origin images for the billing cycle exceeds the quota by 750, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Image Transformations | 850 origin images | $5 |
| **Subtotal** |  | **$40** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$30** |

## View usage[#](#view-usage)

You can view Storage Image Transformations usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Storage Image Transformations section, you can see how many origin images were transformed during the selected time period.

## Optimize usage[#](#optimize-usage)

-   Pre-generate common variants – instead of transforming images on the fly, generate and store commonly used sizes in advance
-   Optimize original image sizes – upload images in an optimized format and resolution to reduce the need for excessive transformations
-   Leverage [Smart CDN](https://supabase.com/docs/guides/storage/cdn/smart-cdn) caching or any other caching solution to serve transformed images efficiently and avoid unnecessary repeated transformations
-   Control how long assets are stored in the browser using the `Cache-Control` header

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/storage-image-transformations.mdx)

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