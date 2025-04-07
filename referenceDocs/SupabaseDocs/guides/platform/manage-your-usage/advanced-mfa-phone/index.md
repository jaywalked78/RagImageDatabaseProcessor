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

7.  [MFA Phone](https://supabase.com/docs/guides/platform/manage-your-usage/advanced-mfa-phone)

# 

Manage Advanced MFA Phone usage

* * *

## What you are charged for[#](#what-you-are-charged-for)

You are charged for having the feature [Advanced Multi-Factor Authentication Phone](https://supabase.com/docs/guides/auth/auth-mfa/phone) enabled for your project.

Additional charges apply for each SMS or WhatsApp message sent, depending on your third-party messaging provider (such as Twilio or MessageBird).

## How charges are calculated[#](#how-charges-are-calculated)

MFA Phone is charged by the hour, meaning you are charged for the exact number of hours that the feature is enabled for a project. If the feature is enabled for part of an hour, you are still charged for the full hour.

### Example[#](#example)

Your billing cycle runs from January 1 to January 31. On January 10 at 4:30 PM, you enable the MFA Phone feature for your project. At the end of the billing cycle you are billed for 512 hours.

| Time Window | MFA Phone | Hours Billed | Description |
| --- | --- | --- | --- |
| January 1, 00:00 AM - January 10, 4:00 PM | Disabled | 0 |  |
| January 10, 04:00 PM - January 10, 4:30 PM | Disabled | 0 |  |
| January 10, 04:30 PM - January 10, 5:00 PM | Enabled | 1 | full hour is billed |
| January 10, 05:00 PM - January 31, 23:59 PM | Enabled | 511 |  |

### Usage on your invoice[#](#usage-on-your-invoice)

Usage is shown as "Auth MFA Phone Hours" on your invoice.

## Pricing[#](#pricing)

$0.1027 per hour ($75 per month) for the first project. $0.0137 per hour ($10 per month) for every additional project.

| Plan | Project 1 per month | Project 2 per month | Project 3 per month |
| --- | --- | --- | --- |
| Pro | $75 | $10 | $10 |
| Team | $75 | $10 | $10 |
| Enterprise | Custom | Custom | Custom |

## Billing examples[#](#billing-examples)

### One project[#](#one-project)

The project has MFA Phone activated throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
| Compute Hours Micro Project 1 | 744 | $10 |
| MFA Phone Hours | 744 | $75 |
| **Subtotal** |  | **$110** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$100** |

### Multiple projects[#](#multiple-projects)

All projects have MFA Phone activated throughout the entire billing cycle.

| Line Item | Hours | Costs |
| --- | --- | --- |
| Pro Plan | \- | $25 |
|  |  |  |
| Compute Hours Micro Project 1 | 744 | $10 |
| MFA Phone Hours Project 1 | 744 | $75 |
|  |  |  |
| Compute Hours Micro Project 2 | 744 | $10 |
| MFA Phone Hours Project 2 | 744 | $10 |
|  |  |  |
| Compute Hours Micro Project 3 | 744 | $10 |
| MFA Phone Hours Project 3 | 744 | $10 |
|  |  |  |
| **Subtotal** |  | **$150** |
| Compute Credits |  | \-$10 |
| **Total** |  | **$140** |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/advanced-mfa-phone.mdx)

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