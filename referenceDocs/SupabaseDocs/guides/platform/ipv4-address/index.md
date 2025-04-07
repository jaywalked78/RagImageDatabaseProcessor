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

3.  Add-ons

5.  [IPv4 Address](https://supabase.com/docs/guides/platform/ipv4-address)

# 

Dedicated IPv4 Address for Ingress

## 

Attach an IPv4 address to your database

* * *

The Supabase IPv4 add-on provides a dedicated IPv4 address for your Postgres database connection. It can be configured in the [Add-ons Settings](https://supabase.com/dashboard/project/_/settings/addons).

## Understanding IP addresses[#](#understanding-ip-addresses)

The Internet Protocol (IP) addresses devices on the internet. There are two main versions:

-   **IPv4**: The older version, with a limited address space.
-   **IPv6**: The newer version, offering a much larger address space and the future-proof option.

## When you need the IPv4 add-on:[#](#when-you-need-the-ipv4-add-on)

IPv4 addresses are guaranteed to be static for ingress traffic. If your database is making outbound connections, the outbound IP address is not static and cannot be guaranteed.

-   When using the direct connection string in an IPv6-incompatible network instead of Supavisor or client libraries.
-   When you need a dedicated IP address for your direct connection string

## Enabling the IPv4 add-on[#](#enabling-the-ipv4-add-on)

You can enable the IPv4 add-on in your project's [add-ons settings](https://supabase.com/dashboard/project/_/settings/addons).

Note that direct database connections can experience a short amount of downtime when toggling the add-on due to DNS reconfiguration and propagation. Generally, this should be less than a minute.

## Read replicas and IPv4 add-on[#](#read-replicas-and-ipv4-add-on)

When using the add-on, each database (including read replicas) receives an IPv4 address. Each replica adds to the total IPv4 cost.

## Changes and updates[#](#changes-and-updates)

-   While the IPv4 address generally remains the same, actions like pausing/unpausing the project or enabling/disabling the add-on can lead to a new IPv4 address.

## Supabase and IPv6 compatibility[#](#supabase-and-ipv6-compatibility)

By default, Supabase Postgres use IPv6 addresses. If your system doesn't support IPv6, you have the following options:

1.  **Supavisor Connection Strings**: The Supavisor connection strings are IPv4-compatible alternatives to direct connections
2.  **Supabase Client Libraries**: These libraries are compatible with IPv4
3.  **Dedicated IPv4 Add-On (Pro Plans+)**: For a guaranteed IPv4 and static database address for the direct connection, enable this paid add-on.

### Checking your network IPv6 support[#](#checking-your-network-ipv6-support)

Most services are IPv6 compatible, but some exceptions exist (listed below). To verify your personal network supports it, run this command on your server:

```
1curl -6 https://ifconfig.co/ip
```

If it returns an IPv6 address then your system is compatible. An example IPv6 address might look like: `2a05:d014:1c06:5f0c:d7a9:8616:bee2:30df`.

### Checking platforms for IPv6 support:[#](#checking-platforms-for-ipv6-support)

The majority of services are IPv6 compatible. However, there are a few prominent ones that only accept IPv4 connections:

-   [Retool](https://retool.com/)
-   [Vercel](https://vercel.com/)
-   [GitHub Actions](https://docs.github.com/en/actions)
-   [Render](https://render.com/)

## Finding your database's IP address[#](#finding-your-databases-ip-address)

Use an IP lookup website or this command (replace `<PROJECT_REF>`):

```
1nslookup db.<PROJECT_REF>.supabase.co
```

## Identifying your connections[#](#identifying-your-connections)

The pooler and direct connection strings can be found in the [database settings](https://supabase.com/dashboard/project/_/settings/database):

#### Direct connection[#](#direct-connection)

IPv6 unless IPv4 Add-On is enabled

```
12# Example direct connection stringpostgresql://postgres:[YOUR-PASSWORD]@db.ajrbwkcuthywfihaarmflo.supabase.co:5432/postgres
```

#### Supavisor in transaction mode (port 6543)[#](#supavisor-in-transaction-mode-port-6543)

Always uses an IPv4 address

```
12# Example transaction stringpostgresql://postgres.ajrbwkcuthywddfihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

#### Supavisor in session mode (port 5432)[#](#supavisor-in-session-mode-port-5432)

Always uses an IPv4 address

```
12# Example session stringpostgresql://postgres.ajrbwkcuthywfddihrmflo:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

## Pricing[#](#pricing)

For a detailed breakdown of how charges are calculated, refer to [Manage IPv4 usage](https://supabase.com/docs/guides/platform/manage-your-usage/ipv4).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/ipv4-address.mdx)

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