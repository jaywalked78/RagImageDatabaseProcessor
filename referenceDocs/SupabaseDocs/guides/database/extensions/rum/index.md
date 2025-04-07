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

5.  [RUM: inverted index for full-text search](https://supabase.com/docs/guides/database/extensions/rum)

# 

RUM: improved inverted index for full-text search based on GIN index

* * *

[RUM](https://github.com/postgrespro/rum) is an extension which adds a RUM index to Postgres.

RUM index is based on GIN that stores additional per-entry information in a posting tree. For example, positional information of lexemes or timestamps. In comparison to GIN it can use this information to make faster index-only scans for:

-   Phrase search
-   Text search with ranking by text distance operator
-   Text `SELECT`s with ordering by some non-indexed additional column e.g. by timestamp.

RUM works best in scenarios when the possible keys are highly repeatable. I.e. all texts are composed of a limited amount of words, so per-lexeme indexing gives significant speed-up in searching texts containing word combinations or phrases.

Main operators for ordering are:

`tsvector` `<=>` `tsquery` | `float4` | Distance between `tsvector` and `tsquery`. value `<=>` value | `float8` | Distance between two values.

Where value is `timestamp`, `timestamptz`, `int2`, `int4`, `int8`, `float4`, `float8`, `money` and `oid`

## Usage[#](#usage)

### Enable the extension[#](#enable-the-extension)

You can get started with rum by enabling the extension in your Supabase dashboard.

DashboardSQL

1.  Go to the [Database](https://supabase.com/dashboard/project/_/database/tables) page in the Dashboard.
2.  Click on **Extensions** in the sidebar.
3.  Search for "rum" and enable the extension.

### Syntax[#](#syntax)

#### For type: `tsvector`[#](#for-type-tsvector)

To understand the following you may need first to see [Official Postgres documentation on text search](https://www.postgresql.org/docs/current/functions-textsearch.html)

`rum_tsvector_ops`

```
1234567891011CREATE TABLE test_rum(t text, a tsvector);CREATE TRIGGER tsvectorupdateBEFORE UPDATE OR INSERT ON test_rumFOR EACH ROW EXECUTE PROCEDURE tsvector_update_trigger('a', 'pg_catalog.english', 't');INSERT INTO test_rum(t) VALUES ('The situation is most beautiful');INSERT INTO test_rum(t) VALUES ('It is a beautiful');INSERT INTO test_rum(t) VALUES ('It looks like a beautiful place');CREATE INDEX rumidx ON test_rum USING rum (a rum_tsvector_ops);
```

And we can execute `tsvector` selects with ordering by text distance operator:

```
12345678910SELECT t, a `<=>` to_tsquery('english', 'beautiful | place') AS rank    FROM test_rum    WHERE a @@ to_tsquery('english', 'beautiful | place')    ORDER BY a `<=>` to_tsquery('english', 'beautiful | place');                t                |  rank---------------------------------+--------- It looks like a beautiful place | 8.22467 The situation is most beautiful | 16.4493 It is a beautiful               | 16.4493(3 rows)
```

`rum_tsvector_addon_ops`

```
123CREATE TABLE tsts (id int, t tsvector, d timestamp);CREATE INDEX tsts_idx ON tsts USING rum (t rum_tsvector_addon_ops, d)    WITH (attach = 'd', to = 't');
```

Now we can execute the selects with ordering distance operator on attached column:

```
123456789SELECT id, d, d `<=>` '2016-05-16 14:21:25' FROM tsts WHERE t @@ 'wr&qh' ORDER BY d `<=>` '2016-05-16 14:21:25' LIMIT 5; id  |                d                |   ?column?-----+---------------------------------+--------------- 355 | Mon May 16 14:21:22.326724 2016 |      2.673276 354 | Mon May 16 13:21:22.326724 2016 |   3602.673276 371 | Tue May 17 06:21:22.326724 2016 |  57597.326724 406 | Wed May 18 17:21:22.326724 2016 | 183597.326724 415 | Thu May 19 02:21:22.326724 2016 | 215997.326724(5 rows)
```

#### For type: `anyarray`[#](#for-type-anyarray)

`rum_anyarray_ops`

This operator class stores `anyarray` elements with length of the array. It supports operators `&&`, `@>`, `<@`, `=`, `%` operators. It also supports ordering by `<=>` operator.

```
123CREATE TABLE test_array (i int2[]);INSERT INTO test_array VALUES ('{}'), ('{0}'), ('{1,2,3,4}'), ('{1,2,3}'), ('{1,2}'), ('{1}');CREATE INDEX idx_array ON test_array USING rum (i rum_anyarray_ops);
```

Now we can execute the query using index scan:

```
12345678SELECT * FROM test_array WHERE i && '{1}' ORDER BY i `<=>` '{1}' ASC;     i----------- {1} {1,2} {1,2,3} {1,2,3,4}(4 rows)
```

`rum_anyarray_addon_ops`

The does the same with `anyarray` index as `rum_tsvector_addon_ops` i.e. allows to order select results using distance operator by attached column.

## Limitations[#](#limitations)

`RUM` has slower build and insert times than `GIN` due to:

1.  It is bigger due to the additional attributes stored in the index.
2.  It uses generic WAL records.

## Resources[#](#resources)

-   [Official RUM documentation](https://github.com/postgrespro/rum)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/rum.mdx)

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