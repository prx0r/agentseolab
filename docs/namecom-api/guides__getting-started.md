> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Getting Started

> Learn how to authenticate and make your first API call with name.com Core API

# Follow these steps to quickly get up and running with the name.com Core API.

<Info>
  Prefer a typed client? Install an [official SDK](/sdks) (TypeScript, Go, or PHP — Python coming soon) and skip hand-rolled HTTP for your first call.

  Otherwise, download our latest [OpenAPI spec](https://namedotcom-cdn.name.tools/api-info/namecom.api.yaml) before you begin, especially if you plan to use your own code generation.
</Info>

## Step 1: Get Your API Token

<Steps>
  <Step title="Create Account">
    Create a name.com account if you don't have one already.

    <Warning>
      We recommend **not** using Google/SSO when creating a reseller account. SSO-based signup often sets your **account username to your email address**, which is not ideal for reseller/API usage.

      Pick a **generic, company-wide** username you can share across the team (e.g., `resellercompanyname`, `company-eng`, `company-dev`). This is the username you’ll use for HTTP Basic Auth, and your sandbox username will be this value with `-test` appended.
    </Warning>
  </Step>

  <Step title="Generate Tokens">
    Go to Account Settings → Security → API Tokens and issue both development and production tokens
  </Step>

  <Step title="Secure Storage">
    Keep your API token secure — treat it like a password
  </Step>
</Steps>

<Info>
  Newly generated sandbox (OT\&E) credentials can occasionally take **up to 15 minutes** to become active in the test environment. If you get a `401 Unauthorized` immediately after creating a token, wait a bit and retry. See [Testing Environment](/guides/testing-environment).
</Info>

<Warning>
  If your account has two-factor authentication (2FA) enabled, go to Account Settings → Security, and toggle name.com API Access on at the bottom.
</Warning>

## Step 2: Choose Your Environment

name.com offers two separate environments:

<CardGroup cols={2}>
  <Card title="Production" icon="globe">
    **Base URL:** `https://api.name.com`\
    **Purpose:** Live domain registrations, renewals, and management
  </Card>

  <Card title="Sandbox" icon="flask">
    **Base URL:** `https://api.dev.name.com`\
    **Purpose:** Safe testing and development — no real charges
  </Card>
</CardGroup>

### Sandbox Environment Details

<AccordionGroup>
  <Accordion title="Authentication Requirements">
    * Use your username with `-test` appended (e.g., `reseller123-test`)
    * Requires a separate sandbox API token
    * The sandbox is API-only — not accessible through the browser
  </Accordion>

  <Accordion title="Testing Features">
    * Supports the Try It feature (limited to test environment)
    * Includes preloaded testing credit
    * Data does not sync with production
  </Accordion>

  <Accordion title="Domain Management">
    * Test domains must be registered in sandbox before use
    * Domain availability and pricing may differ from production
    * Some TLDs are not available in sandbox environment
  </Accordion>
</AccordionGroup>

## Step 3: Authenticate Your API Requests

Use HTTP Basic Auth with your username and API token. See the full guide in [Authentication](/guides/authentication) for curl shorthand vs explicit header, and how to generate a Base64 token on Linux/macOS and Windows PowerShell.

<CodeGroup>
  ```bash Production theme={null}
  curl -u your-username:your-api-token https://api.name.com/core/v1/hello
  ```

  ```bash Sandbox theme={null}
  curl -u your-username-test:your-sandbox-token https://api.dev.name.com/core/v1/hello
  ```
</CodeGroup>

## Step 4: Make Your First API Call

Call the GET `/core/v1/hello` endpoint to verify connectivity:

<CodeGroup>
  ```bash Production theme={null}
  curl -u your-username:your-api-token https://api.name.com/core/v1/hello
  ```

  ```bash Sandbox theme={null}
  curl -u your-username-test:your-sandbox-token https://api.dev.name.com/core/v1/hello
  ```
</CodeGroup>

A successful response should look like this:

```json theme={null}
{
  "motd": "Welcome to Core API from Name.com",
  "serverName": "nameapiserver",
  "serverTime": "2025-01-01T12:15:00Z",
  "username": "myapiusername"
}
```

<Success>
  If you see this message — your authentication was successful!
</Success>

## Using "Try it" Feature

<Steps>
  <Step title="Navigate to Endpoint">
    Go to an endpoint you'd like to test (e.g., `GET /core/v1/domains` → `ListDomains`)
  </Step>

  <Step title="Click Try It">
    Click the "**Try it**" button at the top right of the endpoint panel
  </Step>

  <Step title="Select Environment">
    In the "**Environment**" dropdown (next to "**History**"):

    * Select **Mock Server** to test with sample responses (no credentials needed)
    * Select **Testing** to use the name.com sandbox environment
  </Step>

  <Step title="Enter Credentials">
    Use your sandbox credentials from Account Settings → API Tokens ([https://www.name.com/account/settings/api](https://www.name.com/account/settings/api))
  </Step>

  <Step title="Send Request">
    Click **Send** to make your test request
  </Step>
</Steps>

<Warning>
  Only use sandbox credentials when testing in the development environment. Never use production credentials unless you are working with real data.
</Warning>

## Troubleshooting Common Issues

<AccordionGroup>
  <Accordion title="401 Unauthorized">
    Check your username and API token; verify you're using the right environment
  </Accordion>

  <Accordion title="Permission Denied">
    If 2FA is enabled, go to Account Settings → Security and enable API Access
  </Accordion>

  <Accordion title="404 Not Found">
    Make sure the domain or resource exists; in sandbox, register test domains first
  </Accordion>
</AccordionGroup>

<Card title="Visit FAQ" icon="question" href="/resources/faq">
  Get help with troubleshooting
</Card>

## Next Steps

<CardGroup cols={2}>
  <Card title="Official SDKs" icon="cube" href="/sdks">
    Fastest path in TypeScript, Go, or PHP
  </Card>

  <Card title="Reseller Quickstart" icon="shopping-cart" href="/guides/quickstart">
    Search → register → manage MVP flow
  </Card>

  <Card title="Explore API Resources" icon="code" href="/api/v1/reference">
    Browse the complete API reference
  </Card>

  <Card title="Read API Overview" icon="book" href="/api/v1/overview">
    Understand API structure and features
  </Card>
</CardGroup>
