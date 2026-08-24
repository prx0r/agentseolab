> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# v4 to CORE API Migration

> Complete guide for migrating from the v4 API to the name.com Core API

# v4 To name.com API (Core) Migration Guide

## Why Upgrade?

<CardGroup cols={2}>
  <Card title="Better Documentation" icon="book">
    CORE version uses OpenAPI 3.1-based documentation for better tooling and interactive exploration
  </Card>

  <Card title="Cleaner Errors" icon="alert-circle">
    Cleaner, consistent error messages and HTTP status codes
  </Card>

  <Card title="Streamlined Endpoints" icon="code">
    Streamlined, consolidated endpoints (e.g. UpdateDomain)
  </Card>

  <Card title="Enforced Standards" icon="shield">
    Enforced standards for content types and default response formatting
  </Card>
</CardGroup>

## Upgrading from the legacy v4 API to the new name.com API (CORE)

Welcome to the name.com API! This new API offers a modern, RESTful interface for managing your domains, DNS records, and related services, succeeding our legacy v4 API. We've rebuilt the name.com API from the ground up to provide faster iteration, improved stability, more consistent behavior, and a better overall developer experience.

<Warning>
  **IMPORTANT: Breaking Changes**

  Migrating from the v4 API to the name.com API (CORE) is a breaking change. You will need to review and update your existing integrations to align with the new API structure, endpoints, and behaviors outlined below. The v4 API remains accessible for a transition period, but we strongly encourage all new integrations and existing integrations to migrate to the name.com API (CORE)
</Warning>

## Key Changes Requiring Your Attention & Migration Steps

### 1. New API Documentation (OpenAPI 3.1)

<AccordionGroup>
  <Accordion title="What Changed">
    The Core API documentation is now provided in OpenAPI 3.1 format
  </Accordion>

  <Accordion title="Why">
    This offers significantly better tooling support, interactive documentation capabilities (e.g., "Try it out" features), and clearer schema definitions
  </Accordion>

  <Accordion title="Action Required">
    Familiarize yourself with the new documentation structure. You can leverage a wide range of OpenAPI 3.1 compatible tools to generate client libraries, explore endpoints, and understand request/response models
  </Accordion>
</AccordionGroup>

### 2. Improved Error Handling & Messaging

We've overhauled error responses for clarity and accuracy:

<CardGroup cols={2}>
  <Card title="Before" icon="x-circle">
    Generic 500 Internal Server Error responses for many client-side or predictable error conditions
  </Card>

  <Card title="After" icon="check-circle">
    More specific and appropriate HTTP status codes (e.g., 401, 402, 422)
  </Card>
</CardGroup>

**Example:** If an action fails due to insufficient account credit, the API will now return `402 Payment Required` instead of the previous `500 Internal Server Error`.

<Steps>
  <Step title="Review Error Handling">
    Update your error handling logic to expect and correctly process more specific HTTP status codes
  </Step>

  <Step title="Update Authentication Checks">
    Adjust authentication failure checks to look for `401 Unauthorized`. Treat `403 Forbidden` as a permissions issue for an authenticated user
  </Step>
</Steps>

### 3. Consistent Default Values in API Responses

<AccordionGroup>
  <Accordion title="What Changed">
    API responses will now consistently include fields with their default values (e.g., `false` for booleans, `0` for numbers, `""` for empty strings) instead of omitting them
  </Accordion>

  <Accordion title="Example">
    The Search API previously omitted `"purchasable": false;` it is now explicitly returned as `"purchasable": false`
  </Accordion>

  <Accordion title="Action Required">
    Update your response parsing logic to expect these default values. You should no longer assume that an omitted field implies a specific default (like false or null)
  </Accordion>
</AccordionGroup>

### 4. Correct Content-Type Headers in API Responses

<CardGroup cols={2}>
  <Card title="Before" icon="x-circle">
    `Content-Type: text/html` was often incorrectly returned for JSON responses
  </Card>

  <Card title="After" icon="check-circle">
    `Content-Type: application/json` is now accurately set for JSON responses
  </Card>
