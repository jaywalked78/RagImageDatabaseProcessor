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

# Grafana not displaying data

Last edited: 2/4/2025

* * *

This guide is for identifying configuration mistakes in [self-hosted Supabase Grafana installations](https://supabase.com/docs/guides/monitoring-troubleshooting/metrics#deploying-supabase-grafana)

## Step 1: Ping your Grafana endpoint[#](#step-1-ping-your-grafana-endpoint)

Use the below cURL command to make sure your metrics endpoint returns data:

```
1curl https://<YOUR_PROJECT_REF>.supabase.co/customer/v1/privileged/metrics --user 'service_role:<SERVICE_ROLE_KEY>'
```

## Step 2: Set your Grafana Dashboard to auto-refresh in the top right corner[#](#step-2-set-your-grafana-dashboard-to-auto-refresh-in-the-top-right-corner)

![388343266-ed4b8f38-e0cd-474e-bc1c-1ac6ae68e1aa](https://supabase.com/docs/img/troubleshooting/47998bed-0b77-433a-bfed-63222beb2aee.png)

## Step 3: Make sure your docker container has the default configurations[#](#step-3-make-sure-your-docker-container-has-the-default-configurations)

Run the following command in the terminal:

```
1docker ps -f name=supabase-grafana
```

The output should look something like this:

![image](https://supabase.com/docs/img/troubleshooting/6c284180-0ffd-432d-b86b-e9fbcfe23868.png)

Here it is in an easier to read format

```
1234567- CONTAINER ID: < container id >- IMAGE: supabase-grafana-supabase-grafana- COMMAND: /entrypoint.sh- CREATED: < time >- STATUS: Up < unit of time > ago- PORTS: 3000/tcp, 0.0.0.0:8000 → 8080/tcp- NAMES: supabase-grafana-supabase-grafana-1
```

## Step 4: Enter the container[#](#step-4-enter-the-container)

Try running the following terminal command:

```
1docker exec -it <container id> bash
```

## Step 5: Check the environment variables for errors[#](#step-5-check-the-environment-variables-for-errors)

Run the following in the docker container:

```
1printenv | egrep 'GRAFANA_PASSWORD|SUPABASE_PROJECT_REF|SUPABASE_SERVICE_ROLE_KEY'
```

Ensure the values are correct by comparing them with those in the Dashboard. Users have previously encountered issues by accidentally omitting the last character of their strings, so a thorough check is essential.

## Step 6: Go to the root folder and check permissions on the `entrypoint.sh` file[#](#step-6-go-to-the-root-folder-and-check-permissions-on-the-entrypointsh-file)

Run the following terminal commands:

```
12cd /ls -l | grep entrypoint.sh
```

`entrypoint.sh` should have the following permissions:

```
1-rwxr-xr-x
```

If off, update the values

```
1chmod +x entrypoint.sh
```

## Metadata

* * *

### Products

[Database](https://supabase.com/docs/guides/troubleshooting?products=database)

* * *

### Tags

[grafana](https://supabase.com/docs/guides/troubleshooting?tags=grafana)[docker](https://supabase.com/docs/guides/troubleshooting?tags=docker)[metrics](https://supabase.com/docs/guides/troubleshooting?tags=metrics)[configuration](https://supabase.com/docs/guides/troubleshooting?tags=configuration)

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