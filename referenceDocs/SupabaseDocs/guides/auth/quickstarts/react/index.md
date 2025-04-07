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

3.  Getting Started

5.  [React](https://supabase.com/docs/guides/auth/quickstarts/react)

# 

Use Supabase Auth with React

## 

Learn how to use Supabase Auth with React.js.

* * *

1

### Create a new Supabase project

[Launch a new project](https://supabase.com/dashboard) in the Supabase Dashboard.

Your new database has a table for storing your users. You can see that this table is currently empty by running some SQL in the [SQL Editor](https://supabase.com/dashboard/project/_/sql).

```
1select * from auth.users;
```

2

### Create a React app

Create a React app using the `create-react-app` command.

```
1npx create-react-app my-app
```

3

### Install the Supabase client library

The fastest way to get started is to use Supabase's `auth-ui-react` library which provides a convenient interface for working with Supabase Auth from a React app.

Navigate to the React app and install the Supabase libraries.

```
1cd my-app && npm install @supabase/supabase-js @supabase/auth-ui-react @supabase/auth-ui-shared
```

4

### Set up your login component

In `App.js`, create a Supabase client using your [Project URL and public API (anon) key](https://supabase.com/dashboard/project/_/settings/api).

You can configure the Auth component to display whenever there is no session inside `supabase.auth.getSession()`

```
1234567891011121314151617181920212223242526272829303132import './index.css'  import { useState, useEffect } from 'react'  import { createClient } from '@supabase/supabase-js'  import { Auth } from '@supabase/auth-ui-react'  import { ThemeSupa } from '@supabase/auth-ui-shared'  const supabase = createClient('https://<project>.supabase.co', '<your-anon-key>')  export default function App() {    const [session, setSession] = useState(null)    useEffect(() => {      supabase.auth.getSession().then(({ data: { session } }) => {        setSession(session)      })      const {        data: { subscription },      } = supabase.auth.onAuthStateChange((_event, session) => {        setSession(session)      })      return () => subscription.unsubscribe()    }, [])    if (!session) {      return (<Auth supabaseClient={supabase} appearance={{ theme: ThemeSupa }} />)    }    else {      return (<div>Logged in!</div>)    }  }
```

5

### Start the app

Start the app, go to [http://localhost:3000](http://localhost:3000) in a browser, and open the browser console and you should be able to log in.

```
1npm start
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/quickstarts/react.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)