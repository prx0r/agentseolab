> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Testing Environment

> How to use the sandbox environment for safe integration testing, plus known constraints and differences from production.

The name.com Core API provides a **sandbox (testing) environment** that mirrors production request/response shapes, so you can build and run automated integration tests without affecting real domains or incurring real charges.

This page focuses on **what’s different in sandbox** and the **common issues** teams run into when testing.

## When to use sandbox vs production

* **Sandbox** (`https://api.dev.name.com`): safe development, integration tests, trying purchase flows, and experimenting with API behavior.
* **Production** (`https://api.name.com`): real domains, real billing, and live DNS/registry behavior.

If you’re brand new to the API, start with [Getting Started](/guides/getting-started) and the [API Overview](/api/v1/overview).

## Authentication

Authentication is the same mechanism in both environments (**HTTP Basic Auth**). For full details and examples (curl `-u` vs explicit header, Base64 generation, etc.), see [Authentication](/guides/authentication).

Sandbox-specific requirements:

* Use your username with `-test` appended (example: `reseller123-test`)
* Use the API token labeled **Development/Test Environment** from account settings (`https://www.name.com/account/settings/api`)

<Info>
  In rare cases, newly generated sandbox credentials can take **up to 15 minutes** to become active. If it’s been longer than that, reach out to support at [reseller@name.com](mailto:reseller@name.com).
</Info>

## Endpoints

* **Sandbox**: `https://api.dev.name.com`
* **Production**: `https://api.name.com`

## Quick verification

Use `GET /core/v1/hello` to verify connectivity and credentials:

```bash theme={null}
curl -u your-username-test:your-sandbox-token https://api.dev.name.com/core/v1/hello
```

## What is production-like in sandbox

