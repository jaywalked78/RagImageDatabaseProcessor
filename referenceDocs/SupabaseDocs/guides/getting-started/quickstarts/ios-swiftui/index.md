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

5.  [iOS SwiftUI](https://supabase.com/docs/guides/getting-started/quickstarts/ios-swiftui)

# 

Use Supabase with iOS and SwiftUI

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from an iOS app.

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

### Create an iOS SwiftUI app with Xcode

Open Xcode > New Project > iOS > App. You can skip this step if you already have a working app.

3

### Install the Supabase client library

Install Supabase package dependency using Xcode by following Apple's [tutorial](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app).

Make sure to add `Supabase` product package as dependency to the application.

4

### Initialize the Supabase client

Create a new `Supabase.swift` file add a new Supabase instance using your project URL and public API (anon) key:

###### Project URL

Loading...

###### Anon key

Loading...

```
123456import Supabaselet supabase = SupabaseClient(  supabaseURL: URL(string: "YOUR_SUPABASE_URL")!,  supabaseKey: "YOUR_SUPABASE_ANON_KEY")
```

5

### Create a data model for instruments

Create a decodable struct to deserialize the data from the database.

Add the following code to a new file named `Instrument.swift`.

```
1234struct Instrument: Decodable, Identifiable {  let id: Int  let name: String}
```

6

### Query data from the app

Use a `task` to fetch the data from the database and display it using a `List`.

Replace the default `ContentView` with the following code.

```
12345678910111213141516171819202122struct ContentView: View {  @State var instruments: [Instrument] = []  var body: some View {    List(instruments) { instrument in      Text(instrument.name)    }    .overlay {      if instruments.isEmpty {        ProgressView()      }    }    .task {      do {        instruments = try await supabase.from("instruments").select().execute().value      } catch {        dump(error)      }    }  }}
```

7

### Start the app

Run the app on a simulator or a physical device by hitting `Cmd + R` on Xcode.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/ios-swiftui.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)