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

5.  [Managing database triggers](https://supabase.com/docs/guides/database/postgres/triggers)

# 

Postgres Triggers

## 

Automatically execute SQL on table events.

* * *

In Postgres, a trigger executes a set of actions automatically on table events such as INSERTs, UPDATEs, DELETEs, or TRUNCATE operations.

## Creating a trigger[#](#creating-a-trigger)

Creating triggers involve 2 parts:

1.  A [Function](https://supabase.com/docs/guides/database/functions) which will be executed (called the Trigger Function)
2.  The actual Trigger object, with parameters around when the trigger should be run.

An example of a trigger is:

```
1234create trigger "trigger_name"after insert on "table_name"for each rowexecute function trigger_function();
```

## Trigger functions[#](#trigger-functions)

A trigger function is a user-defined [Function](https://supabase.com/docs/guides/database/functions) that Postgres executes when the trigger is fired.

### Example trigger function[#](#example-trigger-function)

Here is an example that updates `salary_log` whenever an employee's salary is updated:

```
12345678910111213141516-- Example: Update salary_log when salary is updatedcreate function update_salary_log()returns triggerlanguage plpgsqlas $$begin  insert into salary_log(employee_id, old_salary, new_salary)  values (new.id, old.salary, new.salary);  return new;end;$$;create trigger salary_update_triggerafter update on employeesfor each rowexecute function update_salary_log();
```

### Trigger variables[#](#trigger-variables)

Trigger functions have access to several special variables that provide information about the context of the trigger event and the data being modified. In the example above you can see the values inserted into the salary log are `old.salary` and `new.salary` - in this case `old` specifies the previous values and `new` specifies the updated values.

Here are some of the key variables and options available within trigger functions:

-   `TG_NAME`: The name of the trigger being fired.
-   `TG_WHEN`: The timing of the trigger event (`BEFORE` or `AFTER`).
-   `TG_OP`: The operation that triggered the event (`INSERT`, `UPDATE`, `DELETE`, or `TRUNCATE`).
-   `OLD`: A record variable holding the old row's data in `UPDATE` and `DELETE` triggers.
-   `NEW`: A record variable holding the new row's data in `UPDATE` and `INSERT` triggers.
-   `TG_LEVEL`: The trigger level (`ROW` or `STATEMENT`), indicating whether the trigger is row-level or statement-level.
-   `TG_RELID`: The object ID of the table on which the trigger is being fired.
-   `TG_TABLE_NAME`: The name of the table on which the trigger is being fired.
-   `TG_TABLE_SCHEMA`: The schema of the table on which the trigger is being fired.
-   `TG_ARGV`: An array of string arguments provided when creating the trigger.
-   `TG_NARGS`: The number of arguments in the `TG_ARGV` array.

## Types of triggers[#](#types-of-triggers)

There are two types of trigger, `BEFORE` and `AFTER`:

### Trigger before changes are made[#](#trigger-before-changes-are-made)

Executes before the triggering event.

```
1234create trigger before_insert_triggerbefore insert on ordersfor each rowexecute function before_insert_function();
```

### Trigger after changes are made[#](#trigger-after-changes-are-made)

Executes after the triggering event.

```
1234create trigger after_delete_triggerafter delete on customersfor each rowexecute function after_delete_function();
```

## Execution frequency[#](#execution-frequency)

There are two options available for executing triggers:

-   `for each row`: specifies that the trigger function should be executed once for each affected row.
-   `for each statement`: the trigger is executed once for the entire operation (for example, once on insert). This can be more efficient than `for each row` when dealing with multiple rows affected by a single SQL statement, as they allow you to perform calculations or updates on groups of rows at once.

## Dropping a trigger[#](#dropping-a-trigger)

You can delete a trigger using the `drop trigger` command:

```
1drop trigger "trigger_name" on "table_name";
```

## Resources[#](#resources)

-   Official Postgres Docs: [Triggers](https://www.postgresql.org/docs/current/triggers.html)
-   Official Postgres Docs: [Overview of Trigger Behavior](https://www.postgresql.org/docs/current/trigger-definition.html)
-   Official Postgres Docs: [CREATE TRIGGER](https://www.postgresql.org/docs/current/sql-createtrigger.html)

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/postgres/triggers.mdx)

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