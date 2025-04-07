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

1.  [Troubleshooting](https://supabase.com/docs/guides/troubleshooting)

# Why are there gaps in my Postgres id sequence?

Last edited: 2/21/2025

* * *

Most database tables have a primary key that is a made-up number, and that number is usually made by a sequence.

You might be surprised to know that gaps in sequence IDs are a normal aspect of working with relational databases in general. It's a common scenario that can seem puzzling at first, but there are several reasons why these gaps occur, and sometimes, this is typically expected and does not indicate a problem with your database.

It's also important to understand the distinction that sequences guarantee **uniqueness**, but not **consecutiveness**, and this should not imply any issues relating to data integrity with your database.

### How to check the name of your sequence[#](#how-to-check-the-name-of-your-sequence)

If you don't know the name of your sequence, it's often formed based on a standard naming convention: table\_name\_id\_seq, where table\_name is the name of your table and id is the name of your serial column.

### Common reasons for gaps in sequences[#](#common-reasons-for-gaps-in-sequences)

1.  Rollbacks One of the most common reasons for a gap is the rollback of a transaction. If you initiate a transaction that includes an insert operation, the sequence responsible for generating the ID for the new row increments. If, for any reason, the transaction doesn't complete successfully—perhaps due to a constraint violation or a deliberate decision to rollback—the insert operation is undone, but the sequence value used is not returned or reused. The documentation explains that as well:

> To avoid blocking concurrent transactions that obtain numbers from the same sequence, a `nextval` operation is never rolled back; that is, once a value has been fetched it is considered used and will not be returned again. This is true even if the surrounding transaction later aborts, or if the calling query ends up not using the value. For example an INSERT with an ON CONFLICT clause will compute the to-be-inserted tuple, including doing any required `nextval` calls, before detecting any conflict that would cause it to follow the ON CONFLICT rule instead. Such cases will leave unused “holes” in the sequence of assigned values.

2.  Deletions Removing rows from your table also creates gaps in the sequence of primary key values. Although deletions do not affect the sequence directly, they contribute to the non-sequential appearance of IDs in your table.
    
3.  Manual Sequence Adjustments Another source of gaps can be manual interventions, such as incrementing a sequence number directly or setting it to a new value.
    
4.  Upserts When an upsert is executed, it can still increase the sequence even if it is set to do nothing on conflicts
    

### Checking for gaps[#](#checking-for-gaps)

To check for gaps in the sequence of IDs in a Postgres table, you can use a SQL query that compares the sequence of IDs to a generated series of numbers that spans the same range:

```
1234567SELECT    s.id AS missing_idFROM    generate_series((SELECT MIN(id) FROM your_table), (SELECT MAX(id) FROM your_table)) s(id)    LEFT JOIN your_table ON your_table.id = s.idWHERE    your_table.id IS NULL;
```

This query should help you pinpoint where gaps exist.

### Encountering errors and adjusting sequences[#](#encountering-errors-and-adjusting-sequences)

In operations involving sequences, you might encounter an error message such as:

`Failed to run sql query: duplicate key value violates unique constraint "{table}_pkey"`

This error suggests a discrepancy between the sequence-generated IDs and the actual IDs in the table.

To address this, you can check the current value of your sequence or the highest ID in your table with:

```
123postgres=# SELECT max(id) FROM <table_name>;postgres=# SELECT nextval('{table}_{column}_seq');
```

And reset the sequence value to match the highest ID plus one: `SELECT setval('{table}_{column}_seq', (SELECT max(id) FROM <table_name>) + 1);`

Or, alternatively, adjust the sequence to a specific new value: `ALTER SEQUENCE '{table}_{column}_seq' RESTART WITH new_value;`

### Implementing a gapless ID sequence[#](#implementing-a-gapless-id-sequence)

If your application requires contiguous IDs and you decide to build a gapless sequence. Think twice about this, as it will serialize all transactions that use that “sequence” which will then deteriorate your data modification performance considerably. However, if your application truly requires gapless IDs, then you can use a Trigger: After a successful insert, use a database trigger to assign an ID based on a custom logic that finds the next available gapless ID.

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Related error codes

[](https://supabase.com/docs/guides/troubleshooting?errorCodes=)

* * *

### Tags

[sequence](https://supabase.com/docs/guides/troubleshooting?tags=sequence)[id](https://supabase.com/docs/guides/troubleshooting?tags=id)[rollback](https://supabase.com/docs/guides/troubleshooting?tags=rollback)[deletions](https://supabase.com/docs/guides/troubleshooting?tags=deletions)[upserts](https://supabase.com/docs/guides/troubleshooting?tags=upserts)

* * *

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