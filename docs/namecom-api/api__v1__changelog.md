> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Changelog

> name.com CORE API updates and announcements

<Update label="August 17, 2026" description="Docs" tags={["Changed"]}>
  ### Changed

  * **Idempotency key lifetime**: Documented that `X-Idempotency-Key` caches are valid for **1 hour** (previously misstated as 12 hours). API behavior is unchanged.
</Update>

<Update label="August 14, 2026" description="Core 1.33.1" tags={["Fixed"]}>
  ### Fixed

  * POST endpoints that take no fields (for example `enableAutorenew`, `lockDomain`, `cancelTransfer`, `verifyContact`) now document an empty JSON body (`{}`) instead of a `Content-Type` header parameter. API behavior is unchanged: these requests still require `Content-Type: application/json`, and an empty body has always been accepted.
</Update>

<Update label="August 11, 2026" description="Core 1.33.0" tags={["Added"]}>
  ### Added

  * Documented `503 Service Unavailable` on all endpoints for scheduled maintenance windows. See [status.name.com](https://status.name.com) for maintenance updates.
</Update>

<Update label="August 4, 2026" description="Core 1.32.0" tags={["Added"]}>
  ### Added

  * Added new webhook: `account.domain.removal` which fires when a domain is removed from the subscriber's account. See [Account Domain Removal](/api/v1/reference/webhook-notifications/account-domain-removal).
</Update>

<Update label="July 31, 2026" description="Core 1.31.2" tags={["Changed"]}>
  ### Changed

  * **`domain.transfer_out.status_change` (`canceled`)**: Now fires whenever an outbound transfer is no longer pending at the registry. See [Domain Transfer Out Status Change](/api/v1/reference/webhook-notifications/domain-transfer-out-status-change).
</Update>

<Update label="July 21, 2026" description="Core 1.31.1" tags={["Changed"]}>
  ### Changed

  * **List Endpoints**: Tightened the spec to match API behavior for paginated lists — documented the `page` minimum of `1` and added `400 Bad Request` responses on the remaining list operations.
  * **OpenAPI spec**: Documented existing constraints on a few endpoints (`years` bounds on Get Pricing, non-empty `tlds` on TLD Price List, and a `404` on Download Premium Domain Lists). No intended changes to API behavior.
</Update>

<Update label="July 16, 2026" description="Core 1.31.0" tags={["Added"]}>
  ### Added

  * Added new webhook: `domain.expiration` which fires when a domain expires and enters the post-expiry grace period. Payloads include `eventName`, `domainName`, and `expirationDate`. See [Domain Expiration](/api/v1/reference/webhook-notifications/domain-expiration).
</Update>

<Update label="July 15, 2026" description="Core 1.30.0" tags={["Added"]}>
  ### Added

  * Added new webhook: `domain.transfer.internal_out` which fires when a **name.com** domain is transferred **out of** a subscriber's account. See [Internal Transfer Out Status Change](/api/v1/reference/webhook-notifications/domain-transfer-internal-out-status-change).
</Update>

<Update label="July 10, 2026" description="Core 1.29.4" tags={["Changed"]}>
  ### Changed

  * **List Records** (`GET /core/v1/domains/{domainName}/records`): Documented `400 Bad Request` for invalid request parameters. See [List Records](/api/v1/reference/dns/list-records).
  * **List Endpoints**: Cleaned up validation for invalid pagination params.
</Update>

<Update label="July 8, 2026" description="Core 1.29.3" tags={["Changed"]}>
  ### Changed

  * **OpenAPI spec**: Documentation updates for DNSSEC and URL Forwarding endpoints. No intended changes to API behavior.
</Update>

<Update label="July 6, 2026" description="Core 1.29.2" tags={["Added", "Changed"]}>
  ### Added

  * **Create Domain** (`POST /core/v1/domains`): Per-account-per-domain registration rate limiting for TLDs served by selected registry connections. Throttling is enforced before registry availability checks are dispatched. Additional registry connections may be added to this policy over time without API contract changes. See [Create Domain](/api/v1/reference/domains/create-domain).

  ### Changed

  * **Rate Limits** ([API Overview](/api/v1/overview#rate-limits)): Documented the new domain registration rate limit in addition to existing account-wide limits (20 req/s, 3,000 req/hour). Clarified that the limit applies per account and per domain name, returns `429 Too Many Requests` with a `Retry-After` header and a distinct error message from the account-wide rate limit, and that other account–domain pairs are unaffected. Integrations should honor `Retry-After` and use retry/backoff.
</Update>

<Update label="July 2, 2026" description="Core 1.29.1" tags={["Changed"]}>
  ### Changed

  * **Create vanity nameserver** (`POST /core/v1/domains/{domainName}/vanity_nameservers`): Documented `409 Conflict` when a vanity nameserver with the same hostname already exists for the domain. See [Create Vanity Nameserver](/api/v1/reference/vanity-nameservers/create-vanity-nameserver).
</Update>

<Update label="July 1, 2026" description="Core 1.29.0" tags={["Added"]}>
  ### Added

  * **Domain object**: Added optional read-only field `transferLockExpiresAt` (ISO 8601 UTC) on single-domain responses. When present, an active ICANN-mandated transfer lock (new registration, transfer-in, or material registrant contact change) blocks client unlock via the API until this time. When omitted, there is no active policy transfer lock with a known expiry — the domain may still be `locked: true` due to a voluntary user lock or other reasons. Returned by [Get Domain](/api/v1/reference/domains/get-domain) and other single-domain operations (create domain, set contacts, update domain, lock/unlock, internal transfer-in, etc.). Not returned on [List Domains](/api/v1/reference/domains/list-domains).
</Update>

<Update label="June 15, 2026" description="Core 1.28.0" tags={["Added", "Changed"]}>
  ### Added

  * **TLD requirements (`tldInfo`)**: Added `requireIdnSld` on `tldInfo`. When `true`, ASCII/Latin SLDs are not valid for registration.

  ### Changed

  * **Pagination (`perPage`)**: List endpoints now enforce a maximum of **1,000** records per request when `perPage` is explicitly set. When omitted, endpoint-specific defaults apply:
    * **250** — `GET /core/v1/domains`
    * **100** — `GET /core/v1/contacts/unverified`
    * **500** — `GET /core/v1/orders`, `GET /core/v1/transfers`, `GET /core/v1/domains/{domainName}/records`, `GET /core/v1/domains/{domainName}/email/forwarding`, `GET /core/v1/domains/{domainName}/url/forwarding`, `GET /core/v1/urlforwarding/{domainName}`, `GET /core/v1/domains/{domainName}/vanity_nameservers`
    * **25** — `GET /core/v1/tldpricing`
  * **OpenAPI spec**: Cleaned up some language in the spec to make pricing documentation clearer and more concise. No intended changes to API behavior.
</Update>

<Update label="June 3, 2026" description="Core 1.27.1" tags={["Changed"]}>
  ### Changed

  * **Internal transfer in** (`POST /core/v1/transfers/internal/in`): `contacts` previously required all four roles or none; omitted roles now use the gaining account's default contacts. See [Create Internal Transfer In](/api/v1/reference/transfers/create-internal-transfer-in).
</Update>

<Update label="June 2, 2026" description="Core 1.27.0" tags={["Added"]}>
  ### Added

  * **Transfer eligibility**: New `GET /core/v1/transfers/eligibility/{domainName}` endpoint for checking whether a domain is currently registered at name.com and whether its TLD supports internal transfer between name.com accounts. Useful for routing transfer-in flows to either [Create External Transfer In](/api/v1/reference/transfers/create-transfer) or [Create Internal Transfer In](/api/v1/reference/transfers/create-internal-transfer-in) without an RDAP lookup. See [Check Transfer Eligibility](/api/v1/reference/transfers/get-transfer-eligibility).
</Update>

<Update label="May 19, 2026" description="Core 1.26.0" tags={["Changed"]}>
  ### Changed

  * **OpenAPI spec**: Cleaned up mismatched numeric types in the published schema (e.g. integer fields that were incorrectly typed as `number`). No intended changes to API behavior.
</Update>

<Update label="May 5, 2026" description="Core 1.25.0" tags={["Added"]}>
  ### Added

  New optional request parameter filter **`purchaseType`** was added to below endpoints. Omit to return all types. Recommended setting is **`registration`** for standard reseller flows.

  * **Check Availability** — `POST /core/v1/domains:checkAvailability` → [Check Availability](/api/v1/reference/domains/check-availability)
  * **Search** — `POST /core/v1/domains:search` → [Search](/api/v1/reference/domains/search)
</Update>

<Update label="April 29, 2026" description="Core 1.24.1" tags={["Added"]}>
  ### Added

  * **TLD requirements (`tldInfo`)**: `GET /core/v1/domaininfo/requirements/{tld}` and `GET /core/v1/domaininfo/requirementsV2/{tld}` now include `supportsInternalTransfer` on `tldInfo`—whether the TLD supports internal transfer between reseller accounts. See [Get Specific TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements) and [Get Specific TLD Requirements (JSON Schema)](/api/v1/reference/domain-info/get-specific-tld-requirements-v2). Use these in conjunction with [Create Internal Transfer In](/api/v1/reference/transfers/create-internal-transfer-in): resolve the TLD first and confirm `supportsInternalTransfer` before calling `POST /core/v1/transfers/internal/in`.
</Update>

<Update label="April 28, 2026" description="Core 1.24.0" tags={["Added"]}>
  ### Added

  * **Internal transfer in**: New `POST /core/v1/transfers/internal/in` endpoint to pull a domain from another name.com account into the authenticated reseller account using `domainName` and `authCode`. The losing account must unlock the domain and supply the authorization code from the name.com dashboard. Restricted to approved enterprise resellers.  See [Create Internal Transfer In](/api/v1/reference/transfers/create-internal-transfer-in).
</Update>

<Update label="April 22, 2026" description="Core 1.23.2" tags={["Changed"]}>
  ### Fixed

  * **Error response coverage**: Added missing documented error responses on affected operations, including `404 Not Found` and `400 Bad Request`, so endpoint contracts align with observed API behavior.
  * **Content-Type enforcement in spec**: `415 Unsupported Media Type` is now applied consistently for `POST`, `PUT`, and `PATCH` operations.
  * **Request schema validation**: Tightened domain list item validation in request bodies for availability/zone-check style endpoints to better reflect server-side rejection of empty domain entries.
  * **getDomain**: `locks` array now returns all registry locking statuses, including `clientHold`. `lock` value still refers specifically to **transfer lock** status.
</Update>

<Update label="April 15, 2026" description="Core 1.23.1" tags={["Changed"]}>
  ### Changed

  * **Webhook HMAC (`X-NAMECOM-SIGNATURE`)**: When an account has multiple API v4 tokens, outbound webhook signatures now use the token with the lowest id. Previously, there was no explicit rule leading to signature mismatches for accounts with multiple tokens.
</Update>

<Update label="April 15, 2026" description="Core 1.23.0" tags={["Added"]}>
  ### Added

  * **Domain Registry Rejection webhook** (`domain.registry.rejection`): New webhook for resellers subscribed to this event. Some registries complete domain **create** asynchronously; when such a request ultimately fails after initial acceptance, this notification is delivered. Successful creates do not emit this event. See [Domain Registry Rejection](/api/v1/reference/webhook-notifications/domain-registry-rejection).
</Update>

<Update label="April 3, 2026" description="Core 1.22.1" tags={["Changed"]}>
  ### Changed

  * **Error Responses**:  Added `400` (Bad Request) to `POST core/v1/domains/{domainName}/records` with improved answer input validation.
</Update>

<Update label="March 24, 2026" description="Core 1.22.0" tags={["Added"]}>
  ### Added

  * **Cancel outbound transfer**: New `POST /core/v1/transfers/external/out/{domainName}:cancel` endpoint. Cancels a transfer out of name.com before the transfer completes, when the registrant or reseller requests it. The domain must belong to the authenticated account and be in a cancelable pending transfer-out state. Response returns the domain name and updated transfer-out status.
</Update>

<Update label="March 18, 2026" description="Core 1.21.0" tags={["Added", "Changed"]}>
  ### Added

  * **Contact object**: Unverified contacts returned by the GetDomain `GET /core/v1/domains/{domainName}` response will include the numeric verificationId if it exists (Unverified contacts should have an id if they are pending.)

  ### Changed

  * **Domain Transfer Out Status Change webhook** (`domain.transfer_out.status_change`): The webhook now fires for additional statuses. In addition to `completed`, the `status` field may now be `initiated` (transfer out was started) or `canceled` (transfer out was canceled before completion). Subscribers should handle all three status values.
</Update>

<Update label="February 25, 2026" description="Core 1.20.0" tags={["Added", "Changed"]}>
  ### Added

  * **Domain object**: Added `locks` array to the Domain response. Lists the lock types currently applied to the domain (e.g. `RegistrarLock`, `ClientHold`, `ExpirationClientHold`), so you can see whether and how a domain is locked. Returned by **List Domains** (`GET /core/v1/domains`) and **Get Domain** (`GET /core/v1/domains/{domainName}`). When no locks are applied, `locks` is an empty array.
  * **URL Forwarding by ID**: New endpoints so you can list, get, update, and delete URL Forwarding records by server-assigned ID. Create still uses `POST /core/v1/domains/{domainName}/url/forwarding`.
    * **List**: `GET /core/v1/urlforwarding/{domainName}` — returns all URL Forwarding entries for the domain. Each entry includes an `id` for use with the by-ID endpoints.
    * **Get**: `GET /core/v1/urlforwarding/{domainName}/{id}` — fetch a single record by ID.
    * **Update**: `PATCH /core/v1/urlforwarding/{domainName}/{id}` — update a single record by ID.
    * **Delete**: `DELETE /core/v1/urlforwarding/{domainName}/{id}` — delete a single record by ID.
  * **URL Forwarding response**: Added `id` (integer) to the URL Forwarding entry response. Returned in list and single-record responses so you can use the by-ID endpoints.
  * **Error Responses**: Added `502` (Bad Gateway) and `504` (Gateway Timeout) response codes to all endpoints.
    * **Retry Policy**: `502` errors are safe for immediate exponential backoff, while `504` errors should be preceded by a status `/core/v1/hello` check to avoid duplicate operations.

  ### Changed

  * **URL Forwarding (host-based)**: The following operations are now **deprecated**: **List** (`GET /core/v1/domains/{domainName}/url/forwarding`), **Get** (`GET /core/v1/domains/{domainName}/url/forwarding/{host}`), **Update** (`PUT /core/v1/domains/{domainName}/url/forwarding/{host}`), **Delete** (`DELETE /core/v1/domains/{domainName}/url/forwarding/{host}`). **Create** (`POST /core/v1/domains/{domainName}/url/forwarding`) is unchanged and not deprecated.
</Update>

<Update label="February 17, 2026" description="Core 1.19.0" tags={["Added"]}>
  ### Added

  * Added new webhook: `domain.transfer.internal_in` which fires when a **name.com** domain is transferred **to** a subscriber's account.
  * **Check Availability**: Added optional string response property `reason` to the Search result object. When present, it provides additional context (e.g. why a domain is not purchasable).
</Update>

<Update label="February 11, 2026" description="Core 1.18.1" tags={["Fixed"]}>
  ### Fixed

  * Added missing error codes `401` `403` `405` `429` and `500` response codes to all API response objects.
</Update>

<Update label="February 10, 2026" description="Core 1.18.0" tags={["Added"]}>
  ### Added

  * **Create Domain**: Added optional `promoCode` parameter to `POST /core/v1/domains` endpoint. Valid promotional codes can be applied to domain purchases to receive discounts. Only one promo code can be applied per request.
</Update>

<Update label="January 27, 2026" description="Core 1.17.0" tags={["Added", "Changed", "Fixed"]}>
  ### Added

  **Contact Verification**:

  * Added new webhook: `contact.verification.status_change` that fires when a contact verification status changes.
  * Added `POST /core/v1/contacts/verify/{verificationId}:resend` endpoint to resend the verification email for a pending verification record.

  ### Changed

  * **Blocked TLD Filtering**: API endpoints now reject or filter out all .in TLDs (including co.in, firm.in, gen.in, ind.in, net.in, org.in) as these are not supported in the Reseller API. API requests using unsupported TLDs will return `422 Unprocessable Entity` errors or be excluded from results.

  ### Fixed

  * **Requirements**: Both original and V2 Requirements endpoints now return `422 Unprocessable Entity` when blocked or unsupported tlds are requested instead of `500 Internal Server Error`.
</Update>

<Update label="January 21, 2026" description="Core 1.16.2" tags={["Changed"]}>
  ### Changed

  * No functional changes. Schema updates to ensure no broken URLs between docs pages due to doumentation restructuring.
</Update>

<Update label="January 20, 2026" description="Core 1.16.1" tags={["Changed"]}>
  ### Fixed

  * Transfer-ins with a rejected status can now be cancelled.

  ### Changed

  * **Transfer Status**: Clarified that `failed` and `rejected` statuses will not be retried. Improved transfer status information for endpoints & webhooks.
</Update>

<Update label="January 20, 2026" description="Core 1.16.0" tags={["Added"]}>
  ### Added

  * **Domain Info v2 API**: New `GET /core/v1/domaininfo/requirementsV2/{tld}` endpoint that returns TLD registration requirements in JSON Schema Draft-07 format.
    * **Automatic Form Generation**: The JSON Schema Draft-07 format enables direct integration with form generation libraries (e.g., react-jsonschema-form, jsonforms, Form.io), allowing developers to automatically generate dynamic registration forms without manual schema parsing or custom form logic.
    * **Conditional Validation**: The schema uses `if/then/else` structures to express complex conditional requirements (e.g., "if entity type is X, then require field Y"), making it easier to understand and implement TLD-specific registration rules that vary based on user selections.
    * **Standardized Validation**: JSON Schema Draft-07 is a widely-supported standard, enabling developers to leverage existing validation libraries and tooling instead of building custom validation logic for each TLD's unique requirements.
    * **Structured Data**: The schema clearly separates TLD information (`tldInfo`), contact requirements (`contacts`), and TLD-specific fields (`tldRequirements`), providing a consistent structure that simplifies form rendering and data collection workflows.
</Update>

<Update label="January 16, 2026" description="Core 1.15.2" tags={["Fixed"]}>
  ### Fixed

  **Get Order** The Get Order API was incorrectly returning the response object wrapped in an extraneous `order` object. This has been fixed, and the response now matches the specification.
</Update>

<Update label="January 13, 2026" description="Core 1.15.0" tags={["Added", "Fixed"]}>
  ### Added

  * **Refunds Endpoint**: New `POST /core/v1/refund` endpoint to delete eligible domains and privacy products during the Add Grace Period (AGP) and automatically issue refunds for the associated order items.
    * Accepts `orderId` and `orderItemIds` array in the request body
    * Supports `registration` and `whois_privacy` product types only
    * Includes idempotency support via `X-Idempotency-Key` header for safe request retries
    * Returns detailed refund results including individual item status and total refund amount
    * Refunds are issued to the original payment method on file, with fallback to account credit
  * **OrderItem `isRefundable` Property**: New boolean field on `OrderItem` indicating whether the item is currently eligible for refund through the Refunds endpoint based on name.com's refund rules.
  * **List Orders Endpoint**: Updated request has new optional filters to narrow response by domainName, tld, createDate, type and orderStatus.

  ### Fixed

  * **Purchase Privacy**: Now returns `409 Conflict` when privacy protection already exists on a domain instead of `500 Internal Server Error`.
</Update>

<Update label="December 11, 2025" description="Core 1.14.0" tags={["Added", "Changed"]}>
  ### Added

  * **Domain Transfer Out Status Change Webhook**: New `domain.transfer_out.status_change` webhook that fires when a domain transfer out from name.com to another registrar has completed and the domain has been removed from the account.

  ### Changed

  * **Domain Transfer Status Change Webhook**: Clarified that `domain.transfer.status_change` represents transfer IN to name.com (where name.com is the gaining registrar), and updated webhook descriptions to reflect this.
</Update>

<Update label="November 25, 2025" description="Core 1.13.0" tags={["Added", "Changed", "Fixed"]}>
  ### Added

  * **TLD Pricing Response Enhancement**: The TLD Price List endpoint now includes retail pricing information in addition to account-level pricing, which applies to registration, renewal, domain restoration, and transfer purchase types. Each pricing entry now provides three price tiers:
    * Account-level price (includes account discounts)
    * Retail price (includes rebates/promotions/sales, but no account discounts)
    * Original/MSRP price (before any discounts)

  ### Changed

  * **Contact Schema Validation**: Contact schemas have been refactored to separate validation requirements between request and response operations:
    * **GET Operations (Responses)**: The `Contact` and `RegistrantContact` schemas used in API responses now allow nullable fields to accommodate legacy data that may contain null or empty values. This ensures GET operations can successfully return domains with legacy contact information without validation errors.
    * **POST/PUT Operations (Requests)**: The `ContactRequest` and `RegistrantContactRequest` schemas used for creating and updating contacts enforce all validation requirements including:
      * Required fields (firstName, lastName, address1, city, state, zip, country, email, phone)
      * Minimum length constraints (minLength: 1)
      * Format validation (email format, phone/fax E.164 pattern, country code pattern)
    * This separation ensures that while GET operations can handle legacy data gracefully, all contact creation and update operations continue to enforce proper data validation and formatting requirements.

  ### Fixed

  * **Get Domain Pricing**: Fixed validation order in `getPricingForDomain` endpoint to check TLD support before year validation. Unsupported TLDs now return `422 Unprocessable Entity` with the message "TLD not supported" instead of `400 Bad Request` with a misleading "Invalid value for years for this domain" message.
  * **Create Domain**: Added TLD privacy support check before adding WhoIs Privacy to orders. Privacy is only added when the TLD supports it, preventing failed order items for unsupported TLDs.
  * **Purchase Privacy**: Added TLD privacy support validation. Returns `422 Unprocessable Entity` with message "TLD does not support WhoIs Privacy" when attempting to purchase privacy for unsupported TLDs.
</Update>

<Update label="November 21, 2025" description="Core 1.12.2" tags={["Changed"]}>
  ### Changed

  * Cancel Transfer endpoint now returns a 409 conflict if an existing transfer is in a state that cannot be canceled.
</Update>

<Update label="November 20, 2025" description="Core 1.12.1" tags={["Fixed"]}>
  ### Fixed

  * A handful of new contact schemas were missing updates to separate Request vs Response. This has been fixed.
</Update>

<Update label="November 18, 2025" description="Core 1.12.0" tags={["Added", "Fixed"]}>
  ### Added

  * Create Transfer: Added `504 Gateway Timeout` response when domain status cannot be retrieved due to blocked-hostname.
  * Create Transfer: Added optional `warnings` object to `CreateTransferResponse` with `message` and `statuses` to surface non-blocking registry status advisories.
  * Domain Lock Status Change Webhook: Added `ExpirationClientHold` to the `lockType` enum. This lock type is applied to expired domains of configured API Reseller accounts.

  ### Fixed

  * Create Transfer: Fixed issue where a `400 Bad Request` was returned for Insufficient Funds instead of the correct `402 Payment Required` status.
  * Get Domain: Fixed intermittent `500 Server Error` caused by legacy contact data by updating API definitions to allow legacy contacts to be returned while still enforcing correct formatting in requests.
</Update>

<Update label="November 6, 2025" description="Core 1.11.0" tags={["Added", "Changed"]}>
  ### Added

  * Domain Claims Period Support: Register domains during trademark claims period.
  * New endpoint: `GET /core/v1/domaininfo/claims/{domain}` returns claim identifiers and validity dates.

  ### Changed

  * TLD Requirements: `GET /core/v1/domaininfo/requirements/{tld}` now returns `claimsCheckRequired`.
  * Domain Create: `POST /core/v1/domains` now accepts optional `claims` object (`claimId`, `notBefore`, `notAfter`) when required by the TLD.
</Update>

<Update label="October 28, 2025" description="Core 1.10.0" tags={["Added", "Changed"]}>
  ### Added

  * List Domains: New `includeRenewalPrice` query parameter.
    * `true` (default) includes renewal pricing in responses.
    * `false` omits renewal pricing for better performance.

  ### Changed

  * `renewalPrice` field is optional when `includeRenewalPrice=false`.
  * Default pagination for List Domains changed from 1000 to 250.
  * Removed access restriction on `GET /core/v1/contacts/unverified` (now available to all reseller accounts).
  * `.at` TLD requirement now enforces data acknowledgement.
</Update>

<Update label="October 27, 2025" description="Core 1.9.3" tags={["Fixed"]}>
  ### Fixed

  * Create Transfer: Block transfers for domains registered less than 60 days; returns `409 Conflict` with clear `message` and `details`.
</Update>

<Update label="October 15, 2025" description="Core 1.9.1" tags={["Changed"]}>
  ### Changed

  * Webhook documentation: standardized response code capitalization from `4xx/5xx` to `4XX/5XX`.
</Update>

<Update label="October 14, 2025" description="Core 1.9.0" tags={["Added", "Fixed"]}>
  ### Added

  * `Get Specific TLD Requirements`: Added `registryOperator` parameter.
  * Webhook HMAC Header Documentation: `X-NAMECOM-SIGNATURE` now shown on all webhook endpoints.

  ### Fixed

  * Request validation now enforces required fields as described in the API documentation.
</Update>

<Update label="October 10, 2025" description="Core 1.8.2" tags={["Fixed"]}>
  ### Fixed

  * Create Domain: Now correctly honors `privacyEnabled=false` instead of overriding with account default when provided.
</Update>

<Update label="October 7, 2025" description="Core 1.8.1" tags={["Fixed"]}>
  ### Fixed

  * Get Specific TLD Requirements: Clarified that punycode is expected (not URL-encoded params).
</Update>

<Update label="October 2, 2025" description="Core 1.8.0" tags={["Added", "Fixed"]}>
  ### Added

  * Contact model: Added verification status fields.
  * Create Domain: Returns `451 Unavailable for Legal Reasons` where restricted by law.
  * Create Domain: Returns detailed validation errors for contact creation failures.
  * Webhooks: All webhooks now send `X-NAMECOM-SIGNATURE` to verify authenticity.

  ### Fixed

  * Contact Verification List: Corrected `createDate` and `verifyBy` values for some contacts.
</Update>

<Update label="September 25, 2025" description="Core 1.7.0" tags={["Added"]}>
  ### Added

  * New webhook: `domain.lock.status_change` with `registryStatuses` in payload.
  * New contact verification APIs:
    * List Unverified Contacts
    * Verify Contact (account-restricted)
</Update>

<Update label="September 24, 2025" description="Core 1.6.0" tags={["Changed"]}>
  ### Changed

  * TLD Pricing: Clarified that null pricing indicates unavailability for specific TLD/duration combinations.
  * DNS Record Update: Duplicate record DB errors now return `409 Conflict` instead of a generic server error.
</Update>

<Update label="September 23, 2025" description="Core 1.5.2" tags={["Added"]}>
  ### Added

  * Domain Info: New capabilities returned per TLD:
    * `supportsPrivacy`
    * `requiresPreDelegation`
</Update>

<Update label="September 23, 2025" description="Core 1.5.1" tags={["Added"]}>
  ### Added

  * Get Specific TLD Requirements: Added `hsts`, `minDomainLength`, `minIdnDomainLength`.
  * Subscribe to Notifications: Documented `409 Conflict` response when already subscribed.
  * Zone Check API: Documented existing error responses.
</Update>

<Update label="September 15, 2025" description="Core 1.5.0" tags={["Added"]}>
  ### Added

  * Download Premium Domain Lists: New account-restricted API endpoint to download premium domain lists.
</Update>

<Update label="September 12, 2025" description="Core 1.4.1" tags={["Added", "Changed", "Fixed"]}>
  ### Added

  * Transfers: `GET /transfers` and `GET /transfers/{id}` now include a full list of possible transfer statuses.

  ### Changed

  * Transfers: Status field standardized to snake\_case; aligned with Domain Transfer Status Change webhook.

  ### Fixed

  * Create Domain: Now honors account setting for Automatic Advanced Security for new purchases.
</Update>

<Update label="September 10, 2025" description="Core 1.4.0" tags={["Changed"]}>
  ### Changed

  * Domain Get Pricing: When a pricing category is not available, `purchasePrice`, `renewalPrice`, and `transferPrice` return `null` instead of a `422`.
</Update>

<Update label="September 8, 2025" description="Core 1.3.2" tags={["Fixed", "Changed"]}>
  ### Fixed

  * Create Transfer: Supports multiple concurrent transfer requests; `429` now used solely for rate limiting scenarios.
  * Pricing error handling: Added `422 Unprocessable Entity` for temporary pricing unavailability across:
    * Domain Create
    * Domain Renew
    * Domain Get Pricing
  * Domain Get Pricing: Added missing `400 Bad Request` documentation for invalid parameters/malformed requests.

  ### Changed

  * Error Response Consistency: More descriptive pricing-related error details across domain endpoints.
</Update>

<Update label="August 25, 2025" description="Core 1.3.1" tags={["Fixed"]}>
  ### Fixed

  * createDomain: Returns `400 Bad Request` (not `403 Forbidden`) for missing/invalid registration requirements.
</Update>

<Update label="August 7, 2025" description="Core 1.3.0" tags={["Added", "Fixed", "Changed"]}>
  ### Added

  * Zone Check API: Fast availability checks via cached zone file data.
  * Idempotency: Support for `X-Idempotency-Key` on Create Domain and Purchase Privacy.
    * Replayed requests respond with header `X-Idempotent-Replay: 1`.
  * Domain Create docs: Improved examples including IDN domain creation.

  ### Fixed

  * TLD Pricing API: Ensured required fields are always present in responses.
  * Check Availability: Returns `422 Unprocessable Entity` when all domains have unsupported TLDs (replacing malformed dual-object JSON).

  ### Changed

  * Check Availability: Implementation optimized for speed; no behavioral changes.
  * Organization field docs updated due to ICANN policy changes.
  * `429 Rate Limited` response in OpenAPI now indicates `message` is optional.
</Update>

<Update label="July 25, 2025" description="Core 1.2.2" tags={["Changed"]}>
  ### Changed

  * TLD Pricing API:
    * Enforced `duration` parameter validation.
    * Filter invalid/unsupported `tlds`; if list becomes empty after filtering, return `400 Bad Request`.
</Update>

<Update label="July 23, 2025" description="Core 1.2.1" tags={["Fixed"]}>
  ### Fixed

  * Domain Info: Return empty objects `{}` instead of empty arrays `[]` for relevant parameters.
</Update>

<Update label="July 18, 2025" description="Core 1.2.0" tags={["Added", "Changed"]}>
  ### Added

  * TLD Pricing API: View general price list with account-level pricing.

  ### Changed

  * Response Schemas: Clarified which parameters are `required` and always present in responses.
</Update>

<Update label="July 14, 2025" description="Core 1.1.0" tags={["Added", "Changed"]}>
  ### Added

  * Domain Info API: Returns general TLD info and any additional registration requirements; formatted for dynamic form generation.

  ### Changed

  * OpenAPI: Adjusted several descriptions to use v3.0-compatible structures (no functional changes).
  * Webhook docs: DomainTransferStatusChange updated with list of triggering statuses.
</Update>

<Update label="June 24, 2025" description="Core 1.0.4" tags={["Fixed"]}>
  ### Fixed

  * List Domains: Optional filters no longer cause `500 Internal Server Error` or incorrect result sets; filters are applied reliably.
</Update>

<Update label="June 17, 2025" description="Core 1.0.3" tags={["Fixed"]}>
  ### Fixed

  * Create Domain: Missing required contact phone number returns `400 Bad Request` instead of `500`.
  * Validation Enforcement:
    * Contact `phone` and `fax` fields strictly validate E.164 format (`^\+[1-9]\d{7,14}$`); examples updated.
    * All email fields validated per RFC 822 `addr-spec` (with common practical exceptions).
    * Appropriate enums added; empty strings rejected for fields like `first_name`.
</Update>

<Update label="June 10, 2025" description="Core 1.0.2" tags={["Fixed"]}>
  ### Fixed

  * Authentication failures return `401 Unauthorized` instead of `500`.
  * Pagination: `perPage=0` now defaults to `perPage=1000` instead of returning `500`.
</Update>

<Update label="June 4, 2025" description="Core 1.0.1" tags={["Fixed"]}>
  ### Fixed

  * Create Transfer: Intermittent `500` replaced with `409 Conflict` when a transfer is already in process.
    * Message: `A transfer is already processing for this domain`.
</Update>

<Update label="May 12, 2025" description="v4 → Core 1.0.0" tags={["Changed", "Removed", "Added"]}>
  name.com is launching a new Core API — a modern, RESTful API for managing domains, DNS records, and related services. It is the successor to the legacy v4 API.

  ### Changed

  * Documentation format upgraded to OpenAPI 3.1 for better tooling and interactivity.
  * Internal implementation rebuilt for faster iteration, better error handling, and consistent endpoint behavior.
  * Error messaging:
    * Authentication errors now return `401 Unauthorized` (previously conflated with `403 Forbidden` which is now reserved for actual permission issues).
    * Insufficient account credit returns `402 Payment Required` instead of `500`.
  * Consistent default values in responses (e.g., `false`, `0`, `""`) instead of omitting them.
  * Correct `Content-Type` headers for JSON responses (`application/json`).
  * `Content-Type: application/json` strictly required for all `PUT`, `POST`, and `PATCH` requests (including body-less `POST` actions due to server behavior).

  ### Removed

  * SearchStream endpoint (may return in a future version with a revised implementation).

  ### Added

  * Domain Update endpoint for autorenew, WHOIS Privacy, and locking. See DomainUpdate docs.
</Update>
