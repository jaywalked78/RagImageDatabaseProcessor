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

3.  Guides

5.  [Managing dependencies](https://supabase.com/docs/guides/functions/dependencies)

# 

Managing dependencies

## 

Managing packages and dependencies.

* * *

## Importing dependencies[#](#importing-dependencies)

Supabase Edge Functions support several ways to import dependencies:

-   JavaScript modules from npm ([https://docs.deno.com/examples/npm/](https://docs.deno.com/examples/npm/))
-   Built-in [Node APIs](https://docs.deno.com/runtime/manual/node/compatibility)
-   Modules published to [JSR](https://jsr.io/) or [deno.land/x](https://deno.land/x)

### NPM modules[#](#npm-modules)

You can import npm modules using the `npm:` specifier:

```
1import { createClient } from 'npm:@supabase/supabase-js@2'
```

### Node.js built-ins[#](#nodejs-built-ins)

For Node.js built-in APIs, use the `node:` specifier:

```
1import process from 'node:process'
```

Learn more about npm specifiers and Node built-in APIs in [Deno's documentation](https://docs.deno.com/runtime/manual/node/npm_specifiers).

### JSR[#](#jsr)

You can import JS modules published to [JSR](https://jsr.io/) (e.g.: Deno's standard library), using the `jsr:` specifier:

```
1import path from 'jsr:@std/path@1.0.8'
```

## Managing dependencies[#](#managing-dependencies)

Developing with Edge Functions is similar to developing with Node.js, but with a few key differences.

In the Deno ecosystem, each function should be treated as an independent project with its own set of dependencies and configurations. This "isolation by design" approach:

-   Ensures each function has explicit control over its dependencies
-   Prevents unintended side effects between functions
-   Makes deployments more predictable and maintainable
-   Allows for different versions of the same dependency across functions

For these reasons, we recommend maintaining separate configuration files (`deno.json`, `.npmrc`, or `import_map.json`) within each function's directory, even if it means duplicating some configurations.

There are two ways to manage your dependencies in Supabase Edge Functions:

### Using deno.json (recommended)[#](#using-denojson-recommended)

This feature requires Supabase CLI version 1.215.0 or higher.

Each function should have its own `deno.json` file to manage dependencies and configure Deno-specific settings. This ensures proper isolation between functions and is the recommended approach for deployment. For a complete list of supported options, see the [official Deno configuration documentation](https://docs.deno.com/runtime/manual/getting_started/configuration_file).

```
12345{  "imports": {    "lodash": "https://cdn.skypack.dev/lodash"  }}
```

The recommended file structure for deployment:

```
1234567891011└── supabase    ├── functions    │   ├── function-one    │   │   ├── index.ts    │   │   ├─- deno.json    # Function-specific Deno configuration    │   │   └── .npmrc       # Function-specific npm configuration (if needed)    │   └── function-two    │       ├── index.ts    │       ├─- deno.json    # Function-specific Deno configuration    │       └── .npmrc       # Function-specific npm configuration (if needed)    └── config.toml
```

While it's possible to use a global `deno.json` in the `/supabase/functions` directory for local development, this approach is not recommended for deployment. Each function should maintain its own configuration to ensure proper isolation and dependency management.

### Using import maps (legacy)[#](#using-import-maps-legacy)

Import Maps are a legacy way to manage dependencies, similar to a `package.json` file. While still supported, we recommend using `deno.json`. If both exist, `deno.json` takes precedence.

Each function should have its own `import_map.json` file for proper isolation:

```
12345{  "imports": {    "lodash": "https://cdn.skypack.dev/lodash"  }}
```

The recommended file structure:

```
123456789└── supabase    ├── functions    │   ├── function-one    │   │   ├── index.ts    │   │   └── import_map.json    # Function-specific import map    │   └── function-two    │       ├── index.ts    │       └── import_map.json    # Function-specific import map    └── config.toml
```

While it's possible to use a global `import_map.json` in the `/supabase/functions` directory for local development, this approach is not recommended for deployment. Each function should maintain its own import map to ensure proper isolation.

If using import maps with VSCode, update your `.vscode/settings.json` to point to your function-specific import map:

```
123456789{  "deno.enable": true,  "deno.unstable": [    "bare-node-builtins",    "byonm"    // ... other flags ...  ],  "deno.importMap": "./supabase/functions/my-function/import_map.json"}
```

You can override the default import map location using the `--import-map <string>` flag with `serve` and `deploy` commands, or by setting the `import_map` property in your `config.toml` file:

```
12[functions.my-function]import_map = "./supabase/functions/my-function/import_map.json"
```

### Importing from private registries[#](#importing-from-private-registries)

This feature requires Supabase CLI version 1.207.9 or higher.

To use private npm packages, create a `.npmrc` file within your function directory. This ensures proper isolation and dependency management for each function.

```
123456└── supabase    └── functions        └── my-function            ├── index.ts            ├── deno.json            └── .npmrc       # Function-specific npm configuration
```

Add your registry details in the `.npmrc` file. Follow [this guide](https://docs.npmjs.com/cli/v10/configuring-npm/npmrc) to learn more about the syntax of npmrc files.

```
12@myorg:registry=https://npm.registryhost.com//npm.registryhost.com/:_authToken=VALID_AUTH_TOKEN
```

While it's possible to use a global `.npmrc` in the `/supabase/functions` directory for local development, we recommend using function-specific `.npmrc` files for deployment to maintain proper isolation.

After configuring your `.npmrc`, you can import the private package in your function code:

```
123import MyPackage from 'npm:@myorg/private-package@v1.0.1'// use MyPackage
```

### Using a custom NPM registry[#](#using-a-custom-npm-registry)

This feature requires Supabase CLI version 2.2.8 or higher.

Some organizations require a custom NPM registry for security and compliance purposes. In such instances, you can specify the custom NPM registry to use via `NPM_CONFIG_REGISTRY` environment variable.

You can define it in the project's `.env` file or directly specify it when running the deploy command:

```
1NPM_CONFIG_REGISTRY=https://custom-registry/ supabase functions deploy my-function
```

## Importing types[#](#importing-types)

If your [environment is set up properly](https://supabase.com/docs/guides/functions/local-development) and the module you're importing is exporting types, the import will have types and autocompletion support.

Some npm packages may not ship out of the box types and you may need to import them from a separate package. You can specify their types with a `@deno-types` directive:

```
12// @deno-types="npm:@types/express@^4.17"import express from 'npm:express@^4.17'
```

To include types for built-in Node APIs, add the following line to the top of your imports:

```
1/// <reference types="npm:@types/node" />
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/dependencies.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FILr3cneZuFk%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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