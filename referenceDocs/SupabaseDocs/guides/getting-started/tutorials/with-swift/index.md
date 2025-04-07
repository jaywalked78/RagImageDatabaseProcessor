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

5.  [Swift](https://supabase.com/docs/guides/getting-started/tutorials/with-swift)

# 

Build a User Management App with Swift and SwiftUI

* * *

This tutorial demonstrates how to build a basic user management app. The app authenticates and identifies the user, stores their profile information in the database, and allows the user to log in, update their profile details, and upload a profile photo. The app uses:

-   [Supabase Database](https://supabase.com/docs/guides/database) - a Postgres database for storing your user data and [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) so data is protected and users can only access their own information.
-   [Supabase Auth](https://supabase.com/docs/guides/auth) - allow users to sign up and log in.
-   [Supabase Storage](https://supabase.com/docs/guides/storage) - users can upload a profile photo.

![Supabase User Management example](https://supabase.com/docs/img/supabase-swift-demo.png)

If you get stuck while working through this guide, refer to the [full example on GitHub](https://github.com/supabase/supabase/tree/master/examples/user-management/swift-user-management).

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

Let's start building the SwiftUI app from scratch.

### Create a SwiftUI app in Xcode[#](#create-a-swiftui-app-in-xcode)

Open Xcode and create a new SwiftUI project.

Add the [supabase-swift](https://github.com/supabase/supabase-swift) dependency.

Add the `https://github.com/supabase/supabase-swift` package to your app. For instructions, see the [Apple tutorial on adding package dependencies](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app).

Create a helper file to initialize the Supabase client. You need the API URL and the `anon` key that you copied [earlier](#get-the-api-keys). These variables will be exposed on the application, and that's completely fine since you have [Row Level Security](https://supabase.com/docs/guides/auth#row-level-security) enabled on your database.

Supabase.swift

```
1234567import Foundationimport Supabaselet supabase = SupabaseClient(  supabaseURL: URL(string: "YOUR_SUPABASE_URL")!,  supabaseKey: "YOUR_SUPABASE_ANON_KEY")
```

### Set up a login view[#](#set-up-a-login-view)

Set up a SwiftUI view to manage logins and sign ups. Users should be able to sign in using a magic link.

AuthView.swift

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566import SwiftUIimport Supabasestruct AuthView: View {  @State var email = ""  @State var isLoading = false  @State var result: Result<Void, Error>?  var body: some View {    Form {      Section {        TextField("Email", text: $email)          .textContentType(.emailAddress)          .textInputAutocapitalization(.never)          .autocorrectionDisabled()      }      Section {        Button("Sign in") {          signInButtonTapped()        }        if isLoading {          ProgressView()        }      }      if let result {        Section {          switch result {          case .success:            Text("Check your inbox.")          case .failure(let error):            Text(error.localizedDescription).foregroundStyle(.red)          }        }      }    }    .onOpenURL(perform: { url in      Task {        do {          try await supabase.auth.session(from: url)        } catch {          self.result = .failure(error)        }      }    })  }  func signInButtonTapped() {    Task {      isLoading = true      defer { isLoading = false }      do {        try await supabase.auth.signInWithOTP(            email: email,            redirectTo: URL(string: "io.supabase.user-management://login-callback")        )        result = .success(())      } catch {        result = .failure(error)      }    }  }}
```

The example uses a custom `redirectTo` URL. For this to work, add a custom redirect URL to Supabase and a custom URL scheme to your SwiftUI application. Follow the guide on [implementing deep link handling](https://supabase.com/docs/guides/auth/native-mobile-deep-linking?platform=swift).

### Account view[#](#account-view)

After a user is signed in, you can allow them to edit their profile details and manage their account.

Create a new view for that called `ProfileView.swift`.

ProfileView.swift

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596import SwiftUIstruct ProfileView: View {  @State var username = ""  @State var fullName = ""  @State var website = ""  @State var isLoading = false  var body: some View {    NavigationStack {      Form {        Section {          TextField("Username", text: $username)            .textContentType(.username)            .textInputAutocapitalization(.never)          TextField("Full name", text: $fullName)            .textContentType(.name)          TextField("Website", text: $website)            .textContentType(.URL)            .textInputAutocapitalization(.never)        }        Section {          Button("Update profile") {            updateProfileButtonTapped()          }          .bold()          if isLoading {            ProgressView()          }        }      }      .navigationTitle("Profile")      .toolbar(content: {        ToolbarItem(placement: .topBarLeading){          Button("Sign out", role: .destructive) {            Task {              try? await supabase.auth.signOut()            }          }        }      })    }    .task {      await getInitialProfile()    }  }  func getInitialProfile() async {    do {      let currentUser = try await supabase.auth.session.user      let profile: Profile =      try await supabase        .from("profiles")        .select()        .eq("id", value: currentUser.id)        .single()        .execute()        .value      self.username = profile.username ?? ""      self.fullName = profile.fullName ?? ""      self.website = profile.website ?? ""    } catch {      debugPrint(error)    }  }  func updateProfileButtonTapped() {    Task {      isLoading = true      defer { isLoading = false }      do {        let currentUser = try await supabase.auth.session.user        try await supabase          .from("profiles")          .update(            UpdateProfileParams(              username: username,              fullName: fullName,              website: website            )          )          .eq("id", value: currentUser.id)          .execute()      } catch {        debugPrint(error)      }    }  }}
```

### Models[#](#models)

In `ProfileView.swift`, you used 2 model types for deserializing the response and serializing the request to Supabase. Add those in a new `Models.swift` file.

Models.swift

```
1234567891011121314151617181920212223struct Profile: Decodable {  let username: String?  let fullName: String?  let website: String?  enum CodingKeys: String, CodingKey {    case username    case fullName = "full_name"    case website  }}struct UpdateProfileParams: Encodable {  let username: String  let fullName: String  let website: String  enum CodingKeys: String, CodingKey {    case username    case fullName = "full_name"    case website  }}
```

### Launch![#](#launch)

Now that you've created all the views, add an entry point for the application. This will verify if the user has a valid session and route them to the authenticated or non-authenticated state.

Add a new `AppView.swift` file.

AppView.swift

```
12345678910111213141516171819202122import SwiftUIstruct AppView: View {  @State var isAuthenticated = false  var body: some View {    Group {      if isAuthenticated {        ProfileView()      } else {        AuthView()      }    }    .task {      for await state in supabase.auth.authStateChanges {        if [.initialSession, .signedIn, .signedOut].contains(state.event) {          isAuthenticated = state.session != nil        }      }    }  }}
```

Update the entry point to the newly created `AppView`. Run in Xcode to launch your application in the simulator.

## Bonus: Profile photos[#](#bonus-profile-photos)

Every Supabase project is configured with [Storage](https://supabase.com/docs/guides/storage) for managing large files like photos and videos.

### Add `PhotosPicker`[#](#add-photospicker)

Let's add support for the user to pick an image from the library and upload it. Start by creating a new type to hold the picked avatar image:

AvatarImage.swift

```
12345678910111213141516171819202122232425262728293031import SwiftUIstruct AvatarImage: Transferable, Equatable {  let image: Image  let data: Data  static var transferRepresentation: some TransferRepresentation {    DataRepresentation(importedContentType: .image) { data in      guard let image = AvatarImage(data: data) else {        throw TransferError.importFailed      }      return image    }  }}extension AvatarImage {  init?(data: Data) {    guard let uiImage = UIImage(data: data) else {      return nil    }    let image = Image(uiImage: uiImage)    self.init(image: image, data: data)  }}enum TransferError: Error {  case importFailed}
```

#### Add `PhotosPicker` to profile page[#](#add-photospicker-to-profile-page)

ProfileView.swift

```
123456789101112131415161718192021222324252627282930313233343536373839404142434445464748495051525354555657585960616263646566676869707172737475767778798081828384858687888990919293949596979899100101102103104105106107108109110111112113114115116117118119120121122123124125126127128129130131132133134135136137138139140141142143144145146147148149150151152153154155156157158159160161162163164165166167+ import PhotosUI+ import Storage+ import Supabaseimport SwiftUIstruct ProfileView: View {  @State var username = ""  @State var fullName = ""  @State var website = ""  @State var isLoading = false+ @State var imageSelection: PhotosPickerItem?+ @State var avatarImage: AvatarImage?  var body: some View {    NavigationStack {      Form {+        Section {+          HStack {+            Group {+              if let avatarImage {+                avatarImage.image.resizable()+              } else {+                Color.clear+              }+            }+            .scaledToFit()+            .frame(width: 80, height: 80)++            Spacer()++            PhotosPicker(selection: $imageSelection, matching: .images) {+              Image(systemName: "pencil.circle.fill")+                .symbolRenderingMode(.multicolor)+                .font(.system(size: 30))+                .foregroundColor(.accentColor)+            }+          }+        }        Section {          TextField("Username", text: $username)            .textContentType(.username)            .textInputAutocapitalization(.never)          TextField("Full name", text: $fullName)            .textContentType(.name)          TextField("Website", text: $website)            .textContentType(.URL)            .textInputAutocapitalization(.never)        }        Section {          Button("Update profile") {            updateProfileButtonTapped()          }          .bold()          if isLoading {            ProgressView()          }        }      }      .navigationTitle("Profile")      .toolbar(content: {        ToolbarItem {          Button("Sign out", role: .destructive) {            Task {              try? await supabase.auth.signOut()            }          }        }      })+      .onChange(of: imageSelection) { _, newValue in+        guard let newValue else { return }+        loadTransferable(from: newValue)+      }    }    .task {      await getInitialProfile()    }  }  func getInitialProfile() async {    do {      let currentUser = try await supabase.auth.session.user      let profile: Profile =      try await supabase        .from("profiles")        .select()        .eq("id", value: currentUser.id)        .single()        .execute()        .value      username = profile.username ?? ""      fullName = profile.fullName ?? ""      website = profile.website ?? ""+      if let avatarURL = profile.avatarURL, !avatarURL.isEmpty {+        try await downloadImage(path: avatarURL)+      }    } catch {      debugPrint(error)    }  }  func updateProfileButtonTapped() {    Task {      isLoading = true      defer { isLoading = false }      do {+        let imageURL = try await uploadImage()        let currentUser = try await supabase.auth.session.user        let updatedProfile = Profile(          username: username,          fullName: fullName,          website: website,+          avatarURL: imageURL        )        try await supabase          .from("profiles")          .update(updatedProfile)          .eq("id", value: currentUser.id)          .execute()      } catch {        debugPrint(error)      }    }  }+  private func loadTransferable(from imageSelection: PhotosPickerItem) {+    Task {+      do {+        avatarImage = try await imageSelection.loadTransferable(type: AvatarImage.self)+      } catch {+        debugPrint(error)+      }+    }+  }++  private func downloadImage(path: String) async throws {+    let data = try await supabase.storage.from("avatars").download(path: path)+    avatarImage = AvatarImage(data: data)+  }++  private func uploadImage() async throws -> String? {+    guard let data = avatarImage?.data else { return nil }++    let filePath = "\(UUID().uuidString).jpeg"++    try await supabase.storage+      .from("avatars")+      .upload(+        filePath,+        data: data,+        options: FileOptions(contentType: "image/jpeg")+      )++    return filePath+  }}
```

Finally, update your Models.

Models.swift

```
12345678910111213struct Profile: Codable {  let username: String?  let fullName: String?  let website: String?  let avatarURL: String?  enum CodingKeys: String, CodingKey {    case username    case fullName = "full_name"    case website    case avatarURL = "avatar_url"  }}
```

You no longer need the `UpdateProfileParams` struct, as you can now reuse the `Profile` struct for both request and response calls.

At this stage you have a fully functional application!

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/tutorials/with-swift.mdx)

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