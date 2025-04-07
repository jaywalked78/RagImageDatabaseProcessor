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

Auth

1.  Auth

3.  Concepts

5.  [Identities](https://supabase.com/docs/guides/auth/identities)

# 

Identities

* * *

An identity is an authentication method associated with a user. Supabase Auth supports the following types of identity:

-   Email
-   Phone
-   OAuth
-   SAML

A user can have more than one identity. Anonymous users have no identity until they link an identity to their user.

## The user identity object[#](#the-user-identity-object)

The user identity object contains the following attributes:

| Attributes | Type | Description |
| --- | --- | --- |
| provider\_id | `string` | The provider id returned by the provider. If the provider is an OAuth provider, the id refers to the user's account with the OAuth provider. If the provider is `email` or `phone`, the id is the user's id from the `auth.users` table. |
| user\_id | `string` | The user's id that the identity is linked to. |
| identity\_data | `object` | The identity metadata. For OAuth and SAML identities, this contains information about the user from the provider. |
| id | `string` | The unique id of the identity. |
| provider | `string` | The provider name. |
| email | `string` | The email is a generated column that references the optional email property in the identity\_data |
| created\_at | `string` | The timestamp that the identity was created. |
| last\_sign\_in\_at | `string` | The timestamp that the identity was last used to sign in. |
| updated\_at | `string` | The timestamp that the identity was last updated. |

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/identities.mdx)

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