* **Same endpoints and JSON shapes**: request/response formats are intended to match production.
* **Same validation rules**: invalid payloads should fail the same way they would in production.
* **Same rate limits**: see [Rate Limits](/api/v1/overview#rate-limits) for current thresholds.
* **Preloaded test credit**: sandbox accounts include credit so you can exercise purchase/registration flows without real funds (see details below).

## Key constraints and differences (read before writing tests)

### 1) Domain availability and TLD behavior will differ

Sandbox uses **test data** for registry/TLD behavior. You may see differences compared to production, including:

* Availability results that don’t match production
* Claims-related responses that don’t match production (see [Claims Flow](/guides/claims-flow) and [Check Domain Claims](/api/v1/reference/domain-info/check-domain-claims))
* Pricing that differs from production (including **premium domains** and **account-level pricing**)
* Some TLDs not being available in sandbox

If your integration depends on a specific TLD or policy, design tests so they don’t assume production availability/requirements.

<Info>
  **Premium domains & pricing:** Premium classification and pricing can behave differently in sandbox. Sandbox pricing (especially premium pricing and account-specific pricing) should be treated as **non-authoritative** — validate production pricing as part of your launch readiness process.
</Info>

### 2) Sandbox and production are fully separate

Data does **not** sync between environments. A domain created in sandbox only exists in sandbox.

<Info>
  If a request returns 404 in sandbox, confirm you created that resource in sandbox first. This is a common gotcha when switching between environments.
</Info>

### 3) DNS records and nameservers can be set, but won’t resolve publicly

In sandbox, DNS-related API calls can succeed (and you can retrieve what you set), but the changes **will not become publicly queryable via DNS**.

This affects flows like:

* Managing DNS records (example: `POST /core/v1/domains/{domainName}/records`)
* Setting nameservers (example: `POST /core/v1/domains/{domainName}:setNameservers`)

What to test in sandbox:

* Your request building and validation handling
* Your persistence of returned IDs and record objects
* Your read/modify/delete flows against the API

What you should not expect in sandbox:

* Public DNS resolution reflecting your changes (e.g., `dig`, `nslookup`, browser resolution)

### 4) Webhooks work the same as production

You can create and manage webhook subscriptions via the API (for example: `POST /core/v1/notifications`). In sandbox/OT\&E webhooks are supported and intended to behave the same as production.

Recommended approach:

* Test your subscription management logic in sandbox
* Test your webhook handler with real sandbox events, and also keep a test harness (replay a captured payload, or send a synthetic payload to your endpoint) so you can validate signature checks, retries, and idempotency

### 5) Sandbox behavior can change over time

Sandbox is intended for testing and may receive updates and configuration changes that are not synchronized with your integration timeline.

<Warning>
  Do not hardcode assumptions from sandbox into production logic (for example, specific TLD requirements or edge-case behaviors). Always validate production behavior during your launch readiness process.
</Warning>

### 6) Domains cannot be deleted or reset

Domains that are **created or transferred** in sandbox **cannot be deleted** and there isn’t a “reset” mechanism for returning your sandbox account to a blank slate.

Sandbox is also designed to simulate real-world scenarios where possible. In practice, you should expect domain state to follow the standard domain lifecycle (including expiration-related flows), but registry OT\&E behavior can vary and may change over time.

Recommendations:

* Use unique test domains per test run (timestamp/UUID prefix)
* Design tests to be idempotent (safe to re-run without cleanup)

### 7) Transfers are not deterministic in sandbox

Sandbox does not support deterministic “force success/failure/auth error” transfer outcomes. If your integration includes transfers:

* Validate request/response handling and state polling in sandbox
* Perform final end-to-end verification in production as part of your launch checklist

### 8) Sandbox errors are driven by registry OT\&E behavior

In sandbox, many behaviors (and errors) are determined by the **operational test & evaluation (OT\&E)** environment of the related registry. Typically, an error you see during registration, contact updates, etc. will resemble the kinds of errors you may see in production.

However, **name.com cannot guarantee** that a registry’s sandbox/OT\&E behavior will exactly match its production behavior, and sandbox errors may not explicitly indicate when something is unsupported or simulated.

If you see an error you can’t interpret, capture the request/response and contact support at [reseller@name.com](mailto:reseller@name.com).

## Sandbox account credit behavior

Sandbox accounts are provisioned with **\$100,000 of account credit** so you can run paid workflows (registrations, renewals, privacy, etc.) without real billing.

* **Auto-refresh/reset**: The balance is regularly reset back to **\$100,000** if it has been spent down.
* **Test-only**: This credit is sandbox-only and has no real-world monetary value.
* **Running out is unlikely**: Credit is replenished regularly, so most integrations won’t need to worry about depletion.

## Suggested testing workflow

<Steps>
  <Step title="Create sandbox credentials">
    Create a **Development/Test Environment** API token and use your `-test` username. See [Authentication](/guides/authentication).
  </Step>

  <Step title="Verify connectivity">
    Call `GET /core/v1/hello` in sandbox to confirm credentials.
  </Step>

  <Step title="Register test domains before using them">
    Many domain endpoints require the domain to exist in the current environment. Register it in sandbox before calling domain/DNS endpoints.
  </Step>

  <Step title="Run integration tests with backoff">
    Respect rate limits and implement retry/backoff for `429 Too Many Requests`.
  </Step>
</Steps>

## Troubleshooting checklist (common issues)

<AccordionGroup>
  <Accordion title="401 Unauthorized in sandbox">
    Confirm you are using:

    * `https://api.dev.name.com`
    * your `-test` username
    * the **Development/Test Environment** token (not your production token)
  </Accordion>

  <Accordion title="404 Not Found for a domain or record">
    The resource must exist in the environment you’re querying. In sandbox, register/create the domain first, then retry.
  </Accordion>

  <Accordion title="DNS changes don't show up in public lookups">
    Expected: sandbox stores DNS configuration for API testing, but it does not publish DNS in a way that becomes publicly resolvable.
  </Accordion>

  <Accordion title="Webhook subscription created but no events arrive">
    Webhooks are supported in sandbox. If you’re not seeing events:

    * Verify the subscription exists and matches the event type(s) you expect
    * Confirm the action you performed actually emits the event you subscribed to
    * Check your endpoint is reachable and returns a 2xx response
    * Review your logs for signature validation or parsing failures
  </Accordion>
</AccordionGroup>

## Where to go next

<CardGroup cols={2}>
  <Card title="Official SDKs" icon="cube" href="/sdks">
    Call the sandbox from TypeScript, Go, or PHP
  </Card>

  <Card title="Getting Started" icon="rocket" href="/guides/getting-started">
    Create tokens, choose sandbox vs production, and make your first call
  </Card>

  <Card title="Authentication" icon="lock" href="/guides/authentication">
    Full Basic Auth guide (curl and header examples)
  </Card>

  <Card title="API Overview" icon="book" href="/api/v1/overview">
    Rate limits, error formats, and core API conventions
  </Card>
</CardGroup>

<Info>
  If you notice inconsistencies between this documentation and what you’re seeing in the sandbox/OT\&E environment, email us at [reseller@name.com](mailto:reseller@name.com). If possible, include the endpoint, timestamp, and a sanitized request/response sample.
</Info>
