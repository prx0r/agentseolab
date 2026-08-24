> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Domain

> Registers a new domain under your account. You must provide `domain.domainName` at minimum.
This endpoint is commonly used to programmatically onboard new domains through user signup flows or checkout experiences.

If no contacts are passed in this request, the default contacts for your name.com account will be used.

### Create Domain pricing

See the [Domain purchase pricing guide](/guides/domain-pricing) for the full reference.
**Recommendation:** For most integrations, scope discovery to `purchaseType: registration`. Other purchase types are supported but add complexity — details in the guide above.

**Discovery (required before create):** Call [Search](/api/v1/reference/domains/search) or [Check Availability](/api/v1/reference/domains/check-availability), not Get Pricing alone. Both return the same `SearchResult` fields (`purchaseType`, `purchasePrice`, `premium`, `purchasable`). [Zone Check](/api/v1/reference/domains/zone-check) is designed for rapid availability checks only; it is not sufficient to complete a purchase.

### Getting the price for Create Domain

1. **Search or Check Availability** → copy `purchaseType`, `premium`, note `purchasePrice`.

2. Branch on `purchaseType`:
   - **`registration` + `premium: false`** — omit `purchasePrice` on create, set `years`. Optional: Get Pricing with same `years` to preview the total.
   - **`registration` + `premium: true`** — Get Pricing with same `years` → pass `purchasePrice` exactly.
   - **aftermarket / expiring / backorder** — use discovery `purchasePrice` (flat fee). Re-check discovery before create. Do not use Get Pricing for create price. `years` does not multiply price or guarantee registration length.

3. If `purchasePrice` is sent, it must match exactly or the request fails with `400` and `"Purchase price does not match"`.

**Years on acquisition types:** For `aftermarket_s`, `aftermarket_b`, `aftermarket_i`, `expiring`, and `backorder`: omit `years` or pass the TLD default. Check `domain.expireDate` in the response; [Renew](/api/v1/reference/domains/renew-domain) to extend registration.

### Best Practices For Domain Creates

In general, you should check that a domain is available prior to attempting to purchase a domain.
You can use either the [checkAvailability](/api/v1/reference/domains/check-availability) endpoint, or the [Search](/api/v1/reference/domains/search) endpoint
to confirm that a domain is purchasable.

#### Important Note on Dropcatching and Abuse Prevention

_The createDomain endpoint is designed for standard domain registrations and is not intended for automated dropcatching (i.e., mass or high-frequency attempts to register domains the moment they become available after expiration). The use of drop-catching tools or services to acquire expired domains is strictly prohibited. All domain acquisitions must go through approved channels to ensure fair and transparent access._

#### Contact Verification
When a new domain registration is created and a contact is submitted, name.com may need to validate the contact's email address in accordance with ICANN policy. This validation involves sending an email to the provided address, prompting the recipient to click a link to verify their email address.




## OpenAPI

````yaml post /core/v1/domains
openapi: 3.1.0
info:
  contact:
    email: reseller@name.com
    name: Reseller Account Services
  description: >-
    RESTful API for managing domains, DNS records, and related services at
    name.com.  Access via HTTPS at api.name.com (production) or api.dev.name.com
    (testing).  Supports standard authentication, rate-limited to 20
    requests/second.
  title: name.com Core API
  version: 1.33.2
  termsOfService: https://www.name.com/policies/api-access-agreement
servers:
  - description: Testing
    url: https://api.dev.name.com
security:
  - BasicAuth: []
