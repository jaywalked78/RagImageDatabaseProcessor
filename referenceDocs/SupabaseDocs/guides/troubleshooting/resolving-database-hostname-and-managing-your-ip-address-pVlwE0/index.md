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

# Resolving database hostname and managing your IP address

Last edited: 2/4/2025

* * *

### Finding your database hostname[#](#finding-your-database-hostname)

Your database's hostname is crucial for establishing a direct connection. It resolves to the underlying IP address of your database. To find your hostname, navigate to your [Database Settings](https://supabase.com/dashboard/project/_/settings/database). It's important to note that the pooler (connection pooler) has a different IP than your database. Therefore, to reveal the database host and direct connection string, you must hide the pooler connection string.

Example Hostname: `db.zcjtzmeifsoteyjytnbc.supabase.co`

![Screenshot 2024-04-02 at 11 38 28 AM](https://supabase.com/docs/img/troubleshooting/565c96e0-cbb9-4e7a-b0aa-5b423afc0ada.png)

### Managing your IP address[#](#managing-your-ip-address)

To determine your current IP address, you can use an [IP address lookup](https://whatismyipaddress.com/hostname-ip) website or the terminal command:

-   Type `nslookup hostname` and press Enter.
-   This command queries the domain name servers to find the IP address of the given hostname.

Example IPv6 Address: `2a05:d014:1c06:5f0c:d7a9:8616:bee2:30df`

### IPv6 address[#](#ipv6-address)

Upon project creation, a static IPv6 address is assigned. However, it's essential to understand that this IPv6 address can change due to specific actions:

-   When a project is paused or resumed.
-   During database version upgrades.

### IPv4 address[#](#ipv4-address)

Opting for the static [IPv4 add-on](https://supabase.com/docs/guides/platform/ipv4-address) provides a more stable connection address. The IPv4 address remains constant unless:

-   The project is paused or resumed.
-   Unlike the IPv6 address, upgrading your database does not affect the IPv4 address.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[hostname](https://supabase.com/docs/guides/troubleshooting?tags=hostname)[ip](https://supabase.com/docs/guides/troubleshooting?tags=ip)[ipv4](https://supabase.com/docs/guides/troubleshooting?tags=ipv4)[ipv6](https://supabase.com/docs/guides/troubleshooting?tags=ipv6)

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