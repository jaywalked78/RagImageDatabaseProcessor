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

3.  Local development

5.  [Managing config and secrets](https://supabase.com/docs/guides/local-development/managing-config)

# 

Managing config and secrets

* * *

The Supabase CLI uses a `config.toml` file to manage local configuration. This file is located in the `supabase` directory of your project.

## Config reference[#](#config-reference)

The `config.toml` file is automatically created when you run `supabase init`.

There are a wide variety of options available, which can be found in the [CLI Config Reference](https://supabase.com/docs/guides/cli/config).

For example, to enable the "Apple" OAuth provider for local development, you can append the following information to `config.toml`:

```
12345[auth.external.apple]enabled = falseclient_id = ""secret = ""redirect_uri = "" # Overrides the default auth redirectUrl.
```

## Using secrets inside config.toml[#](#using-secrets-inside-configtoml)

You can reference environment variables within the `config.toml` file using the `env()` function. This will detect any values stored in an `.env` file at the root of your project directory. This is particularly useful for storing sensitive information like API keys, and any other values that you don't want to check into version control.

```
12345.├── .env├── .env.example└── supabase    └── config.toml
```

Do NOT commit your `.env` into git. Be sure to configure your `.gitignore` to exclude this file.

For example, if your `.env` contained the following values:

```
12GITHUB_CLIENT_ID=""GITHUB_SECRET=""
```

Then you would reference them inside of our `config.toml` like this:

```
12345[auth.external.github]enabled = trueclient_id = "env(GITHUB_CLIENT_ID)"secret = "env(GITHUB_SECRET)"redirect_uri = "" # Overrides the default auth redirectUrl.
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/local-development/managing-config.mdx)

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