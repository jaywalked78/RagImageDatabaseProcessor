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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Getting started

5.  [Setting up your editor](https://supabase.com/docs/guides/functions/local-development)

# 

Local development

## 

Setup local development environment for Edge Functions.

* * *

We recommend installing the Deno CLI and related tools for local development.

## Deno support[#](#deno-support)

You can follow the [Deno guide](https://deno.com/manual@v1.32.5/getting_started/setup_your_environment) for setting up your development environment with your favorite editor/IDE.

## Deno with Visual Studio Code[#](#deno-with-visual-studio-code)

When using VSCode, you should install both the Deno CLI and the the Deno language server [via this link](vscode:extension/denoland.vscode-deno) or by browsing the extensions in VSCode and choosing to install the _Deno_ extension.

The Supabase CLI can automatically create helpful Deno settings when running `supabase init`. Select `y` when prompted "Generate VS Code settings for Deno? \[y/N\]"!

## Deno support in subfolders[#](#deno-support-in-subfolders)

You can enable the Deno language server for specific sub-paths in a workspace, while using VSCode's built-in JavaScript/TypeScript language server for all other files.

For example if you have a project like this:

```
1234project├── app└── supabase  └── functions
```

To enable the Deno language server only for the `supabase/functions` folder, add `./supabase/functions` to the list of _Deno: Enable Paths_ in the configuration. In your `.vscode/settings.json` file add:

```
1234{  "deno.enablePaths": ["./supabase/functions"],  "deno.importMap": "./supabase/functions/import_map.json"}
```

## Multi-root workspaces in VSCode[#](#multi-root-workspaces-in-vscode)

We recommend using `deno.enablePaths` mentioned above as it's easier to manage, however if you like [multi-root workspaces](https://code.visualstudio.com/docs/editor/workspaces#_multiroot-workspaces) you can use these as an alternative.

For example, see this `edge-functions.code-workspace` configuration for a CRA (create react app) client with Supabase Edge Functions. You can find the complete example on [GitHub](https://github.com/supabase/supabase/tree/master/examples/edge-functions).

```
123456789101112131415161718192021222324{  "folders": [    {      "name": "project-root",      "path": "./"    },    {      "name": "client",      "path": "app"    },    {      "name": "supabase-functions",      "path": "supabase/functions"    }  ],  "settings": {    "files.exclude": {      "node_modules/": true,      "app/": true,      "supabase/functions/": true    },    "deno.importMap": "./supabase/functions/import_map.json"  }}
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/local-development.mdx)

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