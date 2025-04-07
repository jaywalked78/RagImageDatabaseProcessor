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

3.  Working with your database (intermediate)

5.  [Using Full Text Search](https://supabase.com/docs/guides/database/full-text-search)

# 

Full Text Search

## 

How to use full text search in PostgreSQL.

* * *

Postgres has built-in functions to handle `Full Text Search` queries. This is like a "search engine" within Postgres.

## Preparation[#](#preparation)

For this guide we'll use the following example data:

DataSQL

| id | title | author | description |
| --- | --- | --- | --- |
| 1 | The Poky Little Puppy | Janette Sebring Lowrey | Puppy is slower than other, bigger animals. |
| 2 | The Tale of Peter Rabbit | Beatrix Potter | Rabbit eats some vegetables. |
| 3 | Tootle | Gertrude Crampton | Little toy train has big dreams. |
| 4 | Green Eggs and Ham | Dr. Seuss | Sam has changing food preferences and eats unusually colored food. |
| 5 | Harry Potter and the Goblet of Fire | J.K. Rowling | Fourth year of school starts, big drama ensues. |

## Usage[#](#usage)

The functions we'll cover in this guide are:

### `to_tsvector()`[#](#to-tsvector)

Converts your data into searchable tokens. `to_tsvector()` stands for "to text search vector." For example:

```
12select to_tsvector('green eggs and ham');-- Returns 'egg':2 'green':1 'ham':4
```

Collectively these tokens are called a "document" which Postgres can use for comparisons.

### `to_tsquery()`[#](#to-tsquery)

Converts a query string into tokens to match. `to_tsquery()` stands for "to text search query."

This conversion step is important because we will want to "fuzzy match" on keywords. For example if a user searches for `eggs`, and a column has the value `egg`, we probably still want to return a match.

### Match: `@@`[#](#match)

The `@@` symbol is the "match" symbol for Full Text Search. It returns any matches between a `to_tsvector` result and a `to_tsquery` result.

Take the following example:

SQLJavaScriptDartSwiftKotlinPython

```
123select *from bookswhere title = 'Harry';
```

The equality symbol above (`=`) is very "strict" on what it matches. In a full text search context, we might want to find all "Harry Potter" books and so we can rewrite the example above:

SQLJavaScriptDartSwiftKotlin

```
123select *from bookswhere to_tsvector(title) @@ to_tsquery('Harry');
```

## Basic full text queries[#](#basic-full-text-queries)

### Search a single column[#](#search-a-single-column)

To find all `books` where the `description` contain the word `big`:

SQLJavaScriptDartSwiftKotlinPythonData

```
1234567select  *from  bookswhere  to_tsvector(description)  @@ to_tsquery('big');
```

### Search multiple columns[#](#search-multiple-columns)

Right now there is no direct way to use JavaScript or Dart to search through multiple columns but you can do it by creating [computed columns](https://postgrest.org/en/stable/api.html#computed-virtual-columns) on the database.

To find all `books` where `description` or `title` contain the word `little`:

SQLJavaScriptDartSwiftKotlinPythonData

```
1234567select  *from  bookswhere  to_tsvector(description || ' ' || title) -- concat columns, but be sure to include a space to separate them!  @@ to_tsquery('little');
```

### Match all search words[#](#match-all-search-words)

To find all `books` where `description` contains BOTH of the words `little` and `big`, we can use the `&` symbol:

SQLJavaScriptDartSwiftKotlinPythonData

```
1234567select  *from  bookswhere  to_tsvector(description)  @@ to_tsquery('little & big'); -- use & for AND in the search query
```

### Match any search words[#](#match-any-search-words)

To find all `books` where `description` contain ANY of the words `little` or `big`, use the `|` symbol:

SQLJavaScriptDartSwiftKotlinPythonData

```
1234567select  *from  bookswhere  to_tsvector(description)  @@ to_tsquery('little | big'); -- use | for OR in the search query
```

Notice how searching for `big` includes results with the word `bigger` (or `biggest`, etc).

## Partial search[#](#partial-search)

Partial search is particularly useful when you want to find matches on substrings within your data.

### Implementing partial search[#](#implementing-partial-search)

You can use the `:*` syntax with `to_tsquery()`. Here's an example that searches for any book titles beginning with "Lit":

```
1select title from books where to_tsvector(title) @@ to_tsquery('Lit:*');
```

### Extending functionality with RPC[#](#extending-functionality-with-rpc)

To make the partial search functionality accessible through the API, you can wrap the search logic in a stored procedure.

After creating this function, you can invoke it from your application using the SDK for your platform. Here's an example:

SQLJavaScriptDartSwiftKotlinPython

```
1234567create or replace function search_books_by_title_prefix(prefix text)returns setof books AS $$begin  return query  select * from books where to_tsvector('english', title) @@ to_tsquery(prefix || ':*');end;$$ language plpgsql;
```

This function takes a prefix parameter and returns all books where the title contains a word starting with that prefix. The `:*` operator is used to denote a prefix match in the `to_tsquery()` function.

## Handling spaces in queries[#](#handling-spaces-in-queries)

When you want the search term to include a phrase or multiple words, you can concatenate words using a `+` as a placeholder for space:

```
1select * from search_books_by_title_prefix('Little+Puppy');
```

## Creating indexes[#](#creating-indexes)

Now that we have Full Text Search working, let's create an `index`. This will allow Postgres to "build" the documents preemptively so that they don't need to be created at the time we execute the query. This will make our queries much faster.

### Searchable columns[#](#searchable-columns)

Let's create a new column `fts` inside the `books` table to store the searchable index of the `title` and `description` columns.

We can use a special feature of Postgres called [Generated Columns](https://www.postgresql.org/docs/current/ddl-generated-columns.html) to ensure that the index is updated any time the values in the `title` and `description` columns change.

SQLData

```
123456789alter table  booksadd column  fts tsvector generated always as (to_tsvector('english', description || ' ' || title)) stored;create index books_fts on books using gin (fts); -- generate the indexselect id, ftsfrom books;
```

### Search using the new column[#](#search-using-the-new-column)

Now that we've created and populated our index, we can search it using the same techniques as before:

SQLJavaScriptDartSwiftKotlinPythonData

```
123456select  *from  bookswhere  fts @@ to_tsquery('little & big');
```

## Query operators[#](#query-operators)

Visit [Postgres: Text Search Functions and Operators](https://www.postgresql.org/docs/current/functions-textsearch.html) to learn about additional query operators you can use to do more advanced `full text queries`, such as:

### Proximity: `<->`[#](#proximity)

The proximity symbol is useful for searching for terms that are a certain "distance" apart. For example, to find the phrase `big dreams`, where the a match for "big" is followed immediately by a match for "dreams":

SQLJavaScriptDartSwiftKotlinPython

```
123456select  *from  bookswhere  to_tsvector(description) @@ to_tsquery('big <-> dreams');
```

We can also use the `<->` to find words within a certain distance of each other. For example to find `year` and `school` within 2 words of each other:

SQLJavaScriptDartSwiftKotlinPython

```
123456select  *from  bookswhere  to_tsvector(description) @@ to_tsquery('year <2> school');
```

### Negation: `!`[#](#negation)

The negation symbol can be used to find phrases which _don't_ contain a search term. For example, to find records that have the word `big` but not `little`:

SQLJavaScriptDartSwiftKotlinPython

```
123456select  *from  bookswhere  to_tsvector(description) @@ to_tsquery('big & !little');
```

## Resources[#](#resources)

-   [Postgres: Text Search Functions and Operators](https://www.postgresql.org/docs/12/functions-textsearch.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/full-text-search.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2Fb-mgca_2Oe4%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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