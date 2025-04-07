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

3.  Extensions

5.  [pgjwt: JSON Web Tokens](https://supabase.com/docs/guides/database/extensions/pgjwt)

# 

pgjwt: JSON Web Tokens

* * *

The [`pgjwt`](https://github.com/michelp/pgjwt) (PostgreSQL JSON Web Token) extension allows you to create and parse [JSON Web Tokens (JWTs)](https://en.wikipedia.org/wiki/JSON_Web_Token) within a PostgreSQL database. JWTs are commonly used for authentication and authorization in web applications and services.

## Enable the extension[#](#enable-the-extension)

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for `pgjwt` and enable the extension.

## API[#](#api)

-   [`sign(payload json, secret text, algorithm text default 'HSA256')`](https://github.com/michelp/pgjwt#usage): Signs a JWT containing _payload_ with _secret_ using _algorithm_.
-   [`verify(token text, secret text, algorithm text default 'HSA256')`](https://github.com/michelp/pgjwt#usage): Decodes a JWT _token_ that was signed with _secret_ using _algorithm_.

Where:

-   `payload` is an encrypted JWT represented as a string.
-   `secret` is the private/secret passcode which is used to sign the JWT and verify its integrity.
-   `algorithm` is the method used to sign the JWT using the secret.
-   `token` is an encrypted JWT represented as a string.

## Usage[#](#usage)

Once the extension is installed, you can use its functions to create and parse JWTs. Here's an example of how you can use the `sign` function to create a JWT:

```
123456select  extensions.sign(    payload   := '{"sub":"1234567890","name":"John Doe","iat":1516239022}',    secret    := 'secret',    algorithm := 'HS256'  );
```

The `pgjwt_encode` function returns a string that represents the JWT, which can then be safely transmitted between parties.

```
12345678sign--------------------------------- eyJhbGciOiJIUzI1NiIsInR5cCI6IkpX VCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiw ibmFtZSI6IkpvaG4gRG9lIiwiaWF0Ijo xNTE2MjM5MDIyfQ.XbPfbIHMI6arZ3Y9 22BhjWgQzWXcXNrz0ogtVhfEd2o(1 row)
```

To parse a JWT and extract its claims, you can use the `verify` function. Here's an example:

```
123456select  extensions.verify(    token := 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYW1lIjoiRm9vIn0.Q8hKjuadCEhnCPuqIj9bfLhTh_9QSxshTRsA5Aq4IuM',    secret    := 'secret',    algorithm := 'HS256'  );
```

Which returns the decoded contents and some associated metadata.

```
1234header            |    payload     | valid-----------------------------+----------------+------- {"alg":"HS256","typ":"JWT"} | {"name":"Foo"} | t(1 row)
```

## Resources[#](#resources)

-   Official [`pgjwt` documentation](https://github.com/michelp/pgjwt)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pgjwt.mdx)

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