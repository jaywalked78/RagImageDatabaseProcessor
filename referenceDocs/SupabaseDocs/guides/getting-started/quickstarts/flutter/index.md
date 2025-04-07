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

5.  [Flutter](https://supabase.com/docs/guides/getting-started/quickstarts/flutter)

# 

Use Supabase with Flutter

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from a Flutter app.

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

### Create a Flutter app

Create a Flutter app using the `flutter create` command. You can skip this step if you already have a working app.

```
1flutter create my_app
```

3

### Install the Supabase client library

The fastest way to get started is to use the [`supabase_flutter`](https://pub.dev/packages/supabase_flutter) client library which provides a convenient interface for working with Supabase from a Flutter app.

Open the `pubspec.yaml` file inside your Flutter app and add `supabase_flutter` as a dependency.

```
1supabase_flutter: ^2.0.0
```

4

### Initialize the Supabase client

Open `lib/main.dart` and edit the main function to initialize Supabase using your project URL and public API (anon) key:

###### Project URL

Loading...

###### Anon key

Loading...

```
1234567891011import 'package:supabase_flutter/supabase_flutter.dart';Future<void> main() async {  WidgetsFlutterBinding.ensureInitialized();  await Supabase.initialize(    url: 'YOUR_SUPABASE_URL',    anonKey: 'YOUR_SUPABASE_ANON_KEY',  );  runApp(MyApp());}
```

5

### Query data from the app

Use a `FutureBuilder` to fetch the data when the home page loads and display the query result in a `ListView`.

Replace the default `MyApp` and `MyHomePage` classes with the following code.

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748class MyApp extends StatelessWidget {  const MyApp({super.key});  @override  Widget build(BuildContext context) {    return const MaterialApp(      title: 'Instruments',      home: HomePage(),    );  }}class HomePage extends StatefulWidget {  const HomePage({super.key});  @override  State<HomePage> createState() => _HomePageState();}class _HomePageState extends State<HomePage> {  final _future = Supabase.instance.client      .from('instruments')      .select();  @override  Widget build(BuildContext context) {    return Scaffold(      body: FutureBuilder(        future: _future,        builder: (context, snapshot) {          if (!snapshot.hasData) {            return const Center(child: CircularProgressIndicator());          }          final instruments = snapshot.data!;          return ListView.builder(            itemCount: instruments.length,            itemBuilder: ((context, index) {              final instrument = instruments[index];              return ListTile(                title: Text(instrument['name']),              );            }),          );        },      ),    );  }}
```

6

### Start the app

Run your app on a platform of your choosing! By default an app should launch in your web browser.

Note that `supabase_flutter` is compatible with web, iOS, Android, macOS, and Windows apps. Running the app on macOS requires additional configuration to [set the entitlements](https://docs.flutter.dev/development/platform-integration/macos/building#setting-up-entitlements).

```
1flutter run
```

## Setup deep links[#](#setup-deep-links)

Many sign in methods require deep links to redirect the user back to your app after authentication. Read more about setting deep links up for all platforms (including web) in the [Flutter Mobile Guide](https://supabase.com/docs/guides/getting-started/tutorials/with-flutter#setup-deep-links).

## Going to production[#](#going-to-production)

### Android[#](#android)

In production, your Android app needs explicit permission to use the internet connection on the user's device which is required to communicate with Supabase APIs. To do this, add the following line to the `android/app/src/main/AndroidManifest.xml` file.

```
12345<manifest xmlns:android="http://schemas.android.com/apk/res/android">  <!-- Required to fetch data from the internet. -->  <uses-permission android:name="android.permission.INTERNET" />  <!-- ... --></manifest>
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/flutter.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)