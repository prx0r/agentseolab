> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# name.com MCP

> The name.com Model Context Protocol (MCP) server lets AI agents (e.g., Cursor, Claude Desktop) safely call name.com Core API operations on your behalf. This enables assistants to look up account info, manage domains, and perform other tasks programmatically with your authorization.

## What it can do

* Make authenticated calls to name.com CORE API endpoints
* Retrieve and summarize API responses in chat
* Automate common workflows (e.g., check account credit balance, purchase & manage domains, configure DNS)

## Setup

Add the server to your MCP client (e.g., Cursor) configuration and provide your API credentials.

In Cursor:

<Steps>
  <Step title="Open MCP settings">
    Settings → MCP → Add Server (may differ by MCP client)
  </Step>

  <Step title="Paste the example configuration below">
    The example config is complete aside from filling in environment variables
  </Step>

  <Step title="Set environment variables">
    Provide your API username, token, and base URL (production or sandbox). If base URL is not provided, the sandbox URL will be used by default.
  </Step>

  <Step title="Save and prompt">
    Save the server and test with a simple request: "How many domains are expiring soon in my account?"
  </Step>
</Steps>

Example client configuration:

```json theme={null}
{
  "mcpServers": {
    "namecom-mcp": {
      "command": "npx",
      "args": ["-y", "namecom-mcp@latest"],
      "env": {
        "NAME_USERNAME": "<your_username_or_username-test>",
        "NAME_TOKEN": "<your_api_token>",
        "NAME_API_URL": "https://mcp.name.com" # only required if using the production environment
      }
    }
  }
}
```

<Tip>
  Sandbox URL: <code>[https://mcp.dev.name.com](https://mcp.dev.name.com)</code>

  Production URL: <code>[https://mcp.name.com](https://mcp.name.com)</code>
</Tip>

## Example prompts

* “What is my account credit balance?”
* “I need help finding a domain for my new business idea: a coffee shop for people and their pets!”
* “Please tell me what domains of mine are expiring in the next 3 months”
* “Renew myawesomedomain.rocks for 3 more years”

## Reference

For more details about the name.com CORE API MCP Server, please refer to the published NPM package:

* npm package: `https://www.npmjs.com/package/namecom-mcp`
