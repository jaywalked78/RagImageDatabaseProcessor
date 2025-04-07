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

Database

1.  [Database](https://supabase.com/docs/guides/database/overview)

3.  Access and security

5.  [Managing Postgres Roles](https://supabase.com/docs/guides/database/postgres/roles)

# 

Postgres Roles

## 

Managing access to your Postgres database and configuring permissions.

* * *

Postgres manages database access permissions using the concept of roles. Generally you wouldn't use these roles for your own application - they are mostly for configuring _system access_ to your database. If you want to configure _application access_, then you should use [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) (RLS). You can also implement [Role-based Access Control](https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac) on top of RLS.

## Users vs roles[#](#users-vs-roles)

In Postgres, roles can function as users or groups of users. Users are roles with login privileges, while groups (also known as role groups) are roles that don't have login privileges but can be used to manage permissions for multiple users.

## Creating roles[#](#creating-roles)

You can create a role using the `create role` command:

```
1create role "role_name";
```

## Creating users[#](#creating-users)

Roles and users are essentially the same in Postgres, however if you want to use password-logins for a specific role, then you can use `WITH LOGIN PASSWORD`:

```
1create role "role_name" with login password 'extremely_secure_password';
```

## Passwords[#](#passwords)

Your Postgres database is the core of your Supabase project, so it's important that every role has a strong, secure password at all times. Here are some tips for creating a secure password:

-   Use a password manager to generate it.
-   Make a long password (12 characters at least).
-   Don't use any common dictionary words.
-   Use both upper and lower case characters, numbers, and special symbols.

### Special symbols in passwords[#](#special-symbols-in-passwords)

If you use special symbols in your Postgres password, you must remember to [percent-encode](https://en.wikipedia.org/wiki/Percent-encoding) your password later if using the Postgres connection string, for example, `postgresql://postgres.projectref:p%3Dword@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

### Changing your project password[#](#changing-your-project-password)

When you created your project you were also asked to enter a password. This is actually the password for the `postgres` role in your database. You can update this from the Dashboard under the [database settings](https://supabase.com/dashboard/project/_/settings/database) page. You should _never_ give this to third-party service unless you absolutely trust them. Instead, we recommend that you create a new user for every service that you want to give access too. This will also help you with debugging - you can see every query that each role is executing in your database within `pg_stat_statements`.

Changing the password does not result in any downtime. All connected services, such as PostgREST, PgBouncer, and other Supabase managed services, are automatically updated to use the latest password to ensure availability. However, if you have any external services connecting to the Supabase database using hardcoded username/password credentials, a manual update will be required.

## Granting permissions[#](#granting-permissions)

Roles can be granted various permissions on database objects using the `GRANT` command. Permissions include `SELECT`, `INSERT`, `UPDATE`, and `DELETE`. You can configure access to almost any object inside your database - including tables, views, functions, and triggers.

## Revoking permissions[#](#revoking-permissions)

Permissions can be revoked using the `REVOKE` command:

```
1REVOKE permission_type ON object_name FROM role_name;
```

## Role hierarchy[#](#role-hierarchy)

Roles can be organized in a hierarchy, where one role can inherit permissions from another. This simplifies permission management, as you can define permissions at a higher level and have them automatically apply to all child roles.

### Role inheritance[#](#role-inheritance)

To create a role hierarchy, you first need to create the parent and child roles. The child role will inherit permissions from its parent. Child roles can be added using the INHERIT option when creating the role:

```
1create role "child_role_name" inherit "parent_role_name";
```

### Preventing inheritance[#](#preventing-inheritance)

In some cases, you might want to prevent a role from having a child relationship (typically superuser roles). You can prevent inheritance relations using `NOINHERIT`:

```
1alter role "child_role_name" noinherit;
```

## Supabase roles[#](#supabase-roles)

Postgres comes with a set of [predefined roles](https://www.postgresql.org/docs/current/predefined-roles.html). Supabase extends this with a default set of roles which are configured on your database when you start a new project:

### `postgres`[#](#postgres)

The default Postgres role. This has admin privileges.

### `anon`[#](#anon)

For unauthenticated, public access. This is the role which the API (PostgREST) will use when a user _is not_ logged in.

### `authenticator`[#](#authenticator)

A special role for the API (PostgREST). It has very limited access, and is used to validate a JWT and then "change into" another role determined by the JWT verification.

### `authenticated`[#](#authenticated)

For "authenticated access." This is the role which the API (PostgREST) will use when a user _is_ logged in.

### `service_role`[#](#servicerole)

For elevated access. This role is used by the API (PostgREST) to bypass Row Level Security.

### `supabase_auth_admin`[#](#supabaseauthadmin)

Used by the Auth middleware to connect to the database and run migration. Access is scoped to the `auth` schema.

### `supabase_storage_admin`[#](#supabasestorageadmin)

Used by the Auth middleware to connect to the database and run migration. Access is scoped to the `storage` schema.

### `dashboard_user`[#](#dashboarduser)

For running commands via the Supabase UI.

### `supabase_admin`[#](#supabaseadmin)

An internal role Supabase uses for administrative tasks, such as running upgrades and automations.

## Resources[#](#resources)

-   Official Postgres docs: [Database Roles](https://www.postgresql.org/docs/current/database-roles.html)
-   Official Postgres docs: [Role Membership](https://www.postgresql.org/docs/current/role-membership.html)
-   Official Postgres docs: [Function Permissions](https://www.postgresql.org/docs/current/perm-functions.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/roles.mdx)

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