tags:
  - name: Hello
    description: >-
      Use the Hello endpoint to verify that your API connection and credentials
      are working properly. This simple call returns a success message (along
      with server time and version info) to confirm the API is reachable and
      authenticated.
  - name: Account Info
    description: >-
      Use Account Info endpoints to retrieve basic information about your
      name.com account. For example, you can check your account’s current credit
      balance and other account details using these endpoints.
  - name: Accounts
    description: >-
      Use Accounts endpoints (available upon request) to manage sub-accounts
      under your main account. For example, resellers can programmatically
      create new customer accounts with their own login credentials and
      permissions.
  - name: Domains
    description: >-
      Use Domains endpoints to search for domain availability, register new
      domains, and manage existing domains.
  - name: Contact Verification
    description: >-
      Use Contact Verification endpoints to query a reseller’s unverified
      domains/emails and to programmatically mark an end user’s email as
      verified if the reseller has already completed the verification process.
      These endpoints help resellers meet ICANN requirements by ensuring end
      users confirm they can receive email at their listed address.
  - name: DNS
    description: >-
      Use DNS endpoints to manage DNS records for your domains. You can list all
      existing DNS records for a domain and create, update, or delete records as
      needed.
  - name: DNSSECs
    description: >-
      Use DNSSEC endpoints to configure DNS Security Extensions for your
      domains. These endpoints allow you to add, retrieve, or remove DNSSEC
      records.
  - name: Email Forwardings
    description: >-
      Use Email Forwardings endpoints to set up and manage email forwarding
      addresses on your domains.
  - name: URL Forwardings
    description: >-
      Use URL Forwardings endpoints to control URL redirection settings for your
      domains.
  - name: Vanity Nameservers
    description: >-
      Use Vanity Nameservers endpoints to configure custom nameserver hostnames
      (glue records) for your domains.
  - name: Transfers
    description: >-
      Use Transfers endpoints to move domains into your name.com account. Start
      by creating a transfer request for inbound transfers from **external**
      registrars, then monitor and manage the status of pending transfers. Use
      **internal transfer in** to pull a domain from another name.com account
      into your reseller account (enterprise allowlist; requires auth code from
      the losing account’s dashboard). You can cancel an incoming transfer if
      needed, or cancel an outbound transfer (domain leaving name.com) via the
      external transfer-out cancel endpoint. Use the **transfer eligibility**
      endpoint to check whether a domain is currently at name.com before
      initiating a transfer, so you can route to the correct flow (external vs
      internal transfer).
  - name: Orders
    description: Use Orders endpoints to review and track purchases made via the API.
  - name: Refunds
    description: >
      Use the Refunds endpoint to delete eligible domains and advanced security
      products during the Add Grace Period (AGP) and automatically issue refunds
      for the associated order items. You can use the List Orders endpoint to
      retrieve order IDs, then pass those IDs into the Refunds endpoint to
      process eligible deletions and refunds.   This endpoint enforces AGP
      delete limits and supports only domain registrations and advanced security
      add-ons. Refunds are issued  to the original payment method on file. If
      the original payment method is unavailable, the refund will be credited to
      the account balance.
  - name: Webhook Notifications
    description: >
      Use Webhook Notification endpoints to subscribe to real-time notifications
      for account and domain events. This keeps your application updated on
      important changes without polling the API.

      Outbound webhook POSTs include an `X-NAMECOM-SIGNATURE` header. HMAC uses
      one API v4 token per account, chosen deterministically when multiple
      tokens exist (see HMAC Signature Verification in the developer docs). The
      signing input format is unchanged.
  - name: Domain Info
    description: >-
      Use Domain Info endpoints to retrieve information about TLD-specific
      requirements and registration rules. These endpoints help you understand
      what fields, documents, or constraints are needed to successfully register
      domains across different TLDs.
  - name: TLD Pricing
    description: >-
      Use TLD Pricing endpoints to retrieve general pricing information for your
      account.
  - name: Premium Domains
    description: APIs for working with Premium Domains.
