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

3.  Mobile tutorials

5.  [Expo React Native](https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native)

# 

Build a User Management App with Expo React Native

* * *

This tutorial demonstrates how to build a basic user management app. The app authenticates and identifies the user, stores their profile information in the database, and allows the user to log in, update their profile details, and upload a profile photo. The app uses:

-   [Supabase Database](https://supabase.com/docs/guides/database) - a Postgres database for storing your user data and [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) so data is protected and users can only access their own information.
-   [Supabase Auth](https://supabase.com/docs/guides/auth) - allow users to sign up and log in.
-   [Supabase Storage](https://supabase.com/docs/guides/storage) - users can upload a profile photo.

![Supabase User Management example](https://supabase.com/docs/img/supabase-flutter-demo.png)

If you get stuck while working through this guide, refer to the [full example on GitHub](https://github.com/supabase/supabase/tree/master/examples/user-management/expo-user-management).

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

Let's start building the React Native app from scratch.

### Initialize a React Native app[#](#initialize-a-react-native-app)

We can use [`expo`](https://docs.expo.dev/get-started/create-a-new-app/) to initialize an app called `expo-user-management`:

```
123npx create-expo-app -t expo-template-blank-typescript expo-user-managementcd expo-user-management
```

Then let's install the additional dependencies: [supabase-js](https://github.com/supabase/supabase-js)

```
1npx expo install @supabase/supabase-js @react-native-async-storage/async-storage @rneui/themed
```

Now let's create a helper file to initialize the Supabase client. We need the API URL and the `anon` key that you copied [earlier](#get-the-api-keys). These variables are safe to expose in your Expo app since Supabase has [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security) enabled on your Database.

AsyncStorageSecureStore

lib/supabase.ts

```
1234567891011121314import AsyncStorage from '@react-native-async-storage/async-storage'import { createClient } from '@supabase/supabase-js'const supabaseUrl = YOUR_REACT_NATIVE_SUPABASE_URLconst supabaseAnonKey = YOUR_REACT_NATIVE_SUPABASE_ANON_KEYexport const supabase = createClient(supabaseUrl, supabaseAnonKey, {  auth: {    storage: AsyncStorage,    autoRefreshToken: true,    persistSession: true,    detectSessionInUrl: false,  },})
```

### Set up a login component[#](#set-up-a-login-component)

Let's set up a React Native component to manage logins and sign ups. Users would be able to sign in with their email and password.

components/Auth.tsx

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283848586878889909192939495import React, { useState } from 'react'import { Alert, StyleSheet, View, AppState } from 'react-native'import { supabase } from '../lib/supabase'import { Button, Input } from '@rneui/themed'// Tells Supabase Auth to continuously refresh the session automatically if// the app is in the foreground. When this is added, you will continue to receive// `onAuthStateChange` events with the `TOKEN_REFRESHED` or `SIGNED_OUT` event// if the user's session is terminated. This should only be registered once.AppState.addEventListener('change', (state) => {  if (state === 'active') {    supabase.auth.startAutoRefresh()  } else {    supabase.auth.stopAutoRefresh()  }})export default function Auth() {  const [email, setEmail] = useState('')  const [password, setPassword] = useState('')  const [loading, setLoading] = useState(false)  async function signInWithEmail() {    setLoading(true)    const { error } = await supabase.auth.signInWithPassword({      email: email,      password: password,    })    if (error) Alert.alert(error.message)    setLoading(false)  }  async function signUpWithEmail() {    setLoading(true)    const {      data: { session },      error,    } = await supabase.auth.signUp({      email: email,      password: password,    })    if (error) Alert.alert(error.message)    if (!session) Alert.alert('Please check your inbox for email verification!')    setLoading(false)  }  return (    <View style={styles.container}>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Input          label="Email"          leftIcon={{ type: 'font-awesome', name: 'envelope' }}          onChangeText={(text) => setEmail(text)}          value={email}          placeholder="email@address.com"          autoCapitalize={'none'}        />      </View>      <View style={styles.verticallySpaced}>        <Input          label="Password"          leftIcon={{ type: 'font-awesome', name: 'lock' }}          onChangeText={(text) => setPassword(text)}          value={password}          secureTextEntry={true}          placeholder="Password"          autoCapitalize={'none'}        />      </View>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Button title="Sign in" disabled={loading} onPress={() => signInWithEmail()} />      </View>      <View style={styles.verticallySpaced}>        <Button title="Sign up" disabled={loading} onPress={() => signUpWithEmail()} />      </View>    </View>  )}const styles = StyleSheet.create({  container: {    marginTop: 40,    padding: 12,  },  verticallySpaced: {    paddingTop: 4,    paddingBottom: 4,    alignSelf: 'stretch',  },  mt20: {    marginTop: 20,  },})
```

By default Supabase Auth requires email verification before a session is created for the users. To support email verification you need to [implement deep link handling](https://supabase.com/docs/guides/auth/native-mobile-deep-linking?platform=react-native)!

While testing, you can disable email confirmation in your [project's email auth provider settings](https://supabase.com/dashboard/project/_/auth/providers).

### Account page[#](#account-page)

After a user is signed in we can allow them to edit their profile details and manage their account.

Let's create a new component for that called `Account.tsx`.

components/Account.tsx

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120import { useState, useEffect } from 'react'import { supabase } from '../lib/supabase'import { StyleSheet, View, Alert } from 'react-native'import { Button, Input } from '@rneui/themed'import { Session } from '@supabase/supabase-js'export default function Account({ session }: { session: Session }) {  const [loading, setLoading] = useState(true)  const [username, setUsername] = useState('')  const [website, setWebsite] = useState('')  const [avatarUrl, setAvatarUrl] = useState('')  useEffect(() => {    if (session) getProfile()  }, [session])  async function getProfile() {    try {      setLoading(true)      if (!session?.user) throw new Error('No user on the session!')      const { data, error, status } = await supabase        .from('profiles')        .select(`username, website, avatar_url`)        .eq('id', session?.user.id)        .single()      if (error && status !== 406) {        throw error      }      if (data) {        setUsername(data.username)        setWebsite(data.website)        setAvatarUrl(data.avatar_url)      }    } catch (error) {      if (error instanceof Error) {        Alert.alert(error.message)      }    } finally {      setLoading(false)    }  }  async function updateProfile({    username,    website,    avatar_url,  }: {    username: string    website: string    avatar_url: string  }) {    try {      setLoading(true)      if (!session?.user) throw new Error('No user on the session!')      const updates = {        id: session?.user.id,        username,        website,        avatar_url,        updated_at: new Date(),      }      const { error } = await supabase.from('profiles').upsert(updates)      if (error) {        throw error      }    } catch (error) {      if (error instanceof Error) {        Alert.alert(error.message)      }    } finally {      setLoading(false)    }  }  return (    <View style={styles.container}>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Input label="Email" value={session?.user?.email} disabled />      </View>      <View style={styles.verticallySpaced}>        <Input label="Username" value={username || ''} onChangeText={(text) => setUsername(text)} />      </View>      <View style={styles.verticallySpaced}>        <Input label="Website" value={website || ''} onChangeText={(text) => setWebsite(text)} />      </View>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Button          title={loading ? 'Loading ...' : 'Update'}          onPress={() => updateProfile({ username, website, avatar_url: avatarUrl })}          disabled={loading}        />      </View>      <View style={styles.verticallySpaced}>        <Button title="Sign Out" onPress={() => supabase.auth.signOut()} />      </View>    </View>  )}const styles = StyleSheet.create({  container: {    marginTop: 40,    padding: 12,  },  verticallySpaced: {    paddingTop: 4,    paddingBottom: 4,    alignSelf: 'stretch',  },  mt20: {    marginTop: 20,  },})
```

### Launch![#](#launch)

Now that we have all the components in place, let's update `App.tsx`:

App.tsx

```
1234567891011121314151617181920212223242526import { useState, useEffect } from 'react'import { supabase } from './lib/supabase'import Auth from './components/Auth'import Account from './components/Account'import { View } from 'react-native'import { Session } from '@supabase/supabase-js'export default function App() {  const [session, setSession] = useState<Session | null>(null)  useEffect(() => {    supabase.auth.getSession().then(({ data: { session } }) => {      setSession(session)    })    supabase.auth.onAuthStateChange((_event, session) => {      setSession(session)    })  }, [])  return (    <View>      {session && session.user ? <Account key={session.user.id} session={session} /> : <Auth />}    </View>  )}
```

Once that's done, run this in a terminal window:

```
1npm start
```

And then press the appropriate key for the environment you want to test the app in and you should see the completed app.

## Bonus: Profile photos[#](#bonus-profile-photos)

Every Supabase project is configured with [Storage](https://supabase.com/docs/guides/storage) for managing large files like photos and videos.

### Additional dependency installation[#](#additional-dependency-installation)

You will need an image picker that works on the environment you will build the project for, we will use `expo-image-picker` in this example.

```
1npx expo install expo-image-picker
```

### Create an upload widget[#](#create-an-upload-widget)

Let's create an avatar for the user so that they can upload a profile photo. We can start by creating a new component:

components/Avatar.tsx

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127128129130import { useState, useEffect } from 'react'import { supabase } from '../lib/supabase'import { StyleSheet, View, Alert, Image, Button } from 'react-native'import * as ImagePicker from 'expo-image-picker'interface Props {  size: number  url: string | null  onUpload: (filePath: string) => void}export default function Avatar({ url, size = 150, onUpload }: Props) {  const [uploading, setUploading] = useState(false)  const [avatarUrl, setAvatarUrl] = useState<string | null>(null)  const avatarSize = { height: size, width: size }  useEffect(() => {    if (url) downloadImage(url)  }, [url])  async function downloadImage(path: string) {    try {      const { data, error } = await supabase.storage.from('avatars').download(path)      if (error) {        throw error      }      const fr = new FileReader()      fr.readAsDataURL(data)      fr.onload = () => {        setAvatarUrl(fr.result as string)      }    } catch (error) {      if (error instanceof Error) {        console.log('Error downloading image: ', error.message)      }    }  }  async function uploadAvatar() {    try {      setUploading(true)      const result = await ImagePicker.launchImageLibraryAsync({        mediaTypes: ImagePicker.MediaTypeOptions.Images, // Restrict to only images        allowsMultipleSelection: false, // Can only select one image        allowsEditing: true, // Allows the user to crop / rotate their photo before uploading it        quality: 1,        exif: false, // We don't want nor need that data.      })      if (result.canceled || !result.assets || result.assets.length === 0) {        console.log('User cancelled image picker.')        return      }      const image = result.assets[0]      console.log('Got image', image)      if (!image.uri) {        throw new Error('No image uri!') // Realistically, this should never happen, but just in case...      }      const arraybuffer = await fetch(image.uri).then((res) => res.arrayBuffer())      const fileExt = image.uri?.split('.').pop()?.toLowerCase() ?? 'jpeg'      const path = `${Date.now()}.${fileExt}`      const { data, error: uploadError } = await supabase.storage        .from('avatars')        .upload(path, arraybuffer, {          contentType: image.mimeType ?? 'image/jpeg',        })      if (uploadError) {        throw uploadError      }      onUpload(data.path)    } catch (error) {      if (error instanceof Error) {        Alert.alert(error.message)      } else {        throw error      }    } finally {      setUploading(false)    }  }  return (    <View>      {avatarUrl ? (        <Image          source={{ uri: avatarUrl }}          accessibilityLabel="Avatar"          style={[avatarSize, styles.avatar, styles.image]}        />      ) : (        <View style={[avatarSize, styles.avatar, styles.noImage]} />      )}      <View>        <Button          title={uploading ? 'Uploading ...' : 'Upload'}          onPress={uploadAvatar}          disabled={uploading}        />      </View>    </View>  )}const styles = StyleSheet.create({  avatar: {    borderRadius: 5,    overflow: 'hidden',    maxWidth: '100%',  },  image: {    objectFit: 'cover',    paddingTop: 0,  },  noImage: {    backgroundColor: '#333',    borderWidth: 1,    borderStyle: 'solid',    borderColor: 'rgb(200, 200, 200)',    borderRadius: 5,  },})
```

### Add the new widget[#](#add-the-new-widget)

And then we can add the widget to the Account page:

components/Account.tsx

```
123456789101112131415161718192021// Import the new componentimport Avatar from './Avatar'// ...return (  <View>    {/* Add to the body */}    <View>      <Avatar        size={200}        url={avatarUrl}        onUpload={(url: string) => {          setAvatarUrl(url)          updateProfile({ username, website, avatar_url: url })        }}      />    </View>    {/* ... */}  </View>)// ...
```

Now you will need to run the prebuild command to get the application working on your chosen platform.

```
1npx expo prebuild
```

At this stage you have a fully functional application!

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/tutorials/with-expo-react-native.mdx)

Watch video guide

![Video guide preview](https://supabase.com/docs/_next/image?url=https%3A%2F%2Fimg.youtube.com%2Fvi%2FAE7dKIKMJy4%2F0.jpg&w=3840&q=75&dpl=dpl_5BYG5BkQhU19GEfZfhcgAbeGcRQo)

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