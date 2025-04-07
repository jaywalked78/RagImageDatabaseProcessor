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

Edge Functions

1.  [Edge Functions](https://supabase.com/docs/guides/functions)

3.  Getting started

5.  [Quickstart](https://supabase.com/docs/guides/functions/quickstart)

# 

Developing Edge Functions with Supabase

## 

Get started with Edge Functions on the Supabase dashboard.

* * *

In this guide we'll cover how to create a basic Edge Function on the Supabase dashboard, and access it using the Supabase CLI.

## Deploy from Dashboard[#](#deploy-from-dashboard)

Go to your project > Edge Functions > Deploy a new function > Via Editor

This will scaffold a new function for you. You can choose from Templates some of the pre-defined functions for common use cases.

Modify the function as needed, name it, and click `Deploy function`

Your function is now active. Navigate to the function's details page, and click on the test button.

You can test your function by providing the expected HTTP method, headers, query parameters, and request body. You can also change the authorization token passed (e.g., anon key or a user key).

## Access deployed functions via Supabase CLI[#](#access-deployed-functions-via-supabase-cli)

##### CLI not installed?

Check out the [CLI Docs](https://supabase.com/docs/guides/cli) to learn how to install the Supabase CLI on your local machine.

Now that your function is deployed, you can access it from your local development environment. Here's how:

1.  **Link your project** to your local environment.
    
    You can find your project reference ID in the URL of your Supabase dashboard or in the project settings.
    
    ```
    1supabase link --project-ref your-project-ref
    ```
    
2.  **List all Functions** in the linked Supabase project.
    
    ```
    1supabase functions list
    ```
    
3.  **Access the specific function** you want to work on.
    
    ```
    1supabase functions download function-name
    ```
    
4.  **Make local edits** to the function code as needed.
    
5.  **Run your function locally** before redeploying.
    
    ```
    1supabase functions serve function-name
    ```
    
6.  **Redeploy** when you're ready with your changes.
    
    ```
    1supabase functions deploy function-name
    ```
    

## Deploy via Assistant[#](#deploy-via-assistant)

You can also leverage the Supabase Assistant to help you write and deploy edge functions.

Go to your project > Edge Functions > Click on the Assistant icon to Create with Supabase Assistant

This brings up an assistant window with a pre-filled prompt for generating edge functions. Write up your Edge Function requirement, and let Supabase Assistant do the rest.

Click Deploy and the Assistant will automatically deploy your function.

This function requires an OpenAI API key. You can add the key in your Edge Functions secrets page, or ask Assistant for help.

1.  Navigate to your Edge Functions > Secrets page.
2.  Look for the option to add environment variables.
3.  Add a new environment variable with the key `OPENAI_API_KEY` and set its value to your actual OpenAI API key.

Once you've set this environment variable, your edge functions will be able to access the OPENAI\_API\_KEY securely without hardcoding it into the function code. This is a best practice for keeping sensitive information safe.

With your variable set, you can test by sending a request via the dashboard. Navigate to the function's details page, and click on the test button. Then provide a Request Body your function expects.

## Editing functions from the Dashboard[#](#editing-functions-from-the-dashboard)

##### Be careful: there is currently no version control for edits

The Dashboard's Edge Function editor currently does not support versioning or rollbacks. We recommend using it only for quick testing and prototypes. When you’re ready to go to production, store Edge Functions code in a source code repository (e.g., git) and deploy it using one of the [CI integrations](https://supabase.com/docs/guides/functions/cicd-workflow).

1.  From the functions page, click on the function you want to edit. From the function page, click on the Code tab.
    
2.  This opens up a code editor in the dashboard where you can see your deployed function's code.
    
3.  Modify the code as needed, then click Deploy updates. This will overwrite the existing deployment with the newly edited function code.
    

## Next steps[#](#next-steps)

Check out the [Local development](https://supabase.com/docs/guides/functions/local-quickstart) guide for more details on working with Edge Functions.

Read on for some [common development tips](https://supabase.com/docs/guides/functions/development-tips).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/quickstart.mdx)

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