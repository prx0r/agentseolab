> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# API Overview

> Complete overview of name.com Core API structure, environments, and key features

# name.com API (CORE) Overview

The name.com API lets you search, register, and manage domains, DNS records, WHOIS privacy, and more — all through a secure, RESTful interface.

CORE is the latest version of our API, built for developers, SaaS platforms, and businesses.

For legacy v4 integrations, view the [v4 API documentation](https://www.name.com/api-docs). For a summary of what's new in name.com API (CORE), see the [Changelog](/api/v1/changelog)

## Base URLs

<CardGroup cols={2}>
  <Card title="Production" icon="globe">
    **Base URL:** `https://api.name.com`\
    **Purpose:** Manage live domains in your production account
  </Card>

  <Card title="Sandbox (Testing)" icon="flask">
    **Base URL:** `https://api.dev.name.com`\
    **Purpose:** Test and simulate actions without affecting real domains
  </Card>
</CardGroup>

## API Versioning

The name.com API uses path-based versioning (e.g., `core/v1/` in the endpoint URLs). Going forward, our API will be following semantic versioning on changes to the API.

<Info>
  * **Current version:** name.com API (CORE v1), released June 2025
  * **Versioning model:** Major version in the URL path (e.g., `https://api.name.com/core/v1`)
  * **Previous versions:** v4 is still supported and will sunset at a predetermined time in 2026
</Info>

For a detailed timeline of updates, breaking changes, deprecations, and upcoming features, see our [Changelog](/api/v1/changelog).

## Download the Latest OpenAPI Specification

Ready to start building? Download the latest version of name.com CORE API OpenAPI 3.1 specification below.

<CardGroup cols={1}>
  <Card title="YAML Format" icon="file-code" href="https://namedotcom-cdn.name.tools/api-info/namecom.api.yaml">
    Download the OpenAPI specification in YAML format
  </Card>
</CardGroup>

***

## Key Characteristics

<AccordionGroup>
  <Accordion title="RESTful Endpoints">
    Standard HTTP methods (GET, POST, PUT, DELETE)
  </Accordion>

  <Accordion title="Authentication">
    HTTP Basic Auth (username + API token). Sandbox requires a -test username and a sandbox token. See the full [Authentication](/guides/authentication) guide for curl `-u` vs explicit header and Base64 generation on Linux/macOS and Windows PowerShell.
  </Accordion>

  <Accordion title="Secure Access">
    HTTPS only (port 443)
  </Accordion>

  <Accordion title="Structured Resources">
    APIs are organized around Domains, DNS Records, Transfers, URL Forwarding, Vanity Nameservers, and Webhook Notifications
  </Accordion>
</AccordionGroup>

## Authentication

All API requests require **Basic Authentication** using your API credentials. See the [Authentication](/guides/authentication) guide for curl `-u` shorthand vs explicit header, and how to generate the Base64 value on Linux/macOS and Windows PowerShell.

```bash theme={null}
curl -X GET "https://api.dev.name.com/core/v1/hello" \
  -u "username:token"
```

The API uses HTTP Basic Authentication where:

* **Username**: Your name.com API username
* **Token**: Your API token (not your account password)

## Environment Details

The name.com API provides two fully separated environments for safe development and live operations:

### Production Environment

<Card title="Production Environment" icon="globe">
  * **Base URL:** `https://api.name.com`
  * **Purpose:** Manage real domains and billing
  * **Credentials:** Use your name.com username and production API token
</Card>

### Sandbox (Development) Environment

<Card title="Sandbox Environment" icon="flask">
  * **Base URL:** `https://api.dev.name.com`
  * **Purpose:** Safe for testing — no real charges
  * **Credentials:** Use your username with -test appended (e.g., `reseller123-test`) and your sandbox API token
  * **Features:** Preloaded testing credit available, domains and orders do not sync with production
</Card>

<Warning>
  **Important:** Domains must be created in sandbox before using them. For example, `GET /core/v1/domains/example.com` will return "Not Found" unless you register it first in the sandbox environment.
</Warning>

## Response Format

* API responses are returned in JSON format
* Fields set to default values (empty strings, false, 0) are omitted to simplify payloads
* On success (HTTP 200 OK), you receive a structured JSON response
* On error (HTTP 4xx/5xx), you receive an error JSON such as:

```json theme={null}
{
  "message": "Permission Denied",
  "details": "Authentication Error - Account Has Two-Step Verification Enabled"
}
```

<Info>
  Always check both the HTTP status code and the message/details fields to debug responses.
</Info>

## API Usage Guidelines

### Path Parameters

Insert actual values where `{}` appears in endpoints.

**Example:**

* `GET /core/v1/domains/{domainName}/records`
* `GET /core/v1/domains/example.org/records`

### HTTP Methods and Content-Type

Use the correct HTTP verb:

| Method | Action                      |
| ------ | --------------------------- |
| GET    | Retrieve a resource         |
| POST   | Create a new resource       |
| PUT    | Update an existing resource |
| DELETE | Delete a resource           |

When sending JSON payloads (POST/PUT), always set the header: `Content-Type: application/json`

### Pagination

* For list endpoints, use the `perPage` and `page` query parameters
* The API provides Link headers for easy pagination: `Link: <https://api.name.com/core/v1/domains?page=2>; rel="next"`
* You can use these headers to automate paging through large lists of results

### Important Note on Colon (:) in Endpoint Paths

For the following endpoints:

* `POST /core/v1/domains:checkAvailability`
* `POST /core/v1/domains:search`
* `POST /core/v1/domains:searchStream`

<Warning>
  **Do not URL-encode the colon (`:`) in the request path.**

  Some HTTP clients or SDKs may automatically encode `:` to `%3A` (e.g., `/v4/domains%3AcheckAvailability`), which will cause the request to fail.

  Always use the literal colon character `:` in the endpoint URL.
</Warning>

### Rate Limits

* **20 requests per second**
* **3,000 requests per hour**

If you exceed the account-wide rate limit, the server responds with `429 Too Many Requests`.

#### Domain registration limits (selected registry connections)

For domain registrations (`POST /core/v1/domains`) on TLDs served by certain registry connections, an additional limit applies **per account and per domain name**. This limit is separate from the account-wide limits above and is intended to protect registry operations from abusive retry patterns—for example, rapid repeated attempts to register the same name.

* The limit is evaluated independently for each account–domain pair.
* Registering a different domain on the same account, or the same domain from a different account, is not affected by another pair's limit.
* The set of registry connections subject to this limit may expand over time.
* When this limit is exceeded, the API returns `429 Too Many Requests` with a `Retry-After` header indicating when you may retry. The response message differs from the account-wide rate limit message.

<Info>
  Implement retry and backoff logic in your integration, and honor `Retry-After` when present.
</Info>

## Common API Errors

<AccordionGroup>
  <Accordion title="Not Found">
    Resource not found in environment. Make sure the domain or record exists in the correct environment.
  </Accordion>

  <Accordion title="Permission Denied (2FA enabled)">
    2FA-enabled accounts are not supported. Disable Two-Factor Authentication on your account.
  </Accordion>

  <Accordion title="Invalid Argument (Bad IPv4)">
    Invalid or malformed input value. Correct the input, such as providing a valid IPv4 address.
  </Accordion>

  <Accordion title="Permission Denied (Wrong env)">
    Mixing production/sandbox credentials. Double-check that your API URL matches your credentials.
  </Accordion>

  <Accordion title="Unauthenticated">
    Authentication missing or invalid. Fix your Basic Auth headers and verify no typos in URLs.
  </Accordion>

  <Accordion title="Permission Denied (Bad token)">
    Incorrect or revoked API token. Regenerate a new API token and use it for your requests.
  </Accordion>
</AccordionGroup>

## Languages

Any HTTPS client can call the Core API. For the fastest start in supported languages, use an [official SDK](/sdks) (TypeScript, Go, PHP — Python coming soon).

<CardGroup cols={4}>
  <Card title="cURL" icon="terminal">
    Command-line tool
  </Card>

  <Card title="JavaScript" icon="js">
    Browser & Node.js
  </Card>

  <Card title="Python" icon="python">
    Python HTTP libraries
  </Card>

  <Card title="PHP" icon="php">
    PHP HTTP clients
  </Card>

  <Card title="Java" icon="java">
    Java HTTP clients
  </Card>

  <Card title="C#" icon="c">
    .NET HTTP clients
  </Card>

  <Card title="Go" icon="golang">
    Go HTTP packages
  </Card>

  <Card title="Node.js" icon="node">
    Node.js libraries
  </Card>
</CardGroup>

## Next Steps

You're ready to start building!

<CardGroup cols={2}>
  <Card title="Build Your Integration" icon="code" href="https://namedotcom-cdn.name.tools/api-info/namecom.api.yaml">
    Explore the latest CORE API Resources
  </Card>

  <Card title="Legacy v4 API" icon="book" href="https://www.name.com/api-docs">
    View the v4 API Documentation
  </Card>
</CardGroup>

### Accessing the Legacy v4 API

We continue to maintain the v4 API documentation for existing integrations and legacy systems. While the current documentation focuses on the latest CORE API, you can still reference the full v4 guides if your systems depend on them.

<Info>
  * v4 remains supported for legacy users
  * All new integrations should use CORE v1
  * Only CORE v1+ will receive new features
  * Any v4 deprecation will be announced via the Changelog
</Info>

All API access requires HTTPS and authentication with your name.com credentials and API token.

***

<Info>
  **Account Services**

  Contact us at [reseller@name.com](mailto:reseller@name.com)
</Info>

<Card title="Terms of Service" icon="file-contract" href="https://www.name.com/policies/api-access-agreement">
  Review our API Access Agreement and Terms of Service
</Card>
