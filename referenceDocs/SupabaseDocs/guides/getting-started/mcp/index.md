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

3.  AI Tools

5.  [Model context protocol (MCP)](https://supabase.com/docs/guides/getting-started/mcp)

# 

Model context protocol (MCP)

## 

Connect your AI tools to Supabase using MCP

* * *

The [Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) is a standard for connecting Large Language Models (LLMs) to platforms like Supabase. This guide covers how to connect Supabase to the following AI tools using MCP:

-   [Cursor](https://www.cursor.com/)
-   [Windsurf](https://docs.codeium.com/windsurf) (Codium)
-   [Cline](https://github.com/cline/cline) (VS Code extension)
-   [Claude desktop](https://claude.ai/download)
-   [Claude code](https://claude.ai/code)

Once connected, your AI assistants can interact with and query your Supabase projects on your behalf.

## Step 1: Create a personal access token (PAT)[#](#step-1-create-a-personal-access-token-pat)

First, go to your [Supabase settings](https://supabase.com/dashboard/account/tokens) and create a personal access token. Give it a name that describes its purpose, like "Cursor MCP Server". This will be used to authenticate the MCP server with your Supabase account.

## Step 2: Configure in your AI tool[#](#step-2-configure-in-your-ai-tool)

MCP compatible tools can connect to Supabase using the [Supabase MCP server](https://github.com/supabase-community/supabase-mcp). Below are instructions for connecting to this server using popular AI tools:

### Cursor[#](#cursor)

1.  Open Cursor and create a `.cursor` directory in your project root if it doesn't exist.
    
2.  Create a `.cursor/mcp.json` file if it doesn't exist and open it.
    
3.  Add the following configuration:
    
    macOSWindowsWindows (WSL)Linux
    
    ```
    12345678910111213{  "mcpServers": {    "supabase": {      "command": "npx",      "args": [        "-y",        "@supabase/mcp-server-supabase@latest",        "--access-token",        "<personal-access-token>"      ]    }  }}
    ```
    
    Replace `<personal-access-token>` with your personal access token.
    
4.  Save the configuration file.
    
5.  Open Cursor and navigate to **Settings/MCP**. You should see a green active status after the server is successfully connected.
    

### Windsurf[#](#windsurf)

1.  Open Windsurf and navigate to the Cascade assistant.
    
2.  Tap on the hammer (MCP) icon, then **Configure** to open the configuration file.
    
3.  Add the following configuration:
    
    macOSWindowsWindows (WSL)Linux
    
    ```
    12345678910111213{  "mcpServers": {    "supabase": {      "command": "npx",      "args": [        "-y",        "@supabase/mcp-server-supabase@latest",        "--access-token",        "<personal-access-token>"      ]    }  }}
    ```
    
    Replace `<personal-access-token>` with your personal access token.
    
4.  Save the configuration file and reload by tapping **Refresh** in the Cascade assistant.
    
5.  You should see a green active status after the server is successfully connected.
    

### Cline[#](#cline)

1.  Open the Cline extension in VS Code and tap the **MCP Servers** icon.
    
2.  Tap **Configure MCP Servers** to open the configuration file.
    
3.  Add the following configuration:
    
    macOSWindowsWindows (WSL)Linux
    
    ```
    12345678910111213{  "mcpServers": {    "supabase": {      "command": "npx",      "args": [        "-y",        "@supabase/mcp-server-supabase@latest",        "--access-token",        "<personal-access-token>"      ]    }  }}
    ```
    
    Replace `<personal-access-token>` with your personal access token.
    
4.  Save the configuration file. Cline should automatically reload the configuration.
    
5.  You should see a green active status after the server is successfully connected.
    

### Claude desktop[#](#claude-desktop)

1.  Open Claude desktop and navigate to **Settings**.
    
2.  Under the **Developer** tab, tap **Edit Config** to open the configuration file.
    
3.  Add the following configuration:
    
    macOSWindowsWindows (WSL)Linux
    
    ```
    12345678910111213{  "mcpServers": {    "supabase": {      "command": "npx",      "args": [        "-y",        "@supabase/mcp-server-supabase@latest",        "--access-token",        "<personal-access-token>"      ]    }  }}
    ```
    
    Replace `<personal-access-token>` with your personal access token.
    
4.  Save the configuration file and restart Claude desktop.
    
5.  From the new chat screen, you should see a hammer (MCP) icon appear with the new MCP server available.
    

### Claude code[#](#claude-code)

1.  Create a `.mcp.json` file in your project root if it doesn't exist.
    
2.  Add the following configuration:
    
    macOSWindowsWindows (WSL)Linux
    
    ```
    12345678910111213{  "mcpServers": {    "supabase": {      "command": "npx",      "args": [        "-y",        "@supabase/mcp-server-supabase@latest",        "--access-token",        "<personal-access-token>"      ]    }  }}
    ```
    
    Replace `<personal-access-token>` with your personal access token.
    
3.  Save the configuration file.
    
4.  Restart Claude code to apply the new configuration.
    

### Next steps[#](#next-steps)

Your AI tool is now connected to Supabase using MCP. Try asking your AI assistant to create a new project, create a table, or fetch project config.

For a full list of tools available, see the [GitHub README](https://github.com/supabase-community/supabase-mcp#tools). If you experience any issues, [submit an bug report](https://github.com/supabase-community/supabase-mcp/issues/new?template=1.Bug_report.md).

## MCP for local Supabase instances[#](#mcp-for-local-supabase-instances)

The Supabase MCP server connects directly to the cloud platform to access your database. If you are running a local instance of Supabase, you can instead use the [Postgres MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/postgres) to connect to your local database. This MCP server runs all queries as read-only transactions.

### Step 1: Find your database connection string[#](#step-1-find-your-database-connection-string)

To connect to your local Supabase instance, you need to get the connection string for your local database. You can find your connection string by running:

```
1supabase status
```

or if you are using `npx`:

```
1npx supabase status
```

This will output a list of details about your local Supabase instance. Copy the `DB URL` field in the output.

### Step 2: Configure the MCP server[#](#step-2-configure-the-mcp-server)

Configure your client with the following:

macOSWindowsWindows (WSL)Linux

```
12345678{  "mcpServers": {    "supabase": {      "command": "npx",      "args": ["-y", "@modelcontextprotocol/server-postgres", "<connection-string>"]    }  }}
```

Replace `<connection-string>` with your connection string.

### Next steps[#](#next-steps)

Your AI tool is now connected to your local Supabase instance using MCP. Try asking the AI tool to query your database using natural language commands.

[Edit this page on GitHub](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/getting-started/mcp.mdx)

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