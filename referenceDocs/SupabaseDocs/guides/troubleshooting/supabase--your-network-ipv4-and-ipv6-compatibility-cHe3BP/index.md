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

# Supabase & Your Network: IPv4 and IPv6 compatibility

Last edited: 2/4/2025

* * *

# Network compatibility with your Supabase database

The internet uses a system called the Internet Protocol (IP) to route communication between devices. There are two main versions:

-   **IPv4**: Introduced in 1980, it's the original version.
-   **IPv6**: Launched in 1999, it offers a much larger address space and is the preferred future-proof option.

### Supabase and IPv6:[#](#supabase-and-ipv6)

All Supabase databases provide a direct connection string that maps to an IPv6 address.

### Working with IPv6 incompatible hosts:[#](#working-with-ipv6-incompatible-hosts)

Here are your options if your server platform doesn't support IPv6:

-   Use the Supavisor Connection String (available in the [Dashboard](https://supabase.com/dashboard/project/_/settings/database)).
-   Use the [Supabase Client libraries](https://supabase.com/docs/guides/api/rest/client-libs), which are IPv4 compatible.
-   Enable the [dedicated IPv4 Add-On](https://supabase.com/dashboard/project/_/settings/addons) (available to Pro and above organizations)

> Note: the IPv4 Add-On costs $0.0055 an hour, which equates to ~$4.00 if left on for a full month (~720 hours)

### Checking IPv6 support:[#](#checking-ipv6-support)

The majority of services are IPv6 compatible. However, there are a few prominent ones that only accept IPv4 connections:

-   [Retool](https://retool.com/)
-   [Vercel](https://vercel.com/)
-   [GitHub Actions](https://docs.github.com/en/actions)
-   [Render](https://render.com/)

If you're still unsure if your network supports IPv6, you can run this cURL command on your deployment server:

```
1curl -6 https://ifconfig.co/ip
```

If the command returns an IPv6 address, the network is IPv6 compatible.

### Finding your database's IP address:[#](#finding-your-databases-ip-address)

To determine your current IP address, you can use an IP address [lookup website](https://whatismyipaddress.com/hostname-ip) or the terminal command:

```
1nslookup db.<PROJECT_REF>.supabase.co
```

This command queries the domain name servers to find the IP address of the given hostname.

Example IPv6 Address: `2a05:d014:1c06:5f0c:d7a9:8616:bee2:30df`

### Identifying your connections:[#](#identifying-your-connections)

The pooler and direct connection strings can be found in the [database settings](https://supabase.com/dashboard/project/_/settings/database):

> "Note uses an IPv6 address by default

```
12# Example connection stringpostgresql://postgres:[YOUR-PASSWORD]@db.ajrbwkcuthywfihaarmflo.supabase.co:5432/postgres
```

#### Supavisor in transaction mode (port 6543)[#](#supavisor-in-transaction-mode-port-6543)

```
12# Example transaction stringpostgresql://postgres.ajrbwkcuthywddfihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### Supavisor in session mode (port 5432)[#](#supavisor-in-session-mode-port-5432)

```
12# Example session stringpostgresql://postgres.ajrbwkcuthywfddihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)[Platform](https://supabase.com/docs/guides/troubleshooting?products=platform)[Supavisor](https://supabase.com/docs/guides/troubleshooting?products=supavisor)

* * *

### Tags

[ipv4](https://supabase.com/docs/guides/troubleshooting?tags=ipv4)[ipv6](https://supabase.com/docs/guides/troubleshooting?tags=ipv6)[network](https://supabase.com/docs/guides/troubleshooting?tags=network)[compatibility](https://supabase.com/docs/guides/troubleshooting?tags=compatibility)[address](https://supabase.com/docs/guides/troubleshooting?tags=address)

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