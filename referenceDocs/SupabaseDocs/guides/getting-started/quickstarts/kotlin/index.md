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

5.  [Android Kotlin](https://supabase.com/docs/guides/getting-started/quickstarts/kotlin)

# 

Use Supabase with Android Kotlin

## 

Learn how to create a Supabase project, add some sample data to your database, and query the data from an Android Kotlin app.

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

### Create an Android app with Android Studio

Open Android Studio > New > New Android Project.

3

### Install the Dependencies

Open `build.gradle.kts` (app) file and add the serialization plug, Ktor client, and Supabase client.

Replace the version placeholders `$kotlin_version` with the Kotlin version of the project, and `$supabase_version` and `$ktor_version` with the respective latest versions.

The latest supabase-kt version can be found [here](https://github.com/supabase-community/supabase-kt/releases) and Ktor version can be found [here](https://ktor.io/docs/welcome.html).

```
1234567891011plugins {  ...  kotlin("plugin.serialization") version "$kotlin_version"}...dependencies {  ...  implementation(platform("io.github.jan-tennert.supabase:bom:$supabase_version"))  implementation("io.github.jan-tennert.supabase:postgrest-kt")  implementation("io.ktor:ktor-client-android:$ktor_version")}
```

4

### Add internet access permission

Add the following line to the `AndroidManifest.xml` file under the `manifest` tag and outside the `application` tag.

```
123...<uses-permission android:name="android.permission.INTERNET" />...
```

5

### Initialize the Supabase client

You can create a Supabase client whenever you need to perform an API call.

For the sake of simplicity, we will create a client in the `MainActivity.kt` file at the top just below the imports.

Replace the `supabaseUrl` and `supabaseKey` with your own:

###### Project URL

Loading...

###### Anon key

Loading...

```
123456789import ...val supabase = createSupabaseClient(    supabaseUrl = "https://xyzcompany.supabase.co",    supabaseKey = "your_public_anon_key"  ) {    install(Postgrest)}...
```

6

### Create a data model for instruments

Create a serializable data class to represent the data from the database.

Add the following below the `createSupabaseClient` function in the `MainActivity.kt` file.

```
12345@Serializabledata class Instrument(    val id: Int,    val name: String,)
```

7

### Query data from the app

Use `LaunchedEffect` to fetch data from the database and display it in a `LazyColumn`.

Replace the default `MainActivity` class with the following code.

Note that we are making a network request from our UI code. In production, you should probably use a `ViewModel` to separate the UI and data fetching logic.

```
1234567891011121314151617181920212223242526272829303132333435363738class MainActivity : ComponentActivity() {    override fun onCreate(savedInstanceState: Bundle?) {        super.onCreate(savedInstanceState)        setContent {            SupabaseTutorialTheme {                // A surface container using the 'background' color from the theme                Surface(                    modifier = Modifier.fillMaxSize(),                    color = MaterialTheme.colorScheme.background                ) {                    InstrumentsList()                }            }        }    }}@Composablefun InstrumentsList() {    var instruments by remember { mutableStateOf<List<Instrument>>(listOf()) }    LaunchedEffect(Unit) {        withContext(Dispatchers.IO) {            instruments = supabase.from("instruments")                              .select().decodeList<Instrument>()        }    }    LazyColumn {        items(            instruments,            key = { instrument -> instrument.id },        ) { instrument ->            Text(                instrument.name,                modifier = Modifier.padding(8.dp),            )        }    }}
```

8

### Start the app

Run the app on an emulator or a physical device by clicking the `Run app` button in Android Studio.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/kotlin.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)