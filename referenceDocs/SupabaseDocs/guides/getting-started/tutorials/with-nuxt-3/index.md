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

3.  Web app demos

5.  [Nuxt 3](https://supabase.com/docs/guides/getting-started/tutorials/with-nuxt-3)

# 

Build a User Management App with Nuxt 3

* * *

This tutorial demonstrates how to build a basic user management app. The app authenticates and identifies the user, stores their profile information in the database, and allows the user to log in, update their profile details, and upload a profile photo. The app uses:

-   [Supabase Database](https://supabase.com/docs/guides/database) - a Postgres database for storing your user data and [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) so data is protected and users can only access their own information.
-   [Supabase Auth](https://supabase.com/docs/guides/auth) - allow users to sign up and log in.
-   [Supabase Storage](https://supabase.com/docs/guides/storage) - users can upload a profile photo.

![Supabase User Management example](https://supabase.com/docs/img/user-management-demo.png)

If you get stuck while working through this guide, refer to the [full example on GitHub](https://github.com/supabase/supabase/tree/master/examples/user-management/nuxt3-user-management).

## Project setup[#](#project-setup)

Before we start building we're going to set up our Database and API. This is as simple as starting a new Project in Supabase and then creating a "schema" inside the database.

### Create a project[#](#create-a-project)

1.  [Create a new project](https://supabase.com/dashboard) in the Supabase Dashboard.
2.  Enter your project details.
3.  Wait for the new database to launch.

### Set up the database schema[#](#set-up-the-database-schema)

Now we are going to set up the database schema. We can use the "User Management Starter" quickstart in the SQL Editor, or you can just copy/paste the SQL from below and run it yourself.

DashboardSQL

1.  Go to the [SQL Editor](https://supabase.com/dashboard/project/_/sql) page in the Dashboard.
2.  Click **User Management Starter**.
3.  Click **Run**.

You can pull the database schema down to your local project by running the `db pull` command. Read the [local development docs](https://supabase.com/docs/guides/cli/local-development#link-your-project) for detailed instructions.

```
123supabase link --project-ref <project-id># You can get <project-id> from your project's dashboard URL: https://supabase.com/dashboard/project/<project-id>supabase db pull
```

### Get the API keys[#](#get-the-api-keys)

Now that you've created some database tables, you are ready to insert data using the auto-generated API. We just need to get the Project URL and `anon` key from the API settings.

1.  Go to the [API Settings](https://supabase.com/dashboard/project/_/settings/api) page in the Dashboard.
2.  Find your Project `URL`, `anon`, and `service_role` keys on this page.

## Building the app[#](#building-the-app)

Let's start building the Vue 3 app from scratch.

### Initialize a Nuxt 3 app[#](#initialize-a-nuxt-3-app)

We can use [`nuxi init`](https://nuxt.com/docs/getting-started/installation) to create an app called `nuxt-user-management`:

```
123npx nuxi init nuxt-user-managementcd nuxt-user-management
```

Then let's install the only additional dependency: [Nuxt Supabase](https://supabase.nuxtjs.org/). We only need to import Nuxt Supabase as a dev dependency.

```
1npm install @nuxtjs/supabase --save-dev
```

And finally we want to save the environment variables in a `.env`. All we need are the API URL and the `anon` key that you copied [earlier](#get-the-api-keys).

.env

```
12SUPABASE_URL="YOUR_SUPABASE_URL"SUPABASE_KEY="YOUR_SUPABASE_ANON_KEY"
```

These variables will be exposed on the browser, and that's completely fine since we have [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) enabled on our Database. Amazing thing about [Nuxt Supabase](https://supabase.nuxtjs.org/) is that setting environment variables is all we need to do in order to start using Supabase. No need to initialize Supabase. The library will take care of it automatically.

### App styling (optional)[#](#app-styling-optional)

An optional step is to update the CSS file `assets/main.css` to make the app look nice. You can find the full contents of this file [here](https://github.com/supabase-community/nuxt3-quickstarter/blob/main/assets/main.css).

nuxt.config.ts

```
1234567import { defineNuxtConfig } from 'nuxt'// https://v3.nuxtjs.org/api/configuration/nuxt.configexport default defineNuxtConfig({  modules: ['@nuxtjs/supabase'],  css: ['@/assets/main.css'],})
```

### Set up Auth component[#](#set-up-auth-component)

Let's set up a Vue component to manage logins and sign ups. We'll use Magic Links, so users can sign in with their email without using passwords.

/components/Auth.vue

```
123456789101112131415161718192021222324252627282930313233343536373839<script setup>const supabase = useSupabaseClient()const loading = ref(false)const email = ref('')const handleLogin = async () => {  try {    loading.value = true    const { error } = await supabase.auth.signInWithOtp({ email: email.value })    if (error) throw error    alert('Check your email for the login link!')  } catch (error) {    alert(error.error_description || error.message)  } finally {    loading.value = false  }}</script><template>  <form class="row flex-center flex" @submit.prevent="handleLogin">    <div class="col-6 form-widget">      <h1 class="header">Supabase + Nuxt 3</h1>      <p class="description">Sign in via magic link with your email below</p>      <div>        <input class="inputField" type="email" placeholder="Your email" v-model="email" />      </div>      <div>        <input          type="submit"          class="button block"          :value="loading ? 'Loading' : 'Send magic link'"          :disabled="loading"        />      </div>    </div>  </form></template>
```

### User state[#](#user-state)

To access the user information, use the composable [`useSupabaseUser`](https://supabase.nuxtjs.org/usage/composables/usesupabaseuser) provided by the Supabase Nuxt module.

### Account component[#](#account-component)

After a user is signed in we can allow them to edit their profile details and manage their account. Let's create a new component for that called `Account.vue`.

components/Account.vue

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283848586878889909192<script setup>const supabase = useSupabaseClient()const loading = ref(true)const username = ref('')const website = ref('')const avatar_path = ref('')loading.value = trueconst user = useSupabaseUser()const { data } = await supabase  .from('profiles')  .select(`username, website, avatar_url`)  .eq('id', user.value.id)  .single()if (data) {  username.value = data.username  website.value = data.website  avatar_path.value = data.avatar_url}loading.value = falseasync function updateProfile() {  try {    loading.value = true    const user = useSupabaseUser()    const updates = {      id: user.value.id,      username: username.value,      website: website.value,      avatar_url: avatar_path.value,      updated_at: new Date(),    }    const { error } = await supabase.from('profiles').upsert(updates, {      returning: 'minimal', // Don't return the value after inserting    })    if (error) throw error  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}async function signOut() {  try {    loading.value = true    const { error } = await supabase.auth.signOut()    if (error) throw error    user.value = null  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}</script><template>  <form class="form-widget" @submit.prevent="updateProfile">    <div>      <label for="email">Email</label>      <input id="email" type="text" :value="user.email" disabled />    </div>    <div>      <label for="username">Username</label>      <input id="username" type="text" v-model="username" />    </div>    <div>      <label for="website">Website</label>      <input id="website" type="url" v-model="website" />    </div>    <div>      <input        type="submit"        class="button primary block"        :value="loading ? 'Loading ...' : 'Update'"        :disabled="loading"      />    </div>    <div>      <button class="button block" @click="signOut" :disabled="loading">Sign Out</button>    </div>  </form></template>
```

### Launch![#](#launch)

Now that we have all the components in place, let's update `app.vue`:

app.vue

```
12345678910<script setup>const user = useSupabaseUser()</script><template>  <div class="container" style="padding: 50px 0 100px 0">    <Account v-if="user" />    <Auth v-else />  </div></template>
```

Once that's done, run this in a terminal window:

```
1npm run dev
```

And then open the browser to [localhost:3000](http://localhost:3000) and you should see the completed app.

![Supabase Nuxt 3](https://supabase.com/docs/img/supabase-vue-3-demo.png)

## Bonus: Profile photos[#](#bonus-profile-photos)

Every Supabase project is configured with [Storage](https://supabase.com/docs/guides/storage) for managing large files like photos and videos.

### Create an upload widget[#](#create-an-upload-widget)

Let's create an avatar for the user so that they can upload a profile photo. We can start by creating a new component:

components/Avatar.vue

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384<script setup>const props = defineProps(['path'])const { path } = toRefs(props)const emit = defineEmits(['update:path', 'upload'])const supabase = useSupabaseClient()const uploading = ref(false)const src = ref('')const files = ref()const downloadImage = async () => {  try {    const { data, error } = await supabase.storage.from('avatars').download(path.value)    if (error) throw error    src.value = URL.createObjectURL(data)  } catch (error) {    console.error('Error downloading image: ', error.message)  }}const uploadAvatar = async (evt) => {  files.value = evt.target.files  try {    uploading.value = true    if (!files.value || files.value.length === 0) {      throw new Error('You must select an image to upload.')    }    const file = files.value[0]    const fileExt = file.name.split('.').pop()    const fileName = `${Math.random()}.${fileExt}`    const filePath = `${fileName}`    const { error: uploadError } = await supabase.storage.from('avatars').upload(filePath, file)    if (uploadError) throw uploadError    emit('update:path', filePath)    emit('upload')  } catch (error) {    alert(error.message)  } finally {    uploading.value = false  }}downloadImage()watch(path, () => {  if (path.value) {    downloadImage()  }})</script><template>  <div>    <img      v-if="src"      :src="src"      alt="Avatar"      class="avatar image"      style="width: 10em; height: 10em;"    />    <div v-else class="avatar no-image" :style="{ height: size, width: size }" />    <div style="width: 10em; position: relative;">      <label class="button primary block" for="single">        {{ uploading ? 'Uploading ...' : 'Upload' }}      </label>      <input        style="position: absolute; visibility: hidden;"        type="file"        id="single"        accept="image/*"        @change="uploadAvatar"        :disabled="uploading"      />    </div>  </div></template>
```

### Add the new widget[#](#add-the-new-widget)

And then we can add the widget to the Account page:

components/Account.vue

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293<script setup>const supabase = useSupabaseClient()const loading = ref(true)const username = ref('')const website = ref('')const avatar_path = ref('')loading.value = trueconst user = useSupabaseUser()const { data } = await supabase  .from('profiles')  .select(`username, website, avatar_url`)  .eq('id', user.value.id)  .single()if (data) {  username.value = data.username  website.value = data.website  avatar_path.value = data.avatar_url}loading.value = falseasync function updateProfile() {  try {    loading.value = true    const user = useSupabaseUser()    const updates = {      id: user.value.id,      username: username.value,      website: website.value,      avatar_url: avatar_path.value,      updated_at: new Date(),    }    const { error } = await supabase.from('profiles').upsert(updates, {      returning: 'minimal', // Don't return the value after inserting    })    if (error) throw error  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}async function signOut() {  try {    loading.value = true    const { error } = await supabase.auth.signOut()    if (error) throw error  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}</script><template>  <form class="form-widget" @submit.prevent="updateProfile">    <Avatar v-model:path="avatar_path" @upload="updateProfile" />    <div>      <label for="email">Email</label>      <input id="email" type="text" :value="user.email" disabled />    </div>    <div>      <label for="username">Name</label>      <input id="username" type="text" v-model="username" />    </div>    <div>      <label for="website">Website</label>      <input id="website" type="url" v-model="website" />    </div>    <div>      <input        type="submit"        class="button primary block"        :value="loading ? 'Loading ...' : 'Update'"        :disabled="loading"      />    </div>    <div>      <button class="button block" @click="signOut" :disabled="loading">Sign Out</button>    </div>  </form></template>
```

That is it! You should now be able to upload a profile photo to Supabase Storage and you have a fully functional application.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/tutorials/with-nuxt-3.mdx)

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