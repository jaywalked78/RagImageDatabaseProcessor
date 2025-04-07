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

3.  Guides

5.  [Deploying with CI / CD pipelines](https://supabase.com/docs/guides/functions/cicd-workflow)

# 

Deploying with CI / CD pipelines

## 

Use GitHub Actions, Bitbucket, and GitLab CI to deploy your Edge Functions.

* * *

You can use popular CI / CD tools like GitHub Actions, Bitbucket, and GitLab CI to automate Edge Function deployments.

## GitHub Actions[#](#github-actions)

You can use the official [`setup-cli` GitHub Action](https://github.com/marketplace/actions/supabase-cli-action) to run Supabase CLI commands in your GitHub Actions.

The following GitHub Action deploys all Edge Functions any time code is merged into the `main` branch:

```
123456789101112131415161718192021222324name: Deploy Functionon:  push:    branches:      - main  workflow_dispatch:jobs:  deploy:    runs-on: ubuntu-latest    env:      SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}      PROJECT_ID: your-project-id    steps:      - uses: actions/checkout@v4      - uses: supabase/setup-cli@v1        with:          version: latest      - run: supabase functions deploy --project-ref $PROJECT_ID
```

## GitLab CI[#](#gitlab-ci)

Here is the sample pipeline configuration to deploy via GitLab CI.

```
1234567891011121314151617181920212223242526272829image: node:20# List of stages for jobs, and their order of executionstages:  - setup  - deploy# This job runs in the setup stage, which runs first.setup-npm:  stage: setup  script:    - npm i supabase  cache:    paths:      - node_modules/  artifacts:    paths:      - node_modules/# This job runs in the deploy stage, which only starts when the job in the build stage completes successfully.deploy-function:  stage: deploy  script:    - npx supabase init    - npx supabase functions deploy --debug  services:    - docker:dind  variables:    DOCKER_HOST: tcp://docker:2375
```

## Bitbucket Pipelines[#](#bitbucket-pipelines)

Here is the sample pipeline configuration to deploy via Bitbucket.

```
123456789101112131415161718image: node:20pipelines:  default:    - step:        name: Setup        caches:          - node        script:          - npm i supabase    - parallel:        - step:            name: Functions Deploy            script:              - npx supabase init              - npx supabase functions deploy --debug            services:              - docker
```

## Declarative configuration[#](#declarative-configuration)

Individual function configuration like [JWT verification](https://supabase.com/docs/guides/cli/config#functions.function_name.verify_jwt) and [import map location](https://supabase.com/docs/guides/cli/config#functions.function_name.import_map) can be set via the `config.toml` file.

```
12[functions.hello-world]verify_jwt = false
```

## Resources[#](#resources)

-   See the [example on GitHub](https://github.com/supabase/supabase/blob/master/examples/edge-functions/.github/workflows/deploy.yaml).

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/cicd-workflow.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2F6OMVWiiycLs%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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