paths:
  /core/v1/domains:
    post:
      tags:
        - Domains
      summary: Create Domain
      description: >
        Registers a new domain under your account. You must provide
        `domain.domainName` at minimum.

        This endpoint is commonly used to programmatically onboard new domains
        through user signup flows or checkout experiences.


        If no contacts are passed in this request, the default contacts for your
        name.com account will be used.


        ### Create Domain pricing


        See the [Domain purchase pricing guide](/guides/domain-pricing) for the
        full reference.

        **Recommendation:** For most integrations, scope discovery to
        `purchaseType: registration`. Other purchase types are supported but add
        complexity — details in the guide above.


        **Discovery (required before create):** Call
        [Search](/api/v1/reference/domains/search) or [Check
        Availability](/api/v1/reference/domains/check-availability), not Get
        Pricing alone. Both return the same `SearchResult` fields
        (`purchaseType`, `purchasePrice`, `premium`, `purchasable`). [Zone
        Check](/api/v1/reference/domains/zone-check) is designed for rapid
        availability checks only; it is not sufficient to complete a purchase.


        ### Getting the price for Create Domain


        1. **Search or Check Availability** → copy `purchaseType`, `premium`,
        note `purchasePrice`.


        2. Branch on `purchaseType`:
           - **`registration` + `premium: false`** — omit `purchasePrice` on create, set `years`. Optional: Get Pricing with same `years` to preview the total.
           - **`registration` + `premium: true`** — Get Pricing with same `years` → pass `purchasePrice` exactly.
           - **aftermarket / expiring / backorder** — use discovery `purchasePrice` (flat fee). Re-check discovery before create. Do not use Get Pricing for create price. `years` does not multiply price or guarantee registration length.

        3. If `purchasePrice` is sent, it must match exactly or the request
        fails with `400` and `"Purchase price does not match"`.


        **Years on acquisition types:** For `aftermarket_s`, `aftermarket_b`,
        `aftermarket_i`, `expiring`, and `backorder`: omit `years` or pass the
        TLD default. Check `domain.expireDate` in the response;
        [Renew](/api/v1/reference/domains/renew-domain) to extend registration.


        ### Best Practices For Domain Creates


        In general, you should check that a domain is available prior to
        attempting to purchase a domain.

        You can use either the
        [checkAvailability](/api/v1/reference/domains/check-availability)
        endpoint, or the [Search](/api/v1/reference/domains/search) endpoint

        to confirm that a domain is purchasable.


        #### Important Note on Dropcatching and Abuse Prevention


        _The createDomain endpoint is designed for standard domain registrations
        and is not intended for automated dropcatching (i.e., mass or
        high-frequency attempts to register domains the moment they become
        available after expiration). The use of drop-catching tools or services
        to acquire expired domains is strictly prohibited. All domain
        acquisitions must go through approved channels to ensure fair and
        transparent access._


        #### Contact Verification

        When a new domain registration is created and a contact is submitted,
        name.com may need to validate the contact's email address in accordance
        with ICANN policy. This validation involves sending an email to the
        provided address, prompting the recipient to click a link to verify
        their email address.
      operationId: CreateDomain
      parameters:
        - name: X-Idempotency-Key
          in: header
          description: >-
            A unique string (e.g., a UUID v4) to make the request idempotent.
            This key ensures that if the request is retried, the operation will
            not be performed multiple times. Subsequent requests with the same
            key will return the original result.
          schema:
            type: string
            example: 083910ef-04e4-4bd1-a0bf-3737fe005ca8
          required: false
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateDomainRequest'
            examples:
              noContacts:
                summary: Creating a domain without contacts.
                description: >-
                  For a basic domain create, you do not need to send contacts in
                  the request. **When contacts are not sent in the request, we
                  will apply the default contacts for your account to the
                  domain.**
                value:
                  domain:
                    domainName: example.com
              multipleYears:
                summary: Standard registration, 2 years (omit purchasePrice).
                description: >-
                  For `purchaseType: registration` with `premium: false`, omit
                  `purchasePrice` and set `years` on create. Optionally call Get
                  Pricing with `years=2` to preview the registration total.
                value:
                  domain:
                    domainName: example.com
                  years: 2
              registryPremium:
                summary: Registry premium domain, 1 year.
                description: >-
                  Registry premium uses `purchaseType: registration` with
                  `premium: true` from Search or Check Availability. Call Get
                  Pricing with matching `years` and pass `purchasePrice`
                  exactly.
                value:
                  domain:
                    domainName: premiumexample.com
                  purchasePrice: 349.95
                  purchaseType: registration
                  years: 1
              premiumPurchaseMultiYear:
                summary: Registry premium domain, 2 years (from Get Pricing).
                description: >-
                  For registry premium multi-year, call Get Pricing with
                  `years=2` and pass the returned `purchasePrice` total.
                  Example: flat $349.95/yr registry premium → `purchasePrice:
                  699.90` for 2 years. Do not use discovery `renewalPrice` or
                  multiply aftermarket acquisition fees by years.
                value:
                  domain:
                    domainName: premiumexample.com
                  purchasePrice: 699.9
                  purchaseType: registration
                  years: 2
              aftermarketFlatPrice:
                summary: Aftermarket domain — flat acquisition fee.
                description: >-
                  Aftermarket domains use a flat acquisition fee from Search or
                  Check Availability — not Get Pricing. `purchasePrice: 5000.00`
                  is the acquisition fee only; it does not buy multiple years.
                  Omit `years` or pass the TLD default — it does not affect
                  price or guarantee registration length.
                value:
                  domain:
                    domainName: rarename.com
                  purchasePrice: 5000
                  purchaseType: aftermarket_s
                  years: 1
              expiringPurchase:
                summary: Expiring domain (non-registration purchaseType).
                description: >-
                  Expiring domains use a flat acquisition fee from discovery —
                  not Get Pricing. Pass discovery `purchasePrice` with matching
                  `purchaseType`. Omit `years` or pass the TLD default — it does
                  not affect price or guarantee registration length.
                value:
                  domain:
                    domainName: expiringexample.com
                  purchasePrice: 349.95
                  purchaseType: expiring
                  years: 1
              backorderPurchase:
                summary: Backorder domain (non-registration purchaseType).
                description: >-
                  Backorder domains use a flat TLD-based acquisition fee from
                  discovery — not Get Pricing. Pass discovery `purchasePrice`
                  with matching `purchaseType`. `purchasePrice` is required
                  regardless of the `premium` flag. Omit `years` or pass the TLD
                  default — it does not affect price or guarantee registration
                  length. Re-check Check Availability immediately before create
                  — prices can change. Example price below is illustrative — use
                  the value from your discovery result.
                value:
                  domain:
                    domainName: backorderexample.com
                  purchasePrice: 79.99
                  purchaseType: backorder
              singleContactAtCreate:
                summary: Send single, specific contact with domain create
                description: >-
                  Generally all contacts need to be submitted when creating a
                  domain that will not use your account default contacts. By
                  passing a single contact during a domain create, you can set a
                  single contact to be different than the account default
                  contacts. This may also be required for some TLDs due to ICANN
                  changes in registration contact requirements
                value:
                  domain:
                    domainName: example.com
                    contacts:
                      tech:
                        firstName: Jonny
                        lastName: IT Guy
                        companyName: My Company
                        address1: 1234 Any Street
                        address2: null
                        city: Anytown
                        state: NY
                        zip: '11222'
                        country: US
                        email: support@example.com
                        phone: '+15555555'
              idnRegistration:
                summary: Registering an IDN domain
                description: >-
                  How to pass the correct IDN language for domains using
                  non-ASCII characters.
                value:
                  domain:
                    domainName: exámple.com
                  tldRequirements:
                    language: ES
                  years: 1
              cctldRequirements:
                summary: Registering a .se domain with TLD requirements
                description: >-
                  Some ccTLDs require additional registry-specific fields at
                  create time. Fetch the required keys from [Get TLD
                  Requirements as JSON
                  Schema](/api/v1/reference/domain-info/get-specific-tld-requirements-v2),
                  then pass them under `tldRequirements`. For `.se`,
                  `X-NICSE-IDNUMBER` is required (personal or organizational
                  ID).
                value:
                  domain:
                    domainName: example.se
                  tldRequirements:
                    X-NICSE-IDNUMBER: '5566778899'
                  years: 1
              withClaims:
                summary: Creating a domain with trademark claims acknowledgment
                description: >-
                  When a domain has trademark claims (as determined by the
                  [Domain Claims
                  Check](/api/v1/reference/domain-info/check-domain-claims)
                  endpoint), you must include the claims acknowledgment data in
                  the domain creation request. This includes the claim
                  identifier and validity dates from the claims check response.
                value:
                  domain:
                    domainName: tiktok.page
                  claims:
                    claimId: 8c3027d30000000000382500785
                    notBefore: '2020-01-01T00:00:00Z'
                    notAfter: '2030-01-01T00:00:00Z'
        required: true
      responses:
        '200':
          headers:
            X-Idempotency-Key:
              description: >-
                If the initial request contained this header, echoes back with
                the initial value.
              schema:
                type: string
                example: 083910ef-04e4-4bd1-a0bf-3737fe005ca8
            X-Idempotent-Replay:
              description: >-
                Indicates that the response is being replayed from an idempotent
                request. This header will only be returned if the API is
                responding with cached data. Caches are cleared after 1 hour.
              schema:
                type: number
                example: 1
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateDomainResponse'
          description: A successful response.
        '400':
          description: Bad request - Invalid input data.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
              examples:
                premiumPriceRequired:
                  summary: Premium domain purchase requires price
                  value:
                    message: >-
                      Purchase price is required for premium domains in order to
                      complete this request
                priceRequired:
                  summary: Purchase price required (non-registration purchaseType)
                  value:
                    message: >-
                      Purchase price is required in order to complete this
                      request
                priceMismatch:
                  summary: Purchase price does not match
                  value:
                    message: Purchase price does not match
                invalidYears:
                  summary: Invalid registration term
                  value:
                    message: Invalid years
        '401':
          description: Unauthorized.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error
                    example: Unauthorized
        '402':
          description: Payment has failed for this transaction.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaymentRequired402'
        '403':
          description: Forbidden - you do not have permission to perform this action.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error
                    example: Permission denied
                  details:
                    type:
                      - string
                      - 'null'
                    description: Additional context or information about the error
                    example: Failed authentication
        '404':
          description: Domain or requested resource not found.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotFound404'
        '405':
          description: Method not allowed.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error
                    example: Method Not Allowed
        '409':
          description: >-
            When sending idempotent requests, this response indicates that there
            was an issue with the idempotency keys.
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: Idempotency key has been reused for a different request
        '415':
          description: >-
            All POST, PUT, PATCH requests for this API must include the
            `Content-Type: application/json` header in the requests.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnsupportedMedia415'
        '422':
          description: Pricing information unavailable.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnprocessableEntity422'
              examples:
                registrationUnavailable:
                  summary: Registration price unavailable
                  value:
                    message: Domain pricing unavailable
                    details: >-
                      The pricing information required to process this request
                      is temporarily unavailable. This is an internal system
                      error. Please try again in a few minutes or contact
                      support if the issue persists.
        '429':
          description: Rate limit has been exceeded.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                  - details
                properties:
                  message:
                    type: string
                    description: >-
                      ### Too Many Requests

                      You have exceeded the rate limit.


                      **Headers returned:**

                      * 'X-RateLimit-Reset': An integer (UTC epoch) indicating
                      when you can retry.
                    example: Rate Limit Exceeded
          headers:
            x-ratelimit-reset:
              description: >-
                Unix timestamp for the time at which the current rate limit will
                reset.
              schema:
                type: number
                example: 1747668270
        '451':
          description: Unavailable for Legal Reasons.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnavailableForLegal451'
        '500':
          description: Internal server error.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error.
                    example: Internal Server Error
                  details:
                    type:
                      - string
                      - 'null'
                    description: Additional context or information about the error.
                    example: Something went wrong.
        '501':
          description: Not implemented.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericError501'
        '502':
          description: Bad Gateway
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error.
                    example: >-
                      The server received an invalid response from the upstream
                      server.
        '503':
          description: >-
            Service Unavailable — returned during scheduled maintenance when the
            API is offline. See https://status.name.com for updates.
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error.
                    example: Service Unavailable
                  details:
                    type:
                      - string
                      - 'null'
                    description: Additional context or information about the error.
                    example: >-
                      The API is offline for scheduled maintenance. See
                      https://status.name.com for updates.
        '504':
          description: Gateway Timeout
          content:
            application/json:
              schema:
                type: object
                required:
                  - message
                properties:
                  message:
                    type: string
                    description: >-
                      A human-readable message providing more details about the
                      error.
                    example: The upstream server is taking too long to respond.
