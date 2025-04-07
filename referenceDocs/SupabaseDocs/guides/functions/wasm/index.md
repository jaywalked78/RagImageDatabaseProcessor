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

5.  [Wasm modules](https://supabase.com/docs/guides/functions/wasm)

# 

Using Wasm modules

## 

How to use WebAssembly in Edge Functions.

* * *

Edge Functions supports running [WebAssembly (Wasm)](https://developer.mozilla.org/en-US/docs/WebAssembly) modules. WebAssembly is useful if you want to optimize code that's slower to run in JavaScript or require low-level manipulation.

It also gives you the option to port existing libraries written in other languages to be used with JavaScript. For example, [magick-wasm](https://supabase.com/docs/guides/functions/examples/image-manipulation), which does image manipulation and transforms, is a port of an existing C library to WebAssembly.

### Writing a Wasm module[#](#writing-a-wasm-module)

You can use different languages and SDKs to write Wasm modules. For this tutorial, we will write a simple Wasm module in Rust that adds two numbers.

Follow this [guide on writing Wasm modules in Rust](https://developer.mozilla.org/en-US/docs/WebAssembly/Rust_to_Wasm) to setup your dev environment.

Create a new Edge Function called `wasm-add`.

```
1supabase functions new wasm-add
```

Create a new Cargo project for the Wasm module inside the function's directory:

```
12cd supabase/functions/wasm-addcargo new --lib add-wasm
```

Add the following code to `add-wasm/src/lib.rs`.

```
123456use wasm_bindgen::prelude::*;#[wasm_bindgen]pub fn add(a: u32, b: u32) -> u32 {    a + b}
```

[View source](https://github.com/supabase/supabase/blob/cb30f7be2dc31fa93dae25765a5fd28b9b2fa313/examples/edge-functions/supabase/functions/wasm-modules/add-wasm/src/lib.rs)

Update the `add-wasm/Cargo.toml` to include the `wasm-bindgen` dependency.

```
123456789101112[package]name = "add-wasm"version = "0.1.0"description = "A simple wasm module that adds two numbers"license = "MIT/Apache-2.0"edition = "2021"[lib]crate-type = ["cdylib"][dependencies]wasm-bindgen = "0.2"
```

[View source](https://github.com/supabase/supabase/blob/cb30f7be2dc31fa93dae25765a5fd28b9b2fa313/examples/edge-functions/supabase/functions/wasm-modules/add-wasm/Cargo.toml)

After that we can build the package, by running:

```
1wasm-pack build --target deno
```

This will produce a Wasm binary file inside `add-wasm/pkg` directory.

### Calling the Wasm module from the Edge Function[#](#calling-the-wasm-module-from-the-edge-function)

Now let's update the Edge Function to call `add` from the Wasm module.

```
123456789import { add } from "./add-wasm/pkg/add_wasm.js";Deno.serve(async (req) => {  const { a, b } = await req.json();  return new Response(    JSON.stringify({ result: add(a, b) }),    { headers: { "Content-Type": "application/json" } },  );});
```

[View source](https://github.com/supabase/supabase/blob/cb30f7be2dc31fa93dae25765a5fd28b9b2fa313/examples/edge-functions/supabase/functions/wasm-modules/index.ts)

Supabase Edge Functions currently use Deno 1.46. From [Deno 2.1, importing Wasm modules](https://deno.com/blog/v2.1) will require even less boilerplate code.

### Bundle and deploy the Edge Function[#](#bundle-and-deploy-the-edge-function)

Before deploying the Edge Function, we need to ensure it bundles the Wasm module with it. We can do this by defining it in the `static_files` for the function in `superbase/config.toml`.

You will need update Supabase CLI to 2.7.0 or higher for the `static_files` support.

```
12[functions.wasm-add]static_files = [ "./functions/wasm-add/add-wasm/pkg/*"]
```

Deploy the function by running:

```
1supabase functions deploy wasm-add
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/wasm.mdx)

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