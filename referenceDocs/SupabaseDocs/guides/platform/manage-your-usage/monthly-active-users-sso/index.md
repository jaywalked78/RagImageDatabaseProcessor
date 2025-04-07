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

7.  [Monthly Active SSO Users](https://supabase.com/docs/guides/platform/manage-your-usage/monthly-active-users-sso)

# 

Manage Monthly Active SSO Users usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for the number of distinct users who log in or refresh their token during the billing cycle using a SAML 2.0 compatible identity provider. Each unique user is counted only once per billing cycle, regardless of how many times they authenticate. These users are referred to as "SSO MAUs".

### Example[#](#example)

Your billing cycle runs from January 1 to January 31. Although User-1 was signed in multiple times, they are counted as a single SSO MAU for this billing cycle.

1

### Sign User-1 in on January 3

The SSO MAU count increases from 0 to 1.

```
12345678const { data, error } = await supabase.auth.signInWithSSO({domain: 'company.com'})if (data?.url) {// redirect User-1 to the identity provider's authentication flowwindow.location.href = data.url}
```

2

### Sign User-1 out on January 4

`javascript const {error} = await supabase.auth.signOut()`

3

### Sign User-1 in again on January 17

The SSO MAU count remains 1.

```
12345678const { data, error } = await supabase.auth.signInWithSSO({domain: 'company.com'})if (data?.url) {// redirect User-1 to the identity provider's authentication flowwindow.location.href = data.url}
```

## How charges are calculated[#](#how-charges-are-calculated)

You are charged by SSO MAU.

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Monthly Active SSO Users" on your invoice.

## Pricing[#](#pricing)

$0.015 per SSO MAU. You are only charged for usage exceeding your subscription plan's quota.

The count resets at the start of each billing cycle.

| Plan | Quota | Over-Usage |
| --- | --- | --- |
| Pro | 50 | $0.015 per SSO MAU |
| Team | 50 | $0.015 per SSO MAU |
| Enterprise | Custom | Custom |

## Billing examples[#](#billing-examples)

### Within quota[#](#within-quota)

The organization's SSO MAU usage for the billing cycle is within the quota, so no charges apply.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Monthly Active SSO Users | 37 SSO MAU | $0 |
| **Subtotal** |  | **$35** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25** |

### Exceeding quota[#](#exceeding-quota)

The organization's SSO MAU usage for the billing cycle exceeds the quota by 10, incurring charges for this additional usage.

| Line Item | Units | Costs |
| --- | --- | --- |
| Pro Plan | 1 | $25 |
| Compute Hours Micro | 744 hours | $10 |
| Monthly Active SSO Users | 60 SSO MAU | $0.15 |
| **Subtotal** |  | **$35.15** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$25.15** |

## View usage[#](#view-usage)

You can view Monthly Active SSO Users usage on the [organization's usage page](https://supabase.com/dashboard/org/_/usage). The page shows the usage of all projects by default. To view the usage for a specific project, select it from the dropdown. You can also select a different time period.

In the Monthly Active SSO Users section, you can see the usage for the selected time period.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/monthly-active-users-sso.mdx)

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