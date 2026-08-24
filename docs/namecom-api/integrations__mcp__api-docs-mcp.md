> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# API Docs MCP

> Read‑only MCP server that lets agents search and cite the name.com Core API documentation in chat. It does not execute API calls; use the name.com Core API MCP for live operations.

## What it can do

* Search across the complete name.com CORE API documentation content
* Answer “how do I…” questions with links back to related pages
* Surface endpoint details and examples for implementation and debugging

## Setup

Add the name.com CORE API Docs MCP server configuration to your desired MCP client (e.g., Cursor).

In Cursor:

<Steps>
  <Step title="Open MCP settings">
    Settings → MCP → Add Server
  </Step>

  <Step title="Copy server configuration">
    Paste the client configuration below
  </Step>

  <Step title="Save and enable">
    Save the server, enable it, and start asking questions!
  </Step>
</Steps>

Client configuration:

```json theme={null}
{
  "mcpServers": {
    "namecom-docs": {
      "type": "http",
      "url": "https://docs.name.com/mcp"
    }
  }
}
```

## Example prompts

* “Search the docs for sandbox authentication requirements.”
* “Show the steps to generate an API token and link the page.”
* “Find the section that explains webhook retries.”
* “What parameters are required for the transfer endpoint in the docs?”
