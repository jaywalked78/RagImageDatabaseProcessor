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

Getting Started

1.  [Start with Supabase](https://supabase.com/docs/guides/getting-started)

3.  Framework Quickstarts

5.  [refine](https://supabase.com/docs/guides/getting-started/quickstarts/refine)

# 

Use Supabase with refine

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from a refine app.

* * *

1

### Create a Supabase project

Go to [database.new](https://database.new) and create a new Supabase project.

When your project is up and running, go to the [Table Editor](https://supabase.com/dashboard/project/_/editor), create a new table and insert some data.

Alternatively, you can run the following snippet in your project's [SQL Editor](https://supabase.com/dashboard/project/_/sql/new). This will create a `instruments` table with some sample data.

```
12345678910111213-- Create the tablecreate table instruments (  id bigint primary key generated always as identity,  name text not null);-- Insert some sample data into the tableinsert into instruments (name)values  ('violin'),  ('viola'),  ('cello');alter table instruments enable row level security;
```

Make the data in your table publicly readable by adding an RLS policy:

```
1234create policy "public can read instruments"on public.instrumentsfor select to anonusing (true);
```

2

### Create a refine app

Create a [refine](https://github.com/refinedev/refine) app using the [create refine-app](https://refine.dev/docs/getting-started/quickstart/).

The `refine-supabase` preset adds `@refinedev/supabase` supplementary package that supports Supabase in a refine app. `@refinedev/supabase` out-of-the-box includes the Supabase dependency: [supabase-js](https://github.com/supabase/supabase-js).

```
1npm create refine-app@latest -- --preset refine-supabase my-app
```

3

### Open your refine app in VS Code

You will develop your app, connect to the Supabase backend and run the refine app in VS Code.

```
12cd my-appcode .
```

4

### Start the app

Start the app, go to [http://localhost:5173](http://localhost:5173) in a browser, and you should be greeted with the refine Welcome page.

```
1npm run dev
```

![refine welcome page](https://supabase.com/docs/img/refine-qs-welcome-page.png)

5

### Update \`supabaseClient\`

You now have to update the `supabaseClient` with the `SUPABASE_URL` and `SUPABASE_KEY` of your Supabase API. The `supabaseClient` is used in auth provider and data provider methods that allow the refine app to connect to your Supabase backend.

###### Project URL

Loading...

###### Anon key

Loading...

```
12345678910111213import { createClient } from "@refinedev/supabase";const SUPABASE_URL = YOUR_SUPABASE_URL;const SUPABASE_KEY = YOUR_SUPABASE_KEYexport const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY, {  db: {    schema: "public",  },  auth: {    persistSession: true,  },});
```

6

### Add instruments resource and pages

You have to then configure resources and define pages for `instruments` resource.

Use the following command to automatically add resources and generate code for pages for `instruments` using refine Inferencer.

This defines pages for `list`, `create`, `show` and `edit` actions inside the `src/pages/instruments/` directory with `<HeadlessInferencer />` component.

The `<HeadlessInferencer />` component depends on `@refinedev/react-table` and `@refinedev/react-hook-form` packages. In order to avoid errors, you should install them as dependencies with `npm install @refinedev/react-table @refinedev/react-hook-form`.

The `<HeadlessInferencer />` is a refine Inferencer component that automatically generates necessary code for the `list`, `create`, `show` and `edit` pages.

More on [how the Inferencer works is available in the docs here](https://refine.dev/docs/packages/documentation/inferencer/).

```
1npm run refine create-resource instruments
```

7

### Add routes for instruments pages

Add routes for the `list`, `create`, `show`, and `edit` pages.

You should remove the `index` route for the Welcome page presented with the `<Welcome />` component.

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556import { Refine, WelcomePage } from "@refinedev/core";import { RefineKbar, RefineKbarProvider } from "@refinedev/kbar";import routerBindings, {  DocumentTitleHandler,  NavigateToResource,  UnsavedChangesNotifier,} from "@refinedev/react-router-v6";import { dataProvider, liveProvider } from "@refinedev/supabase";import { BrowserRouter, Route, Routes } from "react-router-dom";import "./App.css";import authProvider from "./authProvider";import { supabaseClient } from "./utility";import { InstrumentsCreate, InstrumentsEdit, InstrumentsList, InstrumentsShow } from "./pages/instruments";function App() {  return (    <BrowserRouter>      <RefineKbarProvider>        <Refine          dataProvider={dataProvider(supabaseClient)}          liveProvider={liveProvider(supabaseClient)}          authProvider={authProvider}          routerProvider={routerBindings}          options={{            syncWithLocation: true,            warnWhenUnsavedChanges: true,          }}          resources={[{            name: "instruments",            list: "/instruments",            create: "/instruments/create",            edit: "/instruments/edit/:id",            show: "/instruments/show/:id"          }]}>          <Routes>            <Route index              element={<NavigateToResource resource="instruments" />}            />            <Route path="/instruments">              <Route index element={<InstrumentsList />} />              <Route path="create" element={<InstrumentsCreate />} />              <Route path="edit/:id" element={<InstrumentsEdit />} />              <Route path="show/:id" element={<InstrumentsShow />} />            </Route>          </Routes>          <RefineKbar />          <UnsavedChangesNotifier />          <DocumentTitleHandler />        </Refine>      </RefineKbarProvider>    </BrowserRouter>  );}export default App;
```

8

### View instruments pages

Now you should be able to see the instruments pages along the `/instruments` routes. You may now edit and add new instruments using the Inferencer generated UI.

The Inferencer auto-generated code gives you a good starting point on which to keep building your `list`, `create`, `show` and `edit` pages. They can be obtained by clicking the `Show the auto-generated code` buttons in their respective pages.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/refine.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)