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

# How to Migrate from Supabase Auth Helpers to SSR package

Last edited: 2/21/2025

* * *

The `auth-helpers` packages are being deprecated and replaced with the `@supabase/ssr` package. We recommend migrating to the `@supabase/ssr` package as future bug fixes and feature releases are focused on the `@supabase/ssr` package.

Here are the steps for you to migrate your application from the `auth-helpers` package to `@supabase/ssr` package.

Depending on your implementation, you may ignore some parts of this documentation and use your own implementation (i.e. using API routes vs. Server Actions). What’s important is you replace the clients provided by `auth-helpers` with the utility functions created using clients provided by `@supabase/ssr`.

### 1\. Uninstall Supabase Auth helpers and install the Supabase SSR package[#](#1-uninstall-supabase-auth-helpers-and-install-the-supabase-ssr-package)

It’s important that you don’t use both `auth-helpers-nextjs` and `@supabase/ssr` packages in the same application to avoid running into authentication issues.

```
12npm uninstall @supabase/auth-helpers-nextjs @supabase/supabase-jsnpm install @supabase/ssr @supabase/supabase-js
```

### 2\. Create the utility functions to create Supabase clients.[#](#2-create-the-utility-functions-to-create-supabase-clients)

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106// utils/supabase/client.tsimport { createBrowserClient } from '@supabase/ssr';export function createClient() {  return createBrowserClient(    process.env.NEXT_PUBLIC_SUPABASE_URL!,    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!  );}// utils/supabase/server.tsimport { createServerClient, type CookieOptions } from '@supabase/ssr';import { cookies } from 'next/headers';export function createClient() {  const cookieStore = cookies();  return createServerClient(    process.env.NEXT_PUBLIC_SUPABASE_URL!,    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,    {      cookies: {        getAll() {          return cookieStore.getAll()        },        setAll(cookiesToSet) {          try {            cookiesToSet.forEach(({ name, value, options }) =>              cookieStore.set(name, value, options)            )          } catch {            // The `setAll` method was called from a Server Component.            // This can be ignored if you have middleware refreshing            // user sessions.          }        },      },    }  );}// utils/supabase/middleware.tsimport { createServerClient } from '@supabase/ssr';import { NextResponse, type NextRequest } from 'next/server';export async function updateSession(request: NextRequest) {  let supabaseResponse = NextResponse.next({    request,  });  const supabase = createServerClient(    process.env.NEXT_PUBLIC_SUPABASE_URL!,    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,    {      cookies: {        getAll() {          return request.cookies.getAll()        },        setAll(cookiesToSet) {          cookiesToSet.forEach(({ name, value, options }) => request.cookies.set(name, value))          supabaseResponse = NextResponse.next({            request,          })          cookiesToSet.forEach(({ name, value, options }) =>            supabaseResponse.cookies.set(name, value, options)          )        },      },    }  );  // IMPORTANT: Avoid writing any logic between createServerClient and  // supabase.auth.getUser(). A simple mistake could make it very hard to debug  // issues with users being randomly logged out.  const {    data: { user },  } = await supabase.auth.getUser();  if (    !user &&    !request.nextUrl.pathname.startsWith('/login') &&    !request.nextUrl.pathname.startsWith('/auth')  ) {    // no user, potentially respond by redirecting the user to the login page    const url = request.nextUrl.clone();    url.pathname = '/login';    return NextResponse.redirect(url);  }  // IMPORTANT: You *must* return the supabaseResponse object as it is. If you're  // creating a new response object with NextResponse.next() make sure to:  // 1. Pass the request in it, like so:  //    const myNewResponse = NextResponse.next({ request })  // 2. Copy over the cookies, like so:  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())  // 3. Change the myNewResponse object to fit your needs, but avoid changing  //    the cookies!  // 4. Finally:  //    return myNewResponse  // If this is not done, you may be causing the browser and server to go out  // of sync and terminate the user's session prematurely!  return supabaseResponse;}
```

### 3\. Replace your middleware.ts file[#](#3-replace-your-middlewarets-file)

```
123456789101112131415161718192021// middleware.tsimport { type NextRequest } from 'next/server';import { updateSession } from '@/utils/supabase/middleware';export async function middleware(request: NextRequest) {  return await updateSession(request);}export const config = {  matcher: [    /*     * Match all request paths except for the ones starting with:     * - _next/static (static files)     * - _next/image (image optimization files)     * - favicon.ico (favicon file)     * Feel free to modify this pattern to include more paths.     */    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',  ],};
```

### 4\. Create your server actions to handle login and sign up.[#](#4-create-your-server-actions-to-handle-login-and-sign-up)

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748// app/login/actions.ts'use server';import { revalidatePath } from 'next/cache';import { redirect } from 'next/navigation';import { createClient } from '@/utils/supabase/server';export async function login(formData: FormData) {  const supabase = createClient();  // type-casting here for convenience  // in practice, you should validate your inputs  const data = {    email: formData.get('email') as string,    password: formData.get('password') as string,  };  const { error } = await supabase.auth.signInWithPassword(data)  if (error) {    redirect('/error');  }  revalidatePath('/', 'layout');  redirect('/');}export async function signup(formData: FormData) {  const supabase = createClient();  // type-casting here for convenience  // in practice, you should validate your inputs  const data = {    email: formData.get('email') as string,    password: formData.get('password') as string,  };  const { error } = await supabase.auth.signUp(data);  if (error) {    redirect('/error');  }  revalidatePath('/', 'layout');  redirect('/');}
```

