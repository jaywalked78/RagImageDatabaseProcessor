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

Auth

1.  Auth

3.  Getting Started

5.  [React Native](https://supabase.com/docs/guides/auth/quickstarts/react-native)

# 

Use Supabase Auth with React Native

## 

Learn how to use Supabase Auth with React Native

* * *

1

### Create a new Supabase project

[Launch a new project](https://supabase.com/dashboard) in the Supabase Dashboard.

Your new database has a table for storing your users. You can see that this table is currently empty by running some SQL in the [SQL Editor](https://supabase.com/dashboard/project/_/sql).

```
1select * from auth.users;
```

2

### Create a React app

Create a React app using the `create-expo-app` command.

```
1npx create-expo-app -t expo-template-blank-typescript my-app
```

3

### Install the Supabase client library

Install `supabase-js` and the required dependencies.

```
1cd my-app && npx expo install @supabase/supabase-js @react-native-async-storage/async-storage @rneui/themed react-native-url-polyfill
```

4

### Set up your login component

Create a helper file `lib/supabase.ts` that exports a Supabase client using your [Project URL and public API (anon) key](https://supabase.com/dashboard/project/_/settings/api).

```
1234567891011121314151617181920212223242526272829import { AppState } from 'react-native'import 'react-native-url-polyfill/auto'import AsyncStorage from '@react-native-async-storage/async-storage'import { createClient } from '@supabase/supabase-js'const supabaseUrl = YOUR_REACT_NATIVE_SUPABASE_URLconst supabaseAnonKey = YOUR_REACT_NATIVE_SUPABASE_ANON_KEYexport const supabase = createClient(supabaseUrl, supabaseAnonKey, {  auth: {    storage: AsyncStorage,    autoRefreshToken: true,    persistSession: true,    detectSessionInUrl: false,  },})// Tells Supabase Auth to continuously refresh the session automatically// if the app is in the foreground. When this is added, you will continue// to receive `onAuthStateChange` events with the `TOKEN_REFRESHED` or// `SIGNED_OUT` event if the user's session is terminated. This should// only be registered once.AppState.addEventListener('change', (state) => {  if (state === 'active') {    supabase.auth.startAutoRefresh()  } else {    supabase.auth.stopAutoRefresh()  }})
```

5

### Create a login component

Let's set up a React Native component to manage logins and sign ups.

```
1234567891011121314151617181920212223242526272829303132333435363738394041424344454647484950515253545556575859606162636465666768697071727374757677787980818283import React, { useState } from 'react'import { Alert, StyleSheet, View } from 'react-native'import { supabase } from '../lib/supabase'import { Button, Input } from '@rneui/themed'export default function Auth() {  const [email, setEmail] = useState('')  const [password, setPassword] = useState('')  const [loading, setLoading] = useState(false)  async function signInWithEmail() {    setLoading(true)    const { error } = await supabase.auth.signInWithPassword({      email: email,      password: password,    })    if (error) Alert.alert(error.message)    setLoading(false)  }  async function signUpWithEmail() {    setLoading(true)    const {      data: { session },      error,    } = await supabase.auth.signUp({      email: email,      password: password,    })    if (error) Alert.alert(error.message)    if (!session) Alert.alert('Please check your inbox for email verification!')    setLoading(false)  }  return (    <View style={styles.container}>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Input          label="Email"          leftIcon={{ type: 'font-awesome', name: 'envelope' }}          onChangeText={(text) => setEmail(text)}          value={email}          placeholder="email@address.com"          autoCapitalize={'none'}        />      </View>      <View style={styles.verticallySpaced}>        <Input          label="Password"          leftIcon={{ type: 'font-awesome', name: 'lock' }}          onChangeText={(text) => setPassword(text)}          value={password}          secureTextEntry={true}          placeholder="Password"          autoCapitalize={'none'}        />      </View>      <View style={[styles.verticallySpaced, styles.mt20]}>        <Button title="Sign in" disabled={loading} onPress={() => signInWithEmail()} />      </View>      <View style={styles.verticallySpaced}>        <Button title="Sign up" disabled={loading} onPress={() => signUpWithEmail()} />      </View>    </View>  )}const styles = StyleSheet.create({  container: {    marginTop: 40,    padding: 12,  },  verticallySpaced: {    paddingTop: 4,    paddingBottom: 4,    alignSelf: 'stretch',  },  mt20: {    marginTop: 20,  },})
```

6

### Add the Auth component to your app

Add the `Auth` component to your `App.tsx` file. If the user is logged in, print the user id to the screen.

```
123456789101112131415161718192021222324252627import 'react-native-url-polyfill/auto'import { useState, useEffect } from 'react'import { supabase } from './lib/supabase'import Auth from './components/Auth'import { View, Text } from 'react-native'import { Session } from '@supabase/supabase-js'export default function App() {  const [session, setSession] = useState<Session | null>(null)  useEffect(() => {    supabase.auth.getSession().then(({ data: { session } }) => {      setSession(session)    })    supabase.auth.onAuthStateChange((_event, session) => {      setSession(session)    })  }, [])  return (    <View>      <Auth />      {session && session.user && <Text>{session.user.id}</Text>}    </View>  )}
```

7

### Start the app

Start the app, and follow the instructions in the terminal.

```
1npm start
```

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/auth/quickstarts/react-native.mdx)

-   Need some help?
    
    [Contact support](https://supabase.com/support)
-   Latest product updates?
    
    [See Changelog](https://supabase.com/changelog)
-   Something's not right?
    
    [Check system status](https://status.supabase.com/)

* * *

[© Supabase Inc](https://supabase.com/)—[Contributing](https://github.com/supabase/supabase/blob/master/apps/docs/DEVELOPERS.md)[Author Styleguide](https://github.com/supabase/supabase/blob/master/apps/docs/CONTRIBUTING.md)[Open Source](https://supabase.com/open-source)[SupaSquad](https://supabase.com/supasquad)Privacy Settings

[GitHub](https://github.com/supabase/supabase)[Twitter](https://twitter.com/supabase)[Discord](https://discord.supabase.com/)