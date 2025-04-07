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

3.  Examples

5.  [Image Transformation & Optimization](https://supabase.com/docs/guides/functions/examples/image-manipulation)

# 

Image Manipulation

* * *

Supabase Storage has [out-of-the-box support](https://supabase.com/docs/guides/storage/serving/image-transformations?queryGroups=language&language=js) for the most common image transformations and optimizations you need. If you need to do anything custom beyond what Supabase Storage provides, you can use Edge Functions to write custom image manipulation scripts.

In this example, we will use [`magick-wasm`](https://github.com/dlemstra/magick-wasm) to perform image manipulations. `magick-wasm` is the WebAssembly port of the popular ImageMagick library and supports processing over 100 file formats.

Edge Functions currently doesn't support image processing libraries such as `Sharp`, which depend on native libraries. Only WASM-based libraries are supported.

### Prerequisites[#](#prerequisites)

Make sure you have the latest version of the [Supabase CLI](https://supabase.com/docs/guides/cli#installation) installed.

### Create the Edge Function[#](#create-the-edge-function)

Create a new function locally:

```
1supabase functions new image-blur
```

### Write the function[#](#write-the-function)

In this example, we are implementing a function allowing users to upload an image and get a blurred thumbnail.

Here's the implementation in `index.ts` file:

```
1234567891011121314151617181920212223242526272829303132333435363738394041// This is an example showing how to use Magick WASM to do image manipulations in Edge Functions.//import {  ImageMagick,  initializeImageMagick,  MagickFormat,} from "npm:@imagemagick/magick-wasm@0.0.30";const wasmBytes = await Deno.readFile(  new URL(    "magick.wasm",    import.meta.resolve("npm:@imagemagick/magick-wasm@0.0.30"),  ),);await initializeImageMagick(  wasmBytes,);Deno.serve(async (req) => {  const formData = await req.formData();  const content = await formData.get("file").bytes();  let result = ImageMagick.read(    content,    (img): Uint8Array => {      // resize the image      img.resize(500, 300);      // add a blur of 60x5      img.blur(60, 5);      return img.write(        (data) => data,      );    },  );  return new Response(    result,    { headers: { "Content-Type": "image/png" } },  );});
```

[View source](https://github.com/supabase/supabase/blob/cb30f7be2dc31fa93dae25765a5fd28b9b2fa313/examples/edge-functions/supabase/functions/image-manipulation/index.ts)

### Test it locally[#](#test-it-locally)

You can test the function locally by running:

```
12supabase startsupabase functions serve --no-verify-jwt
```

Then, make a request using `curl` or your favorite API testing tool.

```
123curl --location '<http://localhost:54321/functions/v1/image-blur>' \\--form 'file=@"/path/to/image.png"'--output '/path/to/output.png'
```

If you open the `output.png` file you will find a transformed version of your original image.

### Deploy to your hosted project[#](#deploy-to-your-hosted-project)

Now, let's deploy the function to your Supabase project.

```
12supabase linksupabase functions deploy image-blur
```

Hosted Edge Functions have [limits](https://supabase.com/docs/guides/functions/limits) on memory and CPU usage.

If you try to perform complex image processing or handle large images (> 5MB) your function may return a resource limit exceeded error.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/examples/image-manipulation.mdx)

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