### 5\. Utilize the server actions in your login page UI.[#](#5-utilize-the-server-actions-in-your-login-page-ui)

```
12345678910111213141516// app/login/page.tsximport { login, signup } from './actions';export default function LoginPage() {  return (    <form>      <label htmlFor="email">Email:</label>      <input id="email" name="email" type="email" required />      <label htmlFor="password">Password:</label>      <input id="password" name="password" type="password" required />      <button formAction={login}>Log in</button>      <button formAction={signup}>Sign up</button>    </form>  );}
```

### 6\. Client components[#](#6-client-components)

```
1234567891011121314151617'use client';// replace this lineimport { createClientComponentClient } from '@supabase/auth-helpers-nextjs';// withimport { createClient } from '@/utils/supabase/client';export default async function Page() {	// replace this line	const supabase = createClientComponentClient<Database>();	// with	const supabase = createClient();	return...}
```

### 7\. Server components[#](#7-server-components)

```
12345678910111213141516171819// replaceimport { cookies } from 'next/headers';import { createServerComponentClient } from '@supabase/auth-helpers-nextjs';// withimport { createClient } from '@/utils/supabase/server';export default async function Page() {	// replace	const cookieStore = cookies();	const supabase = createServerComponentClient<Database>({		cookies: () => cookieStore	});	// with	const supabase = createClient();	return...}
```

### 8\. Route handlers[#](#8-route-handlers)

```
123456789101112131415161718// replaceimport { createRouteHandlerClient } from '@supabase/auth-helpers-nextjs';import { cookies } from 'next/headers';// withimport { createClient } from '@/utils/supabase/server';export async function POST(request: Request) {	// replace	const supabase = createRouteHandlerClient<Database>({    cookies: () => cookieStore,  });  // with  const supabase = createClient();  return...}
```

Likewise, you can replace the clients created with `@supabase/auth-helpers-nextjs` with utility functions you created with `@supabase/ssr`.

`createMiddlewareClient` → `createServerClient` `createClientComponentClient` → `createBrowserClient` `createServerComponentClient` → `createServerClient` `createRouteHandlerClient` → `createServerClient`

You can find more clear and concise examples of creating clients in our documentation [here](https://supabase.com/docs/guides/auth/server-side/creating-a-client?queryGroups=framework&framework=nextjs&queryGroups=environment&environment=route-handler#creating-a-client).

If you have any feedback about this guide, provide them as a comment below. If you find any issues or have feedback for the `@supabase/ssr` client, post them as an issue in `@supabase/ssr` repo.

As always, our GitHub community and Discord channel are open for technical discussions and resolving your issues.

## Metadata

* * *

### Products

[Auth](https://supabase.com/docs/guides/troubleshooting?products=auth)

* * *

### Tags

[migration](https://supabase.com/docs/guides/troubleshooting?tags=migration)[auth](https://supabase.com/docs/guides/troubleshooting?tags=auth)[ssr](https://supabase.com/docs/guides/troubleshooting?tags=ssr)[package](https://supabase.com/docs/guides/troubleshooting?tags=package)

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