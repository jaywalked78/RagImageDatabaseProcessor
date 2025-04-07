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

5.  [Vue 3](https://supabase.com/docs/guides/getting-started/tutorials/with-vue-3)

# 

Build a User Management App with Vue 3

* * *

This tutorial demonstrates how to build a basic user management app. The app authenticates and identifies the user, stores their profile information in the database, and allows the user to log in, update their profile details, and upload a profile photo. The app uses:

-   [Supabase Database](https://supabase.com/docs/guides/database) - a Postgres database for storing your user data and [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) so data is protected and users can only access their own information.
-   [Supabase Auth](https://supabase.com/docs/guides/auth) - allow users to sign up and log in.
-   [Supabase Storage](https://supabase.com/docs/guides/storage) - users can upload a profile photo.

![Supabase User Management example](https://supabase.com/docs/img/user-management-demo.png)

If you get stuck while working through this guide, refer to the [full example on GitHub](https://github.com/supabase/supabase/tree/master/examples/user-management/vue3-user-management).

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

### Initialize a Vue 3 app[#](#initialize-a-vue-3-app)

We can quickly use [Vite with Vue 3 Template](https://vitejs.dev/guide/#scaffolding-your-first-vite-project) to initialize an app called `supabase-vue-3`:

```
1234567# npm 6.xnpm create vite@latest supabase-vue-3 --template vue# npm 7+, extra double-dash is needed:npm create vite@latest supabase-vue-3 -- --template vuecd supabase-vue-3
```

Then let's install the only additional dependency: [supabase-js](https://github.com/supabase/supabase-js)

```
1npm install @supabase/supabase-js
```

And finally we want to save the environment variables in a `.env`. All we need are the API URL and the `anon` key that you copied [earlier](#get-the-api-keys).

.env

```
12VITE_SUPABASE_URL=YOUR_SUPABASE_URLVITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

With the API credentials in place, create an `src/supabase.js` helper file to initialize the Supabase client. These variables are exposed on the browser, and that's completely fine since we have [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) enabled on our Database.

src/supabase.js

```
123456import { createClient } from '@supabase/supabase-js'const supabaseUrl = import.meta.env.VITE_SUPABASE_URLconst supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEYexport const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

Optionally, update [src/style.css](https://raw.githubusercontent.com/supabase/supabase/master/examples/user-management/vue3-user-management/src/style.css) to style the app.

### Set up a login component[#](#set-up-a-login-component)

Set up an `src/components/Auth.vue` component to manage logins and sign ups. We'll use Magic Links, so users can sign in with their email without using passwords.

/src/components/Auth.vue

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344<script setup>import { ref } from 'vue'import { supabase } from '../supabase'const loading = ref(false)const email = ref('')const handleLogin = async () => {  try {    loading.value = true    const { error } = await supabase.auth.signInWithOtp({      email: email.value,    })    if (error) throw error    alert('Check your email for the login link!')  } catch (error) {    if (error instanceof Error) {      alert(error.message)    }  } finally {    loading.value = false  }}</script><template>  <form class="row flex-center flex" @submit.prevent="handleLogin">    <div class="col-6 form-widget">      <h1 class="header">Supabase + Vue 3</h1>      <p class="description">Sign in via magic link with your email below</p>      <div>        <input class="inputField" required type="email" placeholder="Your email" v-model="email" />      </div>      <div>        <input          type="submit"          class="button block"          :value="loading ? 'Loading' : 'Send magic link'"          :disabled="loading"        />      </div>    </div>  </form></template>
```

### Account page[#](#account-page)

After a user is signed in we can allow them to edit their profile details and manage their account. Create a new `src/components/Account.vue` component to handle this.

src/components/Account.vue

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106<script setup>import { supabase } from '../supabase'import { onMounted, ref, toRefs } from 'vue'const props = defineProps(['session'])const { session } = toRefs(props)const loading = ref(true)const username = ref('')const website = ref('')const avatar_url = ref('')onMounted(() => {  getProfile()})async function getProfile() {  try {    loading.value = true    const { user } = session.value    const { data, error, status } = await supabase      .from('profiles')      .select(`username, website, avatar_url`)      .eq('id', user.id)      .single()    if (error && status !== 406) throw error    if (data) {      username.value = data.username      website.value = data.website      avatar_url.value = data.avatar_url    }  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}async function updateProfile() {  try {    loading.value = true    const { user } = session.value    const updates = {      id: user.id,      username: username.value,      website: website.value,      avatar_url: avatar_url.value,      updated_at: new Date(),    }    const { error } = await supabase.from('profiles').upsert(updates)    if (error) throw error  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}async function signOut() {  try {    loading.value = true    const { error } = await supabase.auth.signOut()    if (error) throw error  } catch (error) {    alert(error.message)  } finally {    loading.value = false  }}</script><template>  <form class="form-widget" @submit.prevent="updateProfile">    <div>      <label for="email">Email</label>      <input id="email" type="text" :value="session.user.email" disabled />    </div>    <div>      <label for="username">Name</label>      <input id="username" type="text" v-model="username" />    </div>    <div>      <label for="website">Website</label>      <input id="website" type="url" v-model="website" />    </div>    <div>      <input        type="submit"        class="button primary block"        :value="loading ? 'Loading ...' : 'Update'"        :disabled="loading"      />    </div>    <div>      <button class="button block" @click="signOut" :disabled="loading">Sign Out</button>    </div>  </form></template>
```

### Launch![#](#launch)

Now that we have all the components in place, let's update `App.vue`:

src/App.vue

```
12345678910111213141516171819202122232425<script setup>import { onMounted, ref } from 'vue'import Account from './components/Account.vue'import Auth from './components/Auth.vue'import { supabase } from './supabase'const session = ref()onMounted(() => {  supabase.auth.getSession().then(({ data }) => {    session.value = data.session  })  supabase.auth.onAuthStateChange((_, _session) => {    session.value = _session  })})</script><template>  <div class="container" style="padding: 50px 0 100px 0">    <Account v-if="session" :session="session" />    <Auth v-else />  </div></template>
```

Once that's done, run this in a terminal window:

```
1npm run dev
```

And then open the browser to [localhost:5173](http://localhost:5173) and you should see the completed app.

![Supabase Vue 3](https://supabase.com/docs/img/supabase-vue-3-demo.png)

## Bonus: Profile photos[#](#bonus-profile-photos)

Every Supabase project is configured with [Storage](https://supabase.com/docs/guides/storage) for managing large files like photos and videos.

### Create an upload widget[#](#create-an-upload-widget)

Create a new `src/components/Avatar.vue` component that allows users to upload profile photos:

src/components/Avatar.vue

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677<script setup>import { ref, toRefs, watchEffect } from 'vue'import { supabase } from '../supabase'const prop = defineProps(['path', 'size'])const { path, size } = toRefs(prop)const emit = defineEmits(['upload', 'update:path'])const uploading = ref(false)const src = ref('')const files = ref()const downloadImage = async () => {  try {    const { data, error } = await supabase.storage.from('avatars').download(path.value)    if (error) throw error    src.value = URL.createObjectURL(data)  } catch (error) {    console.error('Error downloading image: ', error.message)  }}const uploadAvatar = async (evt) => {  files.value = evt.target.files  try {    uploading.value = true    if (!files.value || files.value.length === 0) {      throw new Error('You must select an image to upload.')    }    const file = files.value[0]    const fileExt = file.name.split('.').pop()    const filePath = `${Math.random()}.${fileExt}`    const { error: uploadError } = await supabase.storage.from('avatars').upload(filePath, file)    if (uploadError) throw uploadError    emit('update:path', filePath)    emit('upload')  } catch (error) {    alert(error.message)  } finally {    uploading.value = false  }}watchEffect(() => {  if (path.value) downloadImage()})</script><template>  <div>    <img      v-if="src"      :src="src"      alt="Avatar"      class="avatar image"      :style="{ height: size + 'em', width: size + 'em' }"    />    <div v-else class="avatar no-image" :style="{ height: size + 'em', width: size + 'em' }" />    <div :style="{ width: size + 'em' }">      <label class="button primary block" for="single">        {{ uploading ? 'Uploading ...' : 'Upload' }}      </label>      <input        style="visibility: hidden; position: absolute"        type="file"        id="single"        accept="image/*"        @change="uploadAvatar"        :disabled="uploading"      />    </div>  </div></template>
```

### Add the new widget[#](#add-the-new-widget)

And then we can add the widget to the Account page in `src/components/Account.vue`:

src/components/Account.vue

```
12345678910111213141516<script>// Import the new componentimport Avatar from './Avatar.vue'//...const avatar_url = ref('')//...</script><template>  <form class="form-widget" @submit.prevent="updateProfile">    <!-- Add to body -->    <Avatar v-model:path="avatar_url" @upload="updateProfile" size="10" />    <!-- Other form elements -->  </form></template>
```

At this stage you have a fully functional application!

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/tutorials/with-vue-3.mdx)

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