</CardGroup>

<Info>
  Ensure your client correctly interprets the `Content-Type: application/json` header for JSON responses. If your client was previously ignoring or misinterpreting this header, updates may be needed.
</Info>

### 5. Enforced Content-Type Header Requirements for Requests

The `Content-Type: application/json` header is now strictly enforced for all `PUT`, `POST`, and `PATCH` requests.

<Warning>
  **Important Note for Body-less POSTs:** Due to server implementations, this enforcement means that even `POST` requests that do not require an actual request body (e.g., certain RPC-style actions like the now-deprecated LockDomain) **will still require the `Content-Type: application/json header`**.
</Warning>

<Steps>
  <Step title="Add Headers">
    For **all** `PUT`, `POST`, and `PATCH` requests made to the name.com Core API, you must include the header: `Content-Type: application/json`
  </Step>

  <Step title="Verify Requests">
    Verify this for requests that previously worked without it, including those that don't send a JSON body
  </Step>
</Steps>

### 6. Consolidated Domain Update Functionality & Endpoint Deprecations

Several individual API endpoints for modifying domain settings have been deprecated. A new, consolidated endpoint, [UpdateDomain](/api/v1/reference/domains/update-a-domain), has been introduced to handle these actions.

<AccordionGroup>
  <Accordion title="Deprecated Endpoints">
    * [LockDomain](/api/v1/reference/domains/lock-domain)
    * [UnlockDomain](/api/v1/reference/domains/unlock-domain)
    * [EnableAutorenew](/api/v1/reference/domains/enable-autorenew)
    * [DisableAutorenew](/api/v1/reference/domains/disable-autorenew)
    * [EnableWhoisPrivacy](/api/v1/reference/domains/enable-whois-privacy)
    * [DisableWhoisPrivacy](/api/v1/reference/domains/disable-whois-privacy)
  </Accordion>

  <Accordion title="New Endpoint">
    `PATCH /v1/domains/{domainName}` (See [DomainUpdate Documentation](/api/v1/reference/domains/update-a-domain))
  </Accordion>

  <Accordion title="Action Required">
    Migrate your domain modification logic from the deprecated endpoints to the new UpdateDomain endpoint. This endpoint allows for updating domain lock status, autorenew settings, and WHOIS Privacy settings in a single call
  </Accordion>
</AccordionGroup>

## Removed Features

### SearchStream Endpoint

<Warning>
  This endpoint has been removed in the name.com Core API. We are evaluating a revised implementation for a future release.

  **Action Required:** If your application uses the SearchStream endpoint, you will need to remove this integration.
</Warning>

## New Features

### UpdateDomain Endpoint

<Card title="New Consolidated Endpoint" icon="plus">
  * **Endpoint:** `PATCH /v1/domains/{domainName}`
  * **Purpose:** Provides a consolidated and more efficient way to modify multiple domain settings such as autorenew status, WHOIS Privacy, and domain lock status
  * **Recommendation:** Utilize this new endpoint for all domain setting modifications
</Card>

## Overall Benefits & Next Steps

The name.com Core API is designed for improved usability, consistency, and future extensibility. The underlying codebase rewrite allows us to iterate faster, provide better error handling, and ensure more consistent behavior across all endpoints.

<Steps>
  <Step title="Review Documentation">
    Thoroughly review this guide and the new name.com Core API documentation
  </Step>

  <Step title="Plan Migration">
    Plan your migration from the legacy v4 API, prioritizing the changes outlined above
  </Step>

  <Step title="Test Integration">
    Test your updated integration extensively in a development or staging environment if available
  </Step>
</Steps>

<Info>
  While the legacy v4 API remains accessible during a transition period, all new development should use the name.com Core API (latest version recommended).
</Info>

We appreciate your partnership and are excited to provide you with a more robust and modern API experience. Please refer to our official documentation for complete details and contact our support channels if you have any questions during your upgrade process.
