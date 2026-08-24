> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Reseller Quickstart

> A minimal, production-ready flow to sell domains with the name.com Core API from discovery, purchase, management, and renewals.

# Reseller Quickstart MVP Flow (Search → Register → Manage)

This guide is for new domain resellers who want to **sell domains on their own site** with a complete, clean MVP from domain discovery through domain management.

<Info>
  This is a **recommended** MVP flow to get up and running quickly — not a requirement. The goal of the name.com Core API is to provide **flexibility** so you can build the domain purchase and management UX that fits your product. We encourage you to get creative, and we’d love your feedback on what would make your UX and developer experience better: [name.com API feedback](https://www.name.com/api-feedback).
</Info>

## What you’ll implement (MVP)

* **Domain purchase**: search → pre-registration checks → registration
* **Domain dashboard**: list domains + basic status
* **Domain management**: DNS records, nameservers, domain contacts, contact verification, renewals, WHOIS privacy

<Info>
  Flow stages:
  <Badge color="blue" size="sm">Discovery</Badge> <Badge color="green" size="sm">Registration</Badge> <Badge color="purple" size="sm">Management</Badge>
</Info>

## Before you start

<Info>
  The fastest way to start coding is an [official SDK](/sdks) (TypeScript, Go, or PHP — Python coming soon). They wrap the same Core API endpoints used in this guide.

  You’ll also move faster if you skim:

  * [Getting Started](/guides/getting-started)
  * [API v1 Overview](/api/v1/overview)

  Download the [OpenAPI spec](https://namedotcom-cdn.name.tools/api-info/namecom.api.yaml) if you prefer your own code generation or raw HTTP.
</Info>

<Warning>
  We recommend **not** using Google/SSO when creating a reseller account. SSO-based signup often sets your **account username to your email address**, which is not ideal for reseller/API usage.

  Pick a **generic, company-wide** username you can share across the team (e.g., `resellercompanyname`, `company-eng`, `company-dev`). This is the username you’ll use for HTTP Basic Auth, and your sandbox username will be this value with `-test` appended.
</Warning>

## Step 1: Build the search UX

<Badge color="blue" size="sm">Discovery</Badge>

**Use Search to show purchasable options + pricing**: `POST /core/v1/domains:search` → [Search](/api/v1/reference/domains/search)

Use the optional **`purchaseType` = `"registration"`** to limit Search to registration inventory and match the simple checkout path below.

**UX recommendations**

* Show **purchase price** and **renewal price** from the API result.
* Mark premium domains clearly (pricing confirmation is required at purchase time for premium domains).
* For a fast MVP, start with a curated set of TLDs: [Recommended TLDs](/guides/quickstart-recommended-tlds)

## Step 2: Pre-checks at checkout (prevents failed purchases)

<Badge color="green" size="sm">Registration</Badge>

At checkout time (right before you call [Create Domain](/api/v1/reference/domains/create-domain), which is the **billable** registration action), do these checks:

**Recommended check**

* **Use Check Availability to confirm the domain is still purchasable + capture `purchasePrice` & `purchaseType`**:
  * `POST /core/v1/domains:checkAvailability` → [Check Availability](/api/v1/reference/domains/check-availability)
  * Use the optional **`purchaseType` = `"registration"`**, same as Search, so the pre-check stays scoped to registration inventory.
  * Search results are a great UX starting point, but availability can change. This is a good safeguard if a user adds a domain to cart and waits, or it gets registered elsewhere between search and purchase. It also gives you the definitive `purchasePrice` & `purchaseType` to pass into create (required for premium domains).

<Tip>
  Not required for Quickstart, but good to add when you’re ready:

  * **TLD-specific registration requirements (often ccTLDs)**: [TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements)
  * **Claims-period domains**: [Claims Flow](/guides/claims-flow)
</Tip>

<Tip>
  **Quickstart constraint:** only support `purchaseType = registration` at first (avoid complex cases like aftermarket/pre-order flows). If `Check Availability` returns a different `purchaseType`, treat it as “not supported yet” in your UI.
</Tip>

## Step 3: Register the domain (idempotent checkout)

<Badge color="green" size="sm">Registration</Badge>

**Use Create Domain to register (billable)**: `POST /core/v1/domains` → [Create Domain](/api/v1/reference/domains/create-domain)

<Warning>
  Always send an `X-Idempotency-Key` on create so retrying a timed-out request doesn’t double-purchase.
</Warning>

**Recommended create defaults for a good MVP UX**

* `autorenewEnabled: true` (reduces churn/support)
* `locked: true` (safer default; can be toggled later). Note: new registrations are **transfer-locked for 60 days** by default, regardless.
* `privacyEnabled: true` (the system will only add privacy for TLDs that support it, even if you always pass `true`)
* `years`: most domains support purchasing **up to 10 years** at registration time (great for customers who want to lock in pricing and reduce renewal overhead). For per‑TLD limits/requirements, see [TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements).
* **Contacts (recommended for Quickstart)**: set the **reseller (you)** as the domain contacts to move fast. Our system defaults to your account level contacts on a domain create call if contact data is not passed. Using end-customer contacts is possible, but typically requires additional setup (e.g., whitelabeled contact emails) and creates more verification/support work. Contacts can be updated later using [Set Contacts](/api/v1/reference/domains/set-contacts).

## Step 4: Domain dashboard & management

<Badge color="purple" size="sm">Management</Badge>

**Use Domains + settings endpoints to power your dashboard**:

* **List domains**: `GET /core/v1/domains` → [List Domains](/api/v1/reference/domains/list-domains)
* **Domain details**: `GET /core/v1/domains/{domainName}` → [Get Domain](/api/v1/reference/domains/get-domain)
* **Autorenew / lock / WHOIS privacy toggles**: `PATCH /core/v1/domains/{domainName}` → [Update a domain](/api/v1/reference/domains/update-a-domain)
* **Update contacts**: `POST /core/v1/domains/{domainName}:setContacts` → [Set Contacts](/api/v1/reference/domains/set-contacts)
* **Renew domain anytime**: `POST /core/v1/domains/{domainName}:renew` → [Renew Domain](/api/v1/reference/domains/renew-domain)
* **Purchase/extend WHOIS privacy**: `POST /core/v1/domains/{domainName}:purchasePrivacy` → [Purchase Privacy](/api/v1/reference/domains/purchase-privacy)

Show these fields prominently:

* domain name, expiration date, autorenew on/off, privacy on/off, lock state
* DNS Settings (see Step 5)
* contact verification status (below)

### Contact verification status

**Use Unverified Contacts to surface verification requirements**:

* `GET /core/v1/contacts/unverified` → [List Unverified Contacts](/api/v1/reference/contact-verification/list-unverified-contacts)

<Info>
  After a new domain registration or contact change, unverified contacts may take up to \~10 minutes to appear in the API. Build your UI accordingly.
</Info>

<Warning>
  If contacts aren’t verified within 15 days, verification locks can apply and the domain may stop resolving. See [Understanding Domain Locks](/guides/domain-locks).
</Warning>

<Tip>
  Optional: some reseller accounts are approved to verify contacts via API; most are not. If you need this, contact [API Support](https://www.name.com/support/api) and see: [Verify Contact](/api/v1/reference/contact-verification/verify-contact)
</Tip>

<Tip>
  If you send your own verification emails (or need resend/webhook details), see the [Contact Verification Compliance Guide](/guides/contact-verification).
</Tip>

## Step 5: DNS & nameservers

<Badge color="purple" size="sm">Management</Badge>

**Use DNS records (and optionally nameservers) to connect the domain**:

* **List records**: `GET /core/v1/domains/{domainName}/records` → [List Records](/api/v1/reference/dns/list-records)
* **Create record**: `POST /core/v1/domains/{domainName}/records` → [Create Record](/api/v1/reference/dns/create-record)
* **Get record**: `GET /core/v1/domains/{domainName}/records/{id}` → [Get Record](/api/v1/reference/dns/get-record)
* **Update record**: `PUT /core/v1/domains/{domainName}/records/{id}` → [Update Record](/api/v1/reference/dns/update-record)
* **Delete record**: `DELETE /core/v1/domains/{domainName}/records/{id}` → [Delete Record](/api/v1/reference/dns/delete-record)

Many resellers request default nameservers up front. If you want customers to use external DNS (or switch away from the default DNS), also include:

* **Set nameservers**: `POST /core/v1/domains/{domainName}:setNameservers` → [Set Nameservers](/api/v1/reference/domains/set-nameservers)

## MVP “no holes” checklist

If you ship this MVP, your customers can:

* **Search** for a domain and see a real price ([Search](/api/v1/reference/domains/search))
* **Checkout** without failed purchases due to proper handling of extra requirements, premiums, and claims gaps ([Check Availability](/api/v1/reference/domains/check-availability), [TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements), [Claims Flow](/guides/claims-flow))
* **Register** safely with retries ([Create Domain](/api/v1/reference/domains/create-domain))
* **Manage domain settings** (DNS records + nameservers, lock status, autorenew, WHOIS privacy)
* **Manage domain contacts** and see verification status (prevents domain outages)
* **Renew** domains and WHOIS privacy

## Recommended next steps (post-MVP)

Keep these out of MVP unless you need them, but they’re high-impact upgrades:

<CardGroup cols={2}>
  <Card title="Webhooks + HMAC verification" icon="bell" href="/guides/hmac-examples">
    Push status changes into your app instead of polling; verify webhook authenticity.
  </Card>

  <Card title="Transfers (bring your domain)" icon="arrow-right" href="/api/v1/reference/transfers/create-transfer">
    Add inbound transfers for users migrating domains to you.
  </Card>

  <Card title="Advanced DNS: DNSSEC + Vanity Nameservers" icon="shield" href="/api/v1/reference/dnssecs/list-dnssecs">
    Add DNSSEC and/or branded nameservers for advanced customers.
  </Card>

  <Card title="Orders & reconciliation" icon="receipt" href="/api/v1/reference/orders/list-orders">
    Build admin tooling for reporting, reconciliation, and customer support workflows.
  </Card>
</CardGroup>

## Need help?

<Card title="API support" icon="life-ring" href="https://www.name.com/support/api">
  Share your request/response details with our team to troubleshoot your integration.
</Card>

## Common pitfalls

<Warning>
  **Do not URL-encode the `:`** in endpoints like `POST /core/v1/domains:search` and `POST /core/v1/domains:checkAvailability`. Some clients encode `:` → `%3A` which will fail. See [API v1 Overview](/api/v1/overview).
</Warning>
