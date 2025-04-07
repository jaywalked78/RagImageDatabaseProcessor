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

5.  [Implementing cascade deletes](https://supabase.com/docs/guides/database/postgres/cascade-deletes)

# 

Cascade Deletes

* * *

There are 5 options for foreign key constraint deletes:

1.  **CASCADE:** When a row is deleted from the parent table, all related rows in the child tables are deleted as well.
2.  **RESTRICT:** When a row is deleted from the parent table, the delete operation is aborted if there are any related rows in the child tables.
3.  **SET NULL:** When a row is deleted from the parent table, the values of the foreign key columns in the child tables are set to NULL.
4.  **SET DEFAULT:** When a row is deleted from the parent table, the values of the foreign key columns in the child tables are set to their default values.
5.  **NO ACTION:** This option is similar to RESTRICT, but it also has the option to be “deferred” to the end of a transaction. This means that other cascading deletes can run first, and then this delete constraint will only throw an error if there is referenced data remaining _at the end of the transaction_.

These options can be specified when defining a foreign key constraint using the "ON DELETE" clause. For example, the following SQL statement creates a foreign key constraint with the `CASCADE` option:

```
123alter table child_tableadd constraint fk_parent foreign key (parent_id) references parent_table (id)  on delete cascade;
```

This means that when a row is deleted from the `parent_table`, all related rows in the `child_table` will be deleted as well.

## `RESTRICT` vs `NO ACTION`[#](#restrict-vs-no-action)

The difference between `NO ACTION` and `RESTRICT` is subtle and can be a bit confusing.

Both `NO ACTION` and `RESTRICT` are used to prevent deletion of a row in a parent table if there are related rows in a child table. However, there is a subtle difference in how they behave.

When a foreign key constraint is defined with the option `RESTRICT`, it means that if a row in the parent table is deleted, the database will immediately raise an error and prevent the deletion of the row in the parent table. The database will not delete, update or set to NULL any rows in the referenced tables.

When a foreign key constraint is defined with the option `NO ACTION`, it means that if a row in the parent table is deleted, the database will also raise an error and prevent the deletion of the row in the parent table. However unlike `RESTRICT`, `NO ACTION` has the option defer the check using `INITIALLY DEFERRED`. This will only raise the above error _if_ the referenced rows still exist at the end of the transaction.

The difference from `RESTRICT` is that a constraint marked as `NO ACTION INITIALLY DEFERRED` is deferred until the end of the transaction, rather than running immediately. If, for example there is another foreign key constraint between the same tables marked as `CASCADE`, the cascade will occur first and delete the referenced rows, and no error will be thrown by the deferred constraint. Otherwise if there are still rows referencing the parent row by the end of the transaction, an error will be raised just like before. Just like `RESTRICT`, the database will not delete, update or set to NULL any rows in the referenced tables.

In practice, you can use either `NO ACTION` or `RESTRICT` depending on your needs. `NO ACTION` is the default behavior if you do not specify anything. If you prefer to defer the check until the end of the transaction, use `NO ACTION INITIALLY DEFERRED`.

## Example[#](#example)

Let's further illustrate the difference with an example. We'll use the following data:

`grandparent`

| id | name |
| --- | --- |
| 1 | Elizabeth |

`parent`

| id | name | `parent_id` |
| --- | --- | --- |
| 1 | Charles | 1 |
| 2 | Diana | 1 |

`child`

| id | name | father | mother |
| --- | --- | --- | --- |
| 1 | William | 1 | 2 |

To create these tables and their data, we run:

```
123456789101112131415161718192021222324252627282930313233343536373839create table grandparent (  id serial primary key,  name text);create table parent (  id serial primary key,  name text,  parent_id integer references grandparent (id)    on delete cascade);create table child (  id serial primary key,  name text,  father integer references parent (id)    on delete restrict);insert into grandparent  (id, name)values  (1, 'Elizabeth');insert into parent  (id, name, parent_id)values  (1, 'Charles', 1);insert into parent  (id, name, parent_id)values  (2, 'Diana', 1);-- We'll just link the father for nowinsert into child  (id, name, father)values  (1, 'William', 1);
```

### `RESTRICT`[#](#restrict)

`RESTRICT` will prevent a delete and raise an error:

```
123postgres=# delete from grandparent;ERROR: update or delete on table "parent" violates foreign key constraint "child_father_fkey" on table "child"DETAIL: Key (id)=(1) is still referenced from table "child".
```

Even though the foreign key constraint between parent and grandparent is `CASCADE`, the constraint between child and father is `RESTRICT`. Therefore an error is raised and no records are deleted.

### `NO ACTION`[#](#no-action)

Let's change the child-father relationship to `NO ACTION`:

```
123456alter table childdrop constraint child_father_fkey;alter table childadd constraint child_father_fkey foreign key (father) references parent (id)  on delete no action;
```

We see that `NO ACTION` will also prevent a delete and raise an error:

```
123postgres=# delete from grandparent;ERROR: update or delete on table "parent" violates foreign key constraint "child_father_fkey" on table "child"DETAIL: Key (id)=(1) is still referenced from table "child".
```

### `NO ACTION INITIALLY DEFERRED`[#](#no-action-initially-deferred)

We'll change the foreign key constraint between child and father to be `NO ACTION INITIALLY DEFERRED`:

```
123456alter table childdrop constraint child_father_fkey;alter table childadd constraint child_father_fkey foreign key (father) references parent (id)  on delete no action initially deferred;
```

Here you will see that `INITIALLY DEFFERED` seems to operate like `NO ACTION` or `RESTRICT`. When we run a delete, it seems to make no difference:

```
123postgres=# delete from grandparent;ERROR: update or delete on table "parent" violates foreign key constraint "child_father_fkey" on table "child"DETAIL: Key (id)=(1) is still referenced from table "child".
```

But, when we combine it with _other_ constraints, then any other constraints take precedence. For example, let's run the same but add a `mother` column that has a `CASCADE` delete:

```
1234567alter table childadd column mother integer references parent (id)  on delete cascade;update childset mother = 2where id = 1;
```

Then let's run a delete on the `grandparent` table:

```
123456789101112postgres=# delete from grandparent;DELETE 1postgres=# select * from parent; id | name | parent_id----+------+-----------(0 rows)postgres=# select * from child; id | name | father | mother----+------+--------+--------(0 rows)
```

The `mother` deletion took precedence over the `father`, and so William was deleted. After William was deleted, there was no reference to “Charles” and so he was free to be deleted, even though previously he wasn't (without `INITIALLY DEFERRED`).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/cascade-deletes.mdx)

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