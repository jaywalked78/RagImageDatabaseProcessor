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

Local Development

1.  [Local Dev / CLI](https://supabase.com/docs/guides/local-development)

3.  Testing

5.  [pgTAP advanced guide](https://supabase.com/docs/guides/local-development/testing/pgtap-extended)

# 

Advanced pgTAP Testing

* * *

While basic pgTAP provides excellent testing capabilities, you can enhance the testing workflow using database development tools and helper packages. This guide covers advanced testing techniques using database.dev and community-maintained test helpers.

## Using database.dev[#](#using-databasedev)

[Database.dev](https://database.dev) is a package manager for Postgres that allows installation and use of community-maintained packages, including testing utilities.

### Setting up dbdev[#](#setting-up-dbdev)

To use database development tools and packages, install some prerequisites:

```
123456789101112131415161718192021222324252627282930313233343536create extension if not exists http with schema extensions;create extension if not exists pg_tle;drop extension if exists "supabase-dbdev";select pgtle.uninstall_extension_if_exists('supabase-dbdev');select    pgtle.install_extension(        'supabase-dbdev',        resp.contents ->> 'version',        'PostgreSQL package manager',        resp.contents ->> 'sql'    )from http(    (        'GET',        'https://api.database.dev/rest/v1/'        || 'package_versions?select=sql,version'        || '&package_name=eq.supabase-dbdev'        || '&order=version.desc'        || '&limit=1',        array[            ('apiKey', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtdXB0cHBsZnZpaWZyYndtbXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODAxMDczNzIsImV4cCI6MTk5NTY4MzM3Mn0.z2CN0mvO2No8wSi46Gw59DFGCTJrzM0AQKsu_5k134s')::http_header        ],        null,        null    )) x,lateral (    select        ((row_to_json(x) -> 'content') #>> '{}')::json -> 0) resp(contents);create extension "supabase-dbdev";select dbdev.install('supabase-dbdev');-- Drop and recreate the extension to ensure a clean installationdrop extension if exists "supabase-dbdev";create extension "supabase-dbdev";
```

### Installing test helpers[#](#installing-test-helpers)

The Test Helpers package provides utilities that simplify testing Supabase-specific features:

```
12select dbdev.install('basejump-supabase_test_helpers');create extension if not exists "basejump-supabase_test_helpers" version '0.0.6';
```

## Test helper benefits[#](#test-helper-benefits)

The test helpers package provides several advantages over writing raw pgTAP tests:

1.  **Simplified User Management**
    
    -   Create test users with `tests.create_supabase_user()`
    -   Switch contexts with `tests.authenticate_as()`
    -   Retrieve user IDs using `tests.get_supabase_uid()`
2.  **Row Level Security (RLS) Testing Utilities**
    
    -   Verify RLS status with `tests.rls_enabled()`
    -   Test policy enforcement
    -   Simulate different user contexts
3.  **Reduced Boilerplate**
    
    -   No need to manually insert auth.users
    -   Simplified JWT claim management
    -   Clean test setup and cleanup

## Schema-wide Row Level Security testing[#](#schema-wide-row-level-security-testing)

When working with Row Level Security, it's crucial to ensure that RLS is enabled on all tables that need it. Create a simple test to verify RLS is enabled across an entire schema:

```
12345678begin;select plan(1);-- Verify RLS is enabled on all tables in the public schemaselect tests.rls_enabled('public');select * from finish();rollback;
```

## Test file organization[#](#test-file-organization)

When working with multiple test files that share common setup requirements, it's beneficial to create a single "pre-test" file that handles the global environment setup. This approach reduces duplication and ensures consistent test environments.

### Creating a pre-test hook[#](#creating-a-pre-test-hook)

Since pgTAP test files are executed in alphabetical order, create a setup file that runs first by using a naming convention like `000-setup-tests-hooks.sql`:

```
1supabase test new 000-setup-tests-hooks
```

This setup file should contain:

1.  All shared extensions and dependencies
2.  Common test utilities
3.  A simple always green test to verify the setup

Here's an example setup file:

```
12345678910111213141516171819202122232425262728293031323334353637383940414243444546474849505152535455-- install tests utilities-- install pgtap extension for testingcreate extension if not exists pgtap with schema extensions;/*------------------------- install dbdev --------------------------Requires:  - pg_tle: https://github.com/aws/pg_tle  - pgsql-http: https://github.com/pramsey/pgsql-http*/create extension if not exists http with schema extensions;create extension if not exists pg_tle;drop extension if exists "supabase-dbdev";select pgtle.uninstall_extension_if_exists('supabase-dbdev');select    pgtle.install_extension(        'supabase-dbdev',        resp.contents ->> 'version',        'PostgreSQL package manager',        resp.contents ->> 'sql'    )from http(    (        'GET',        'https://api.database.dev/rest/v1/'        || 'package_versions?select=sql,version'        || '&package_name=eq.supabase-dbdev'        || '&order=version.desc'        || '&limit=1',        array[            ('apiKey', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhtdXB0cHBsZnZpaWZyYndtbXR2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODAxMDczNzIsImV4cCI6MTk5NTY4MzM3Mn0.z2CN0mvO2No8wSi46Gw59DFGCTJrzM0AQKsu_5k134s')::http_header        ],        null,        null    )) x,lateral (    select        ((row_to_json(x) -> 'content') #>> '{}')::json -> 0) resp(contents);create extension "supabase-dbdev";select dbdev.install('supabase-dbdev');drop extension if exists "supabase-dbdev";create extension "supabase-dbdev";-- Install test helpersselect dbdev.install('basejump-supabase_test_helpers');create extension if not exists "basejump-supabase_test_helpers" version '0.0.6';-- Verify setup with a no-op testbegin;select plan(1);select ok(true, 'Pre-test hook completed successfully');select * from finish();rollback;
```

### Benefits[#](#benefits)

This approach provides several advantages:

-   Reduces code duplication across test files
-   Ensures consistent test environment setup
-   Makes it easier to maintain and update shared dependencies
-   Provides immediate feedback if the setup process fails

Your subsequent test files (`001-auth-tests.sql`, `002-rls-tests.sql`) can focus solely on their specific test cases, knowing that the environment is properly configured.

## Example: Advanced RLS testing[#](#example-advanced-rls-testing)

Here's a complete example using test helpers to verify RLS policies putting it all together:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051begin;-- Assuming 000-setup-tests-hooks.sql file is present to use tests helpersselect plan(4);-- Set up test data-- Create test supabase usersselect tests.create_supabase_user('user1@test.com');select tests.create_supabase_user('user2@test.com');-- Create test datainsert into public.todos (task, user_id) values  ('User 1 Task 1', tests.get_supabase_uid('user1@test.com')),  ('User 1 Task 2', tests.get_supabase_uid('user1@test.com')),  ('User 2 Task 1', tests.get_supabase_uid('user2@test.com'));-- Test as User 1select tests.authenticate_as('user1@test.com');-- Test 1: User 1 should only see their own todosselect results_eq(  'select count(*) from todos',  ARRAY[2::bigint],  'User 1 should only see their 2 todos');-- Test 2: User 1 can create their own todoselect lives_ok(  $$insert into todos (task, user_id) values ('New Task', tests.get_supabase_uid('user1@test.com'))$$,  'User 1 can create their own todo');-- Test as User 2select tests.authenticate_as('user2@test.com');-- Test 3: User 2 should only see their own todosselect results_eq(  'select count(*) from todos',  ARRAY[1::bigint],  'User 2 should only see their 1 todo');-- Test 4: User 2 cannot modify User 1's todoSELECT results_ne(    $$ update todos set task = 'Hacked!' where user_id = tests.get_supabase_uid('user1@test.com') returning 1 $$,    $$ values(1) $$,    'User 2 cannot modify User 1 todos');select * from finish();rollback;
```

## Not another todo app: Testing complex organizations[#](#not-another-todo-app-testing-complex-organizations)

Todo apps are great for learning, but this section explores testing a more realistic scenario: a multi-tenant content publishing platform. This example demonstrates testing complex permissions, plan restrictions, and content management.

### System overview[#](#system-overview)

This demo app implements:

-   Organizations with tiered plans (free/pro/enterprise)
-   Role-based access (owner/admin/editor/viewer)
-   Content management (posts/comments)
-   Premium content restrictions
-   Plan-based limitations

### What makes this complex?[#](#what-makes-this-complex)

1.  **Layered Permissions**
    
    -   Role hierarchies affect access rights
    -   Plan types influence user capabilities
    -   Content state (draft/published) affects permissions
2.  **Business Rules**
    
    -   Free plan post limits
    -   Premium content visibility
    -   Cross-organization security

### Testing focus areas[#](#testing-focus-areas)

When writing tests, verify:

-   Organization member access control
-   Content visibility across roles
-   Plan limitation enforcement
-   Cross-organization data isolation

#### 1\. App schema definitions[#](#1-app-schema-definitions)

The app schema tables are defined like this:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051create table public.profiles (  id uuid references auth.users(id) primary key,  username text unique not null,  full_name text,  bio text,  created_at timestamptz default now(),  updated_at timestamptz default now());create table public.organizations (  id bigint primary key generated always as identity,  name text not null,  slug text unique not null,  plan_type text not null check (plan_type in ('free', 'pro', 'enterprise')),  max_posts int not null default 5,  created_at timestamptz default now());create table public.org_members (  org_id bigint references public.organizations(id) on delete cascade,  user_id uuid references auth.users(id) on delete cascade,  role text not null check (role in ('owner', 'admin', 'editor', 'viewer')),  created_at timestamptz default now(),  primary key (org_id, user_id));create table public.posts (  id bigint primary key generated always as identity,  title text not null,  content text not null,  author_id uuid references public.profiles(id) not null,  org_id bigint references public.organizations(id),  status text not null check (status in ('draft', 'published', 'archived')),  is_premium boolean default false,  scheduled_for timestamptz,  category text,  view_count int default 0,  published_at timestamptz,  created_at timestamptz default now(),  updated_at timestamptz default now());create table public.comments (  id bigint primary key generated always as identity,  post_id bigint references public.posts(id) on delete cascade,  author_id uuid references public.profiles(id),  content text not null,  is_deleted boolean default false,  created_at timestamptz default now(),  updated_at timestamptz default now());
```

#### 2\. RLS policies declaration[#](#2-rls-policies-declaration)

Now to setup the RLS policies for each tables:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122-- Create a private schema to store all security definer functions utils-- As such functions should never be in a API exposed schemacreate schema if not exists private;-- Helper function for role checkscreate or replace function private.get_user_org_role(org_id bigint, user_id uuid)returns textset search_path = ''as $$  select role from public.org_members  where org_id = $1 and user_id = $2;-- Note the use of security definer to avoid RLS checking recursion issue-- see: https://supabase.com/docs/guides/database/postgres/row-level-security#use-security-definer-functions$$ language sql security definer;-- Helper utils to check if an org is below the max post limitcreate or replace function private.can_add_post(org_id bigint)returns booleanset search_path = ''as $$  select (select count(*)          from public.posts p          where p.org_id = $1) < o.max_posts  from public.organizations o  where o.id = $1$$ language sql security definer;-- Enable RLS for all tablesalter table public.profiles enable row level security;alter table public.organizations enable row level security;alter table public.org_members enable row level security;alter table public.posts enable row level security;alter table public.comments enable row level security;-- Profiles policiescreate policy "Public profiles are viewable by everyone"  on public.profiles for select using (true);create policy "Users can insert their own profile"  on public.profiles for insert with check ((select auth.uid()) = id);create policy "Users can update their own profile"  on public.profiles for update using ((select auth.uid()) = id)  with check ((select auth.uid()) = id);-- Organizations policiescreate policy "Public org info visible to all"  on public.organizations for select using (true);create policy "Org management restricted to owners"  on public.organizations for all using (    private.get_user_org_role(id, (select auth.uid())) = 'owner'  );-- Org Members policiescreate policy "Members visible to org members"  on public.org_members for select using (    private.get_user_org_role(org_id, (select auth.uid())) is not null  );create policy "Member management restricted to admins and owners"  on public.org_members for all using (    private.get_user_org_role(org_id, (select auth.uid())) in ('owner', 'admin')  );-- Posts policiescreate policy "Complex post visibility"  on public.posts for select using (    -- Published non-premium posts are visible to all    (status = 'published' and not is_premium)    or    -- Premium posts visible to org members only    (status = 'published' and is_premium and    private.get_user_org_role(org_id, (select auth.uid())) is not null)    or    -- All posts visible to editors and above    private.get_user_org_role(org_id, (select auth.uid())) in ('owner', 'admin', 'editor')  );create policy "Post creation rules"  on public.posts for insert with check (    -- Must be org member with appropriate role    private.get_user_org_role(org_id, (select auth.uid())) in ('owner', 'admin', 'editor')    and    -- Check org post limits for free plans    (      (select o.plan_type != 'free'      from organizations o      where o.id = org_id)      or      (select private.can_add_post(org_id))    )  );create policy "Post update rules"  on public.posts for update using (    exists (      select 1      where        -- Editors can update non-published posts        (private.get_user_org_role(org_id, (select auth.uid())) = 'editor' and status != 'published')        or        -- Admins and owners can update any post        private.get_user_org_role(org_id, (select auth.uid())) in ('owner', 'admin')    )  );-- Comments policiescreate policy "Comments on published posts are viewable by everyone"  on public.comments for select using (    exists (      select 1 from public.posts      where id = post_id      and status = 'published'    )    and not is_deleted  );create policy "Authenticated users can create comments"  on public.comments for insert with check ((select auth.uid()) = author_id);create policy "Users can update their own comments"  on public.comments for update using (author_id = (select auth.uid()));
```

#### 3\. Test cases:[#](#3-test-cases)

Now everything is setup, let's write RLS test cases, note that each section could be in its own test:

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127128129130131132133134135136137138139140141142143144145146147148149150151152153154155156157158159160161162163164165166167168169170171172173174175176177178179180181-- Assuming we already have: 000-setup-tests-hooks.sql file we can use tests helpersbegin;-- Declare total number of testsselect plan(10);-- Create test usersselect tests.create_supabase_user('org_owner', 'owner@test.com');select tests.create_supabase_user('org_admin', 'admin@test.com');select tests.create_supabase_user('org_editor', 'editor@test.com');select tests.create_supabase_user('premium_user', 'premium@test.com');select tests.create_supabase_user('free_user', 'free@test.com');select tests.create_supabase_user('scheduler', 'scheduler@test.com');select tests.create_supabase_user('free_author', 'free_author@test.com');-- Create profiles for test usersinsert into profiles (id, username, full_name)values  (tests.get_supabase_uid('org_owner'), 'org_owner', 'Organization Owner'),  (tests.get_supabase_uid('org_admin'), 'org_admin', 'Organization Admin'),  (tests.get_supabase_uid('org_editor'), 'org_editor', 'Organization Editor'),  (tests.get_supabase_uid('premium_user'), 'premium_user', 'Premium User'),  (tests.get_supabase_uid('free_user'), 'free_user', 'Free User'),  (tests.get_supabase_uid('scheduler'), 'scheduler', 'Scheduler User'),  (tests.get_supabase_uid('free_author'), 'free_author', 'Free Author');-- First authenticate as service role to bypass RLS for initial setupselect tests.authenticate_as_service_role();-- Create test organizations and setup datawith new_org as (  insert into organizations (name, slug, plan_type, max_posts)  values    ('Test Org', 'test-org', 'pro', 100),    ('Premium Org', 'premium-org', 'enterprise', 1000),    ('Schedule Org', 'schedule-org', 'pro', 100),    ('Free Org', 'free-org', 'free', 2)  returning id, slug),-- Setup members and postsmember_setup as (  insert into org_members (org_id, user_id, role)  select    org.id,    user_id,    role  from new_org org cross join (    values      (tests.get_supabase_uid('org_owner'), 'owner'),      (tests.get_supabase_uid('org_admin'), 'admin'),      (tests.get_supabase_uid('org_editor'), 'editor'),      (tests.get_supabase_uid('premium_user'), 'viewer'),      (tests.get_supabase_uid('scheduler'), 'editor'),      (tests.get_supabase_uid('free_author'), 'editor')  ) as members(user_id, role)  where org.slug = 'test-org'     or (org.slug = 'premium-org' and role = 'viewer')     or (org.slug = 'schedule-org' and role = 'editor')     or (org.slug = 'free-org' and role = 'editor'))-- Setup initial postsinsert into posts (title, content, org_id, author_id, status, is_premium, scheduled_for)select  title,  content,  org.id,  author_id,  status,  is_premium,  scheduled_forfrom new_org org cross join (  values    ('Premium Post', 'Premium content', tests.get_supabase_uid('premium_user'), 'published', true, null),    ('Free Post', 'Free content', tests.get_supabase_uid('premium_user'), 'published', false, null),    ('Future Post', 'Future content', tests.get_supabase_uid('scheduler'), 'published', false, '2024-01-02 12:00:00+00'::timestamptz)) as posts(title, content, author_id, status, is_premium, scheduled_for)where org.slug in ('premium-org', 'schedule-org');-- Test owner privilegesselect tests.authenticate_as('org_owner');select lives_ok(  $$    update organizations    set name = 'Updated Org'    where id = (select id from organizations limit 1)  $$,  'Owner can update organization');-- Test admin privilegesselect tests.authenticate_as('org_admin');select results_eq(    $$select count(*) from org_members$$,    ARRAY[6::bigint],    'Admin can view all members');-- Test editor restrictionsselect tests.authenticate_as('org_editor');select throws_ok(  $$    insert into org_members (org_id, user_id, role)    values (      (select id from organizations limit 1),      (select tests.get_supabase_uid('org_editor')),      'viewer'    )  $$,  '42501',  'new row violates row-level security policy for table "org_members"',  'Editor cannot manage members');-- Premium Content Access Testsselect tests.authenticate_as('premium_user');select results_eq(    $$select count(*) from posts where org_id = (select id from organizations where slug = 'premium-org')$$,    ARRAY[3::bigint],    'Premium user can see all posts');select tests.clear_authentication();select results_eq(    $$select count(*) from posts where org_id = (select id from organizations where slug = 'premium-org')$$,    ARRAY[2::bigint],    'Anonymous users can only see free posts');-- Time-Based Publishing Testsselect tests.authenticate_as('scheduler');select tests.freeze_time('2024-01-01 12:00:00+00'::timestamptz);select results_eq(    $$select count(*) from posts where scheduled_for > now() and org_id = (select id from organizations where slug = 'schedule-org')$$,    ARRAY[1::bigint],    'Can see scheduled posts');select tests.freeze_time('2024-01-02 13:00:00+00'::timestamptz);select results_eq(    $$select count(*) from posts where scheduled_for < now() and org_id = (select id from organizations where slug = 'schedule-org')$$,    ARRAY[1::bigint],    'Can see posts after schedule time');select tests.unfreeze_time();-- Plan Limit Testsselect tests.authenticate_as('free_author');select lives_ok(  $$    insert into posts (title, content, org_id, author_id, status)    select 'Post 1', 'Content 1', id, auth.uid(), 'draft'    from organizations where slug = 'free-org' limit 1  $$,  'First post creates successfully');select lives_ok(  $$    insert into posts (title, content, org_id, author_id, status)    select 'Post 2', 'Content 2', id, auth.uid(), 'draft'    from organizations where slug = 'free-org' limit 1  $$,  'Second post creates successfully');select throws_ok(  $$    insert into posts (title, content, org_id, author_id, status)    select 'Post 3', 'Content 3', id, auth.uid(), 'draft'    from organizations where slug = 'free-org' limit 1  $$,  '42501',  'new row violates row-level security policy for table "posts"',  'Cannot exceed free plan post limit');select * from finish();rollback;
```

## Additional resources[#](#additional-resources)

-   [Test Helpers Documentation](https://database.dev/basejump/supabase_test_helpers)
-   [Test Helpers Reference](https://github.com/usebasejump/supabase-test-helpers)
-   [Row Level Security Writing Guide](https://usebasejump.com/blog/testing-on-supabase-with-pgtap)
-   [Database.dev Package Registry](https://database.dev)
-   [Row Level Security Performance and Best Practices](https://github.com/orgs/supabase/discussions/14576)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/local-development/testing/pgtap-extended.mdx)

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