components:
  schemas:
    CreateDomainRequest:
      description: >-
        CreateDomainRequest has the information that is needed to create a
        domain with the CreateDomain function.

        See the [Domain pricing guide](/guides/domain-pricing) for which
        endpoints supply create pricing (Search/Check Availability vs Get
        Pricing) for each `purchaseType`.
      properties:
        domain:
          $ref: '#/components/schemas/DomainCreatePayload'
        purchasePrice:
          description: >-
            PurchasePrice is the price in USD for purchasing this domain for the
            minimum time period (typically 1 year). PurchasePrice is required if
            purchaseType is not "registration" or if it is a premium domain. If
            privacyEnabled is set, the regular price for Whois Privacy
            protection will be added automatically. If VAT tax applies, it will
            also be added automatically.
          format: double
          type: number
        purchaseType:
          description: >-
            PurchaseType indicates what kind of purchase this domain create is
            for. Defaults to `registration` if omitted. **Recommended:** Use
            `registration` unless you support acquisition types (aftermarket,
            expiring, backorder) — see the [Domain purchase pricing
            guide](/guides/domain-pricing). This value should be copied from the
            [Search](/api/v1/reference/domains/search) or [Check
            Availability](/api/v1/reference/domains/check-availability) result.
            The value `registration` covers both standard and **registry
            premium** domains — use the `premium` flag from the discovery result
            to tell them apart. Aftermarket, expiring, and backorder types use
            flat acquisition fees from Search or Check Availability; see the
            [Domain pricing guide](/guides/domain-pricing).
          type: string
        tldRequirements:
          additionalProperties:
            type: string
          description: >-
            TLDRequirements is a way to pass additional data that is required by
            some registries. You can check before registration by using the
            [Domain
            Info](/api/v1/reference/domain-info/get-specific-tld-requirements)
            API.

            As these requirements vary wildly between registries and TLDs, we
            are not attempting to document them here.

            #### IDN Domains

            This parameter is required for registering domains that contain
            non-ASCII characters.  The value should be the specific code for the
            character set, such as `ES` for Spanish, or `CYRL` for Cyrillic.
            These abbreviations can vary between TLDs, and it is highly
            recommended that you use [Domain
            Info](/api/v1/reference/domain-info/get-specific-tld-requirements)
            API to ensure that the TLD allows for the specific IDN table, as
            well as the correct abbreviation.
          type: object
        claims:
          $ref: '#/components/schemas/DomainClaimsInfo'
        years:
          description: >-
            Years specifies the registration term in years. **Only affects price
            and registration length for `purchaseType: registration`.** Defaults
            to each TLD's minimum if omitted (usually 1; 2 for `.ai`). Must be a
            supported registration term for the TLD when `purchaseType` is
            `registration` (commonly 1–10 years). For `purchaseType:
            registration` when `purchasePrice` is required, call [Get
            Pricing](/api/v1/reference/domains/get-pricing-for-domain) with the
            same `years` value. For aftermarket, expiring, and backorder types:
            pass the TLD default — it does **not** multiply `purchasePrice` and
            does **not** guarantee a multi-year registration. Check
            `domain.expireDate` in the create response for actual expiry. To add
            registration time after acquisition, use [Renew
            Domain](/api/v1/reference/domains/renew-domain).
          format: int32
          type: integer
          example: 1
        promoCode:
          description: >-
            PromoCode is an optional promotional code to apply to the domain
            purchase. Only one promo code can be applied per request.
          type: string
          minLength: 1
      type: object
      required:
        - domain
    CreateDomainResponse:
      description: >-
        CreateDomainResponse contains the domain info as well as the order info
        for the created domain.
      properties:
        domain:
          $ref: '#/components/schemas/DomainResponsePayload'
        order:
          description: Order is an identifier for this purchase.
          format: int32
          type: integer
        totalPaid:
          description: >-
            TotalPaid is the total amount paid, including VAT and Whois privacy
            protection.
          format: double
          type: number
      type: object
      required:
        - order
        - totalPaid
        - domain
    InvalidArgument400:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Bad Request
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: '''domainName'' cannot be null'
    PaymentRequired402:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Payment failed
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: Insufficient Funds
    NotFound404:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Not Found
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: The requested domain does not exist.
    UnsupportedMedia415:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: >-
            The 'Content-Type' header must be 'application/json' for this
            request.
    UnprocessableEntity422:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Unprocessable Entity
        details:
          type: string
          description: Additional context or information about the pricing error
          example: >-
            The pricing information required to process this request is
            temporarily unavailable. This is an internal system error. Please
            try again in a few minutes or contact support if the issue persists.
    UnavailableForLegal451:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: >-
            A human-readable message explaining why the resource is unavailable
            for legal reasons
          example: Unavailable for Legal Reasons
        details:
          type: string
          description: Additional context or information about the legal restriction
          example: >-
            This domain registration is restricted due to legal requirements in
            your jurisdiction.
    GenericError501:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Unimplemented
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: Requested feature is not yet implemented
    DomainCreatePayload:
      description: The payload to be sent for when making a request to purchase a domain.
      allOf:
        - $ref: '#/components/schemas/Domain'
        - type: object
          required:
            - domainName
          properties:
            domainName:
              type: string
            contacts:
              $ref: '#/components/schemas/ContactsRequest'
    DomainClaimsInfo:
      description: >-
        Claims acknowledgement data is required if trademark claims exist for
        requested domain. This data is obtained from a [Domain Claims
        Check](/api/v1/reference/domain-info/check-domain-claims) response and
        includes the claim identifier and validity dates.
      type: object
      properties:
        claimId:
          type: string
          description: The claim identifier from TMCH (Trademark Clearinghouse)
          example: 8c3027d30000000000382500785
        notBefore:
          type: string
          format: date-time
          description: The date before which the claim acknowledgment is not valid
          example: '2024-01-15T10:30:00Z'
        notAfter:
          type: string
          format: date-time
          description: The date after which the claim acknowledgment expires
          example: '2024-01-15T10:30:00Z'
    DomainResponsePayload:
      description: The response format for a domain.
      allOf:
        - $ref: '#/components/schemas/Domain'
        - type: object
          properties:
            domainName:
              $ref: '#/components/schemas/domainName'
            createDate:
              $ref: '#/components/schemas/createDate'
            expireDate:
              $ref: '#/components/schemas/expireDate'
            autorenewEnabled:
              $ref: '#/components/schemas/autorenewEnabled'
            locked:
              $ref: '#/components/schemas/locked'
            transferLockExpiresAt:
              $ref: '#/components/schemas/transferLockExpiresAt'
            privacyEnabled:
              $ref: '#/components/schemas/privacyEnabled'
            contacts:
              $ref: '#/components/schemas/Contacts'
            nameservers:
              $ref: '#/components/schemas/nameservers'
            renewalPrice:
              $ref: '#/components/schemas/renewalPrice'
          required:
            - domainName
            - createDate
            - expireDate
            - autorenewEnabled
            - locked
            - privacyEnabled
            - contacts
            - nameservers
    Domain:
      description: Domain contains all relevant data for a domain.
      type: object
      properties:
        domainName:
          description: The punycode-encoded value of the domain name.
          type: string
          example: example.com
        createDate:
          description: The date and time when the domain was created at the registry.
          type: string
          format: date-time
          example: '2023-01-15T14:30:00Z'
          readOnly: true
        expireDate:
          description: The date and time when the domain will expire.
          type: string
          format: date-time
          example: '2025-01-15T14:30:00Z'
          readOnly: true
        autorenewEnabled:
          description: >-
            Indicates whether the domain is set to renew automatically before
            expiration.
          type: boolean
          example: true
        locked:
          description: >-
            Indicates if the domain is **transfer locked**, preventing transfers
            to another registrar.
          type: boolean
          example: true
        locks:
          description: >-
            List of all registry locking statuses currently applied to the
            domain. Use this to see which locks are active (e.g.
            clientTransferProhibited, clientHold). Empty when the domain has no
            locks applied.
          type: array
          items:
            type: string
          readOnly: true
          example:
            - clientTransferProhibited
            - clientHold
        transferLockExpiresAt:
          description: >-
            When present, the domain has an active ICANN-mandated transfer lock
            (new registration, transfer-in, or material registrant contact
            change) that blocks client unlock via the API until this time. When
            omitted, there is no active policy transfer lock with a known expiry
            — the domain may still be locked (`locked: true`) due to a voluntary
            user lock. Does not represent RegistrarLock, AccountLock,
            verification holds, trademark-claim locks, or admin TransferLock
            with no expiry date.
          type: string
          format: date-time
          example: '2023-03-16T14:30:00Z'
          readOnly: true
        privacyEnabled:
          description: Indicates if Whois Privacy is enabled for this domain.
          type: boolean
          example: true
        contacts:
          $ref: '#/components/schemas/Contacts'
        nameservers:
          description: >-
            The list of nameservers assigned to this domain. If unspecified, it
            defaults to the account's default nameservers.
          type: array
          items:
            type: string
          example:
            - ns1.example.com
            - ns2.example.com
        renewalPrice:
          description: >-
            The cost to renew the domain. This may be required for the
            RenewDomain operation.
          type: number
          format: double
          example: 12.99
          readOnly: true
    ContactsRequest:
      description: >-
        Contacts stores the contact information for the roles related to
        domains. This schema is used for requests.
      properties:
        admin:
          $ref: '#/components/schemas/ContactRequest'
        billing:
          $ref: '#/components/schemas/ContactRequest'
        registrant:
          $ref: '#/components/schemas/RegistrantContactRequest'
        tech:
          $ref: '#/components/schemas/ContactRequest'
      type: object
    domainName:
      description: The punycode-encoded value of the domain name.
      type: string
      example: example.com
    createDate:
      description: The date and time when the domain was created at the registry.
      type: string
      format: date-time
      example: '2023-01-15T14:30:00Z'
      readOnly: true
    expireDate:
      description: The date and time when the domain will expire.
      type: string
      format: date-time
      example: '2025-01-15T14:30:00Z'
      readOnly: true
    autorenewEnabled:
      description: >-
        Indicates whether the domain is set to renew automatically before
        expiration.
      type: boolean
      example: true
    locked:
      description: >-
        Indicates if the domain is **transfer locked**, preventing transfers to
        another registrar.
      type: boolean
      example: true
    transferLockExpiresAt:
      description: >-
        When present, the domain has an active ICANN-mandated transfer lock (new
        registration, transfer-in, or material registrant contact change) that
        blocks client unlock via the API until this time. When omitted, there is
        no active policy transfer lock with a known expiry — the domain may
        still be locked (`locked: true`) due to a voluntary user lock. Does not
        represent RegistrarLock, AccountLock, verification holds,
        trademark-claim locks, or admin TransferLock with no expiry date.
      type: string
      format: date-time
      example: '2023-03-16T14:30:00Z'
      readOnly: true
    privacyEnabled:
      description: Indicates if Whois Privacy is enabled for this domain.
      type: boolean
      example: true
    Contacts:
      description: >-
        Contacts stores the contact information for the roles related to
        domains.
      properties:
        admin:
          $ref: '#/components/schemas/Contact'
        billing:
          $ref: '#/components/schemas/Contact'
        registrant:
          $ref: '#/components/schemas/RegistrantContact'
        tech:
          $ref: '#/components/schemas/Contact'
      type: object
    nameservers:
      description: >-
        The list of nameservers assigned to this domain. If unspecified, it
        defaults to the account's default nameservers.
      type: array
      items:
        type: string
      example:
        - ns1.example.com
        - ns2.example.com
    renewalPrice:
      description: >-
        The cost to renew the domain. This may be required for the RenewDomain
        operation.
      type: number
      format: double
      example: 12.99
      readOnly: true
    ContactRequest:
      description: >-
        Contact contains all relevant contact data for a domain registrant. 
        This schema is used for creating and updating contacts (POST/PUT
        requests) and includes all validation requirements. All fields listed in
        the `required` array must be provided and cannot be null or empty.
      allOf:
        - $ref: '#/components/schemas/Contact'
        - type: object
          properties:
            firstName:
              description: First name of the contact.
              type: string
              example: John
              minLength: 1
            lastName:
              description: Last name of the contact.
              type: string
              example: Doe
              minLength: 1
            address1:
              description: The first line of the contact's address.
              type: string
              example: 123 Main Street
              minLength: 1
            city:
              description: City of the contact's address.
              type: string
              example: New York
              minLength: 1
            state:
              description: State or Province of the contact's address.
              type: string
              example: NY
              minLength: 1
            zip:
              description: >-
                ZIP or Postal Code of the contact's address. This field is
                required and must be a non-empty string.
              type: string
              example: '10001'
              minLength: 1
            country:
              description: >-
                Country code for the contact's address. Must be an ISO 3166-1
                alpha-2 country code.
              type: string
              example: US
              pattern: ^[A-Z]{2}$
            email:
              description: >-
                Email address of the contact. Must be a valid email format. The
                validation is performed against the `addr-spec` syntax in [RFC
                822](https://datatracker.ietf.org/doc/html/rfc822)
              type: string
              format: email
              example: john.doe@example.com
            phone:
              description: >-
                Phone number of the contact. Should follow the E.164
                international format: "+[country code][number]".
              type: string
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15551234567'
            fax:
              description: >-
                Fax number of the contact. Should follow the E.164 international
                format: "+[country code][number]".
              type:
                - string
                - 'null'
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15557654321'
          required:
            - firstName
            - lastName
            - address1
            - city
            - state
            - zip
            - country
            - email
            - phone
    RegistrantContactRequest:
      description: >-
        Contact contains all relevant contact data for a domain registrant. 
        This schema is used for creating and updating contacts (POST/PUT
        requests) and includes all validation requirements. All fields listed in
        the `required` array must be provided and cannot be null or empty.
      allOf:
        - $ref: '#/components/schemas/RegistrantContact'
        - type: object
          properties:
            firstName:
              description: First name of the contact.
              type: string
              example: John
              minLength: 1
            lastName:
              description: Last name of the contact.
              type: string
              example: Doe
              minLength: 1
            address1:
              description: The first line of the contact's address.
              type: string
              example: 123 Main Street
              minLength: 1
            city:
              description: City of the contact's address.
              type: string
              example: New York
              minLength: 1
            state:
              description: State or Province of the contact's address.
              type: string
              example: NY
              minLength: 1
            zip:
              description: >-
                ZIP or Postal Code of the contact's address. This field is
                required and must be a non-empty string.
              type: string
              example: '10001'
              minLength: 1
            country:
              description: >-
                Country code for the contact's address. Must be an ISO 3166-1
                alpha-2 country code.
              type: string
              example: US
              pattern: ^[A-Z]{2}$
            email:
              description: >-
                Email address of the contact. Must be a valid email format. The
                validation is performed against the `addr-spec` syntax in [RFC
                822](https://datatracker.ietf.org/doc/html/rfc822)
              type: string
              format: email
              example: john.doe@example.com
            phone:
              description: >-
                Phone number of the contact. Should follow the E.164
                international format: "+[country code][number]".
              type: string
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15551234567'
            fax:
              description: >-
                Fax number of the contact. Should follow the E.164 international
                format: "+[country code][number]".
              type:
                - string
                - 'null'
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15557654321'
          required:
            - firstName
            - lastName
            - address1
            - city
            - state
            - zip
            - country
            - email
            - phone
    Contact:
      description: >-
        Contact contains all relevant contact data for a domain registrant. This
        schema is used for API responses and may contain null values for legacy
        data. For creating or updating contacts, use ContactRequest which
        enforces all validation requirements.
      type: object
      properties:
        firstName:
          description: First name of the contact.
          type:
            - string
            - 'null'
          example: John
        lastName:
          description: Last name of the contact.
          type:
            - string
            - 'null'
          example: Doe
        companyName:
          description: >-
            Company name of the contact. Leave blank if the contact is an
            individual, as some registries may assume it is a corporate entity
            otherwise.
          type:
            - string
            - 'null'
          example: Example Inc.
        address1:
          description: The first line of the contact's address.
          type:
            - string
            - 'null'
          example: 123 Main Street
        address2:
          description: The second line of the contact's address (optional).
          type:
            - string
            - 'null'
          example: Suite 400
        city:
          description: City of the contact's address.
          type:
            - string
            - 'null'
          example: New York
        state:
          description: State or Province of the contact's address.
          type:
            - string
            - 'null'
          example: NY
        zip:
          description: ZIP or Postal Code of the contact's address.
          type:
            - string
            - 'null'
          example: '10001'
        country:
          description: >-
            Country code for the contact's address. Must be an ISO 3166-1
            alpha-2 country code.
          type:
            - string
            - 'null'
          example: US
        email:
          description: >-
            Email address of the contact. Must be a valid email format. The
            validation is performed against the `addr-spec` syntax in [RFC
            822](https://datatracker.ietf.org/doc/html/rfc822)
          type:
            - string
            - 'null'
          example: john.doe@example.com
        phone:
          description: >-
            Phone number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15551234567'
        fax:
          description: >-
            Fax number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15557654321'
        isVerified:
          description: >-
            Indicates if the contact has been verified as per ICANN
            requirements. If the value is `false` it indicates that the contact
            has not completed the required verification process. This property
            is read-only and will be included in responses but should not be
            included in requests.
          type: boolean
          example: true
          readOnly: true
        verificationId:
          description: >-
            When the contact is unverified, this is the ID of the pending
            verification record. Use this ID with the resend verification email
            and verify contact endpoints. Omitted or null when the contact is
            verified.
          type:
            - integer
            - 'null'
          format: int64
          example: 12345
          readOnly: true
    RegistrantContact:
      description: >-
        Contact contains all relevant contact data for a domain registrant. This
        schema is used for API responses and may contain null values for legacy
        data. For creating or updating contacts, use RegistrantContactRequest
        which enforces all validation requirements.
      type: object
      properties:
        firstName:
          description: First name of the contact.
          type:
            - string
            - 'null'
          example: John
        lastName:
          description: Last name of the contact.
          type:
            - string
            - 'null'
          example: Doe
        companyName:
          description: >-
            Company name of the contact. Leave blank if the contact is an
            individual. Please be advised that ICANN policy links the "Company
            Name" field (Organization) in your domain's contact details to its
            legal ownership. If this field contains information, the listed
            organization is considered the legal "Registered Name Holder"
            (domain owner).
          type:
            - string
            - 'null'
          example: Example Inc.
        address1:
          description: The first line of the contact's address.
          type:
            - string
            - 'null'
          example: 123 Main Street
        address2:
          description: The second line of the contact's address (optional).
          type:
            - string
            - 'null'
          example: Suite 400
        city:
          description: City of the contact's address.
          type:
            - string
            - 'null'
          example: New York
        state:
          description: State or Province of the contact's address.
          type:
            - string
            - 'null'
          example: NY
        zip:
          description: ZIP or Postal Code of the contact's address.
          type:
            - string
            - 'null'
          example: '10001'
        country:
          description: >-
            Country code for the contact's address. Must be an ISO 3166-1
            alpha-2 country code.
          type:
            - string
            - 'null'
          example: US
        email:
          description: >-
            Email address of the contact. Must be a valid email format. The
            validation is performed against the `addr-spec` syntax in [RFC
            822](https://datatracker.ietf.org/doc/html/rfc822)
          type:
            - string
            - 'null'
          example: john.doe@example.com
        phone:
          description: >-
            Phone number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15551234567'
        fax:
          description: >-
            Fax number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15557654321'
        isVerified:
          description: >-
            Indicates if the contact has been verified as per ICANN
            requirements. If the value is `false` it indicates that the contact
            has not completed the required verification process. This property
            is read-only and will be included in responses but should not be
            included in requests.
          type: boolean
          example: true
          readOnly: true
        verificationId:
          description: >-
            When the contact is unverified, this is the ID of the pending
            verification record. Use this ID with the resend verification email
            and verify contact endpoints. Omitted or null when the contact is
            verified.
          type:
            - integer
            - 'null'
          format: int64
          example: 12345
          readOnly: true
  securitySchemes:
    BasicAuth:
      scheme: basic
      type: http
      description: >-
        Authenticate via HTTP Basic with your account username and API token.
        Examples use an explicit 'Authorization: Basic <base64(username:token)>'
        header; 'curl -u username:token' is equivalent. For sandbox, append
        "-test" to your username and use your sandbox token on api.dev.name.com.

````