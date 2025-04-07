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

5.  [Ruby on Rails](https://supabase.com/docs/guides/getting-started/quickstarts/ruby-on-rails)

# 

Use Supabase with Ruby on Rails

## 

Learn how to create a Rails project and connect it to your Supabase Postgres database.

* * *

1

### Create a Rails Project

Make sure your Ruby and Rails versions are up to date, then use `rails new` to scaffold a new Rails project. Use the `-d=postgresql` flag to set it up for Postgres.

Go to the [Rails docs](https://guides.rubyonrails.org/getting_started.html) for more details.

```
1rails new blog -d=postgresql
```

2

### Set up the Postgres connection details

Go to [database.new](https://database.new) and create a new Supabase project. Save your database password securely.

When your project is up and running, navigate to the [database settings](https://supabase.com/dashboard/project/_/settings/database) to find the URI connection string. Make sure **Use connection pooling** is checked and **Session mode** is selected. Then copy the URI. Replace the password placeholder with your saved database password.

If your network supports IPv6 connections, you can also use the direct connection string. Uncheck **Use connection pooling** and copy the new URI.

```
1export DATABASE_URL=postgres://postgres.xxxx:password@xxxx.pooler.supabase.com:5432/postgres
```

3

### Create and run a database migration

Rails includes Active Record as the ORM as well as database migration tooling which generates the SQL migration files for you.

Create an example `Article` model and generate the migration files.

```
12bin/rails generate model Article title:string body:textbin/rails db:migrate
```

4

### Use the Model to interact with the database

You can use the included Rails console to interact with the database. For example, you can create new entries or list all entries in a Model's table.

```
1bin/rails console
```

```
1234article = Article.new(title: "Hello Rails", body: "I am on Rails!")article.save # Saves the entry to the databaseArticle.all
```

5

### Start the app

Run the development server. Go to [http://127.0.0.1:3000](http://127.0.0.1:3000) in a browser to see your application running.

```
1bin/rails server
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/quickstarts/ruby-on-rails.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)