> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Pricing For Domain

> Returns registration, renewal, and transfer pricing for a domain and term.

**Not a discovery endpoint:** Does not return `purchaseType`. Cannot determine whether a domain is acquired via registration vs aftermarket/expiring/backorder — call [Search](/api/v1/reference/domains/search) or [Check Availability](/api/v1/reference/domains/check-availability) first.

**Scope:** `purchasePrice` and `premium` reflect **standard and registry-premium registration** only. They do **not** return aftermarket, expiring, or backorder acquisition prices. For those types, use `purchasePrice` from Search or Check Availability.

**Registration create (`purchaseType: registration`):** When create requires `purchasePrice` (registry premium), call with the **same** `years` you will send on create. Pass `purchasePrice` directly — it is the **total** for that term, not a per-year component.

**Renew:** Pass `renewalPrice` as `purchasePrice` on [Renew Domain](/api/v1/reference/domains/renew-domain) for premium renewals — not for computing Create Domain totals.

**Transfer:** Pass `transferPrice` as `purchasePrice` on [Create Transfer](/api/v1/reference/transfers/create-transfer) for premium transfers. The `years` query parameter does not affect `transferPrice`.

See the [Domain pricing guide](/guides/domain-pricing) for the full workflow.




## OpenAPI

````yaml get /core/v1/domains/{domainName}:getPricing
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
  /core/v1/domains/{domainName}:getPricing:
    get:
      tags:
        - Domains
      summary: Get Pricing For Domain
      description: >
        Returns registration, renewal, and transfer pricing for a domain and
        term.


        **Not a discovery endpoint:** Does not return `purchaseType`. Cannot
        determine whether a domain is acquired via registration vs
        aftermarket/expiring/backorder — call
        [Search](/api/v1/reference/domains/search) or [Check
        Availability](/api/v1/reference/domains/check-availability) first.


        **Scope:** `purchasePrice` and `premium` reflect **standard and
        registry-premium registration** only. They do **not** return
        aftermarket, expiring, or backorder acquisition prices. For those types,
        use `purchasePrice` from Search or Check Availability.


        **Registration create (`purchaseType: registration`):** When create
        requires `purchasePrice` (registry premium), call with the **same**
        `years` you will send on create. Pass `purchasePrice` directly — it is
        the **total** for that term, not a per-year component.


        **Renew:** Pass `renewalPrice` as `purchasePrice` on [Renew
        Domain](/api/v1/reference/domains/renew-domain) for premium renewals —
        not for computing Create Domain totals.


        **Transfer:** Pass `transferPrice` as `purchasePrice` on [Create
        Transfer](/api/v1/reference/transfers/create-transfer) for premium
        transfers. The `years` query parameter does not affect `transferPrice`.


        See the [Domain pricing guide](/guides/domain-pricing) for the full
        workflow.
      operationId: GetPricingForDomain
      parameters:
        - name: domainName
          description: DomainName is the domain to retrieve.
          in: path
          required: true
          schema:
            type: string
        - name: years
          description: >-
            Years specifies the registration term to price in years. Defaults to
            each TLD's minimum registration term if omitted — usually 1 year (2
            for `.ai`). Must be a supported registration term for the TLD
            (commonly 1–10 years). Use the same value on Create Domain when
            passing `purchasePrice` for `purchaseType: registration`.
          in: query
          schema:
            format: int32
            type: integer
            minimum: 1
            maximum: 10
            example: 2
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PricingResponse'
          description: A successful response.
        '400':
          description: Bad request - Invalid input data.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
              examples:
                invalidYears:
                  summary: Invalid registration term
                  value:
                    message: Invalid value for years for this domain
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
          description: Domain name not found.
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
        '422':
          description: TLD not supported.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnprocessableEntity422'
              examples:
                tldNotSupported:
                  summary: TLD not supported
                  value:
                    message: Unsupported TLD
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
    PricingResponse:
      description: >-
        PricingResponse returns the Pricing related information from the
        GetPricingForDomain endpoint.

        Covers standard and registry-premium **registration** pricing, plus
        renewal and transfer. Not a discovery endpoint — does not return
        `purchaseType`. Does not return aftermarket, expiring, or backorder
        acquisition prices. See the [Domain pricing
        guide](/guides/domain-pricing).
      properties:
        premium:
          description: >-
            Premium indicates whether this registration pricing result is for a
            registry premium or other non-standard registration. Reflects
            registration pricing only — may differ from discovery `premium` for
            aftermarket, expiring, or backorder results. When `true`,
            `purchasePrice` must be passed on [Create
            Domain](/api/v1/reference/domains/create-domain), [Renew
            Domain](/api/v1/reference/domains/renew-domain), or [Create
            Transfer](/api/v1/reference/transfers/create-transfer), requests.
          type: boolean
        purchasePrice:
          description: >-
            PurchasePrice is the total standard or registry-premium registration
            cost for the requested `years` query parameter — not a one-year
            component. Does not include aftermarket, expiring, or backorder
            acquisition prices. If `null`, name.com is not currently accepting
            registrations for this domain/term combination. For registry premium
            create (`purchaseType: registration`), pass this value with the same
            `years`. For aftermarket, expiring, or backorder types, use
            `purchasePrice` from Search/Check Availability instead.
          format: double
          type:
            - number
            - 'null'
          example: 24.99
        renewalPrice:
          description: >-
            RenewalPrice is the total renewal cost for the requested `years`. If
            `null`, name.com is not currently accepting renewals for this
            domain/term combination. Pass as `purchasePrice` on [Renew
            Domain](/api/v1/reference/domains/renew-domain) for premium
            renewals. Do not use for computing Create Domain `purchasePrice` or
            multi-year create totals.
          format: double
          type:
            - number
            - 'null'
          example: 24.99
        transferPrice:
          description: >-
            TransferPrice is the inbound transfer cost for this domain. The
            `years` query parameter does not affect this value. Pricing uses the
            TLD's minimum transfer/registration term (typically 1 year; for TLDs
            with a higher minimum, e.g. `.ai`, the total will reflect that
            minimum). If `null`, transfers are not accepted for this domain/term
            combination. Pass to [Create
            Transfer](/api/v1/reference/transfers/create-transfer) as
            `purchasePrice` when transfer price validation applies (required for
            premium transfers).
          format: double
          type:
            - number
            - 'null'
          example: 24.99
      type: object
      required:
        - premium
        - purchasePrice
        - transferPrice
        - renewalPrice
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