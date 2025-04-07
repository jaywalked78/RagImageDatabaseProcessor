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

3.  Security

5.  [Password Security](https://supabase.com/docs/guides/auth/password-security)

# 

Password security

## 

Help your users to protect their password security

* * *

A password is more secure if it is harder to guess or brute-force. In theory, a password is harder to guess if it is longer. It is also harder to guess if it uses a larger set of characters (for example, digits, lowercase and uppercase letters, and symbols).

This table shows the _minimum_ number of guesses that need to be tried to access a user's account:

| Required characters | Length | Guesses |
| --- | --- | --- |
| Digits only | 8 | ~ 227 |
| Digits and letters | 8 | ~ 241 |
| Digits, lower and uppercase letters | 8 | ~ 248 |
| Digits, lower and uppercase letters, symbols | 8 | ~ 252 |

In reality though, passwords are not always generated at random. They often contain variations of names, words, dates, and common phrases. Malicious actors can use these properties to guess a password in fewer attempts.

There are hundreds of millions (and growing!) known passwords out there. Malicious actors can use these lists of leaked passwords to automate login attempts (known as credential stuffing) and steal or access sensitive user data.

## Password strength and leaked password protection[#](#password-strength-and-leaked-password-protection)

To help protect your users, Supabase Auth allows you fine-grained control over the strength of the passwords used on your project. You can configure these in your project's [Auth settings](https://supabase.com/dashboard/project/_/settings/auth):

-   Set a large minimum password length. Anything less than 8 characters is not recommended.
-   Set the required characters that must appear at least once in a user's password. Use the strongest option of requiring digits, lowercase and uppercase letters, and symbols.
-   Prevent the use of leaked passwords. Supabase Auth uses the open-source [HaveIBeenPwned.org Pwned Passwords API](https://haveibeenpwned.com/Passwords) to reject passwords that have been leaked and are known by malicious actors.

## Additional recommendations[#](#additional-recommendations)

In addition to choosing suitable password strength settings and preventing the use of leaked passwords, consider asking your users to:

-   Use a password manager to store and generate passwords.
-   Avoid password reuse across websites and apps.
-   Avoid using personal information in passwords.
-   Use [Multi-Factor Authentication](https://supabase.com/docs/guides/auth/auth-mfa).

## Frequently asked questions[#](#frequently-asked-questions)

### How are passwords stored?[#](#how-are-passwords-stored)

Supabase Auth uses [bcrypt](https://en.wikipedia.org/wiki/Bcrypt), a strong password hashing function, to store hashes of users' passwords. Only hashed passwords are stored. You cannot impersonate a user with the password hash. Each hash is accompanied by a randomly generated salt parameter for extra security.

The hash is stored in the `encrypted_password` column of the `auth.users` table. The column's name is a misnomer (cryptographic hashing is not encryption), but is kept for backward compatibility.

### How will strengthened password requirements affect current users?[#](#how-will-strengthened-password-requirements-affect-current-users)

Existing users can still sign in with their current password even if it doesn't meet the new, strengthened password requirements. However, if their password falls short of these updated standards, they will encounter a `WeakPasswordError` during the `signInWithPassword` process, explaining why it's considered weak. This change is also applicable to new users and existing users changing their passwords, ensuring everyone adheres to the enhanced security standards.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/password-security.mdx)

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