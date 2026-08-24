> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Zone Check

> Zone Check offers a rapid, preliminary check for domain availability by leveraging cached zone file data.  Ideal for large-batch queries, it provides a high confidence indication of a domain's availability significantly faster than live registry checks.  For definitive, real-time availability and pricing, you can follow up with the standard [Check Availability](/api/v1/reference/domains/check-availability) call.
The API normalizes and validates each submitted domain string. Domains that fail validation, use an unsupported TLD for this service, or  are otherwise not eligible for zone check are **removed** from the request before the zone file lookup runs. The response includes **only**  a numeric count of removed domains (`removed`); individual removed strings are not returned. A future API version may extend the contract to  include details about removed domains.

For the best results and to avoid `400 Bad Request` errors after cleaning, ensure each domain string meets the criteria described for  `domainNames` in the request body schema.

If no valid domains remain after this process, the API returns a `400 Bad Request` response.
**Note:** The cached zone files used for this check are refreshed twice daily based on the latest available data from the registries.



## OpenAPI

````yaml post /core/v1/zonecheck
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
  /core/v1/zonecheck:
    post:
      tags:
        - Domains
      summary: Zone Check
      description: >-
        Zone Check offers a rapid, preliminary check for domain availability by
        leveraging cached zone file data.  Ideal for large-batch queries, it
        provides a high confidence indication of a domain's availability
        significantly faster than live registry checks.  For definitive,
        real-time availability and pricing, you can follow up with the standard
        [Check Availability](/api/v1/reference/domains/check-availability) call.

        The API normalizes and validates each submitted domain string. Domains
        that fail validation, use an unsupported TLD for this service, or  are
        otherwise not eligible for zone check are **removed** from the request
        before the zone file lookup runs. The response includes **only**  a
        numeric count of removed domains (`removed`); individual removed strings
        are not returned. A future API version may extend the contract to 
        include details about removed domains.


        For the best results and to avoid `400 Bad Request` errors after
        cleaning, ensure each domain string meets the criteria described for 
        `domainNames` in the request body schema.


        If no valid domains remain after this process, the API returns a `400
        Bad Request` response.

        **Note:** The cached zone files used for this check are refreshed twice
        daily based on the latest available data from the registries.
      operationId: ZoneCheck
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ZoneCheckRequest'
        description: Request body to check for availability
        required: true
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ZoneCheckResponse'
          description: Successful response for a DNS zone check.
        '400':
          description: Bad request - Invalid input data.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
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
        '415':
          description: >-
            All POST, PUT, PATCH requests for this API must include the
            `Content-Type: application/json` header in the requests.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnsupportedMedia415'
        '422':
          description: >-
            Returned when, after cleaning, there were no valid domains passed in
            the request.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnprocessableEntity422'
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
          description: >-
            There was a temporary error in processing the request. The request
            can be retried immediately.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BadGateway502'
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
    ZoneCheckRequest:
      description: >-
        ZoneCheck request checks DNS zone files for the availability of the
        specified domains.
      type: object
      properties:
        domainNames:
          description: >-
            Array of domain names to check. Each entry is normalized and
            validated before zone check runs. Entries that are not valid domain
            strings,  that use unsupported TLDs for this service, or that fail
            other pre-validation rules are omitted from the check; the response
            `removed` field  reports how many were omitted (not which values).


            **Valid domain string (after normalization)** — for reliable results
            and to avoid errors once all entries are removed:


            - **Allowed characters:** ASCII letters (`a`–`z`), digits (`0`–`9`),
            and hyphens (`-`).


            - **Hyphen rules:** A domain (the part between dots) must not start
            or end with a hyphen (for example, `-test.com` and `test-.com` are
            invalid).


            - **Domain length:** Each domain must be between 1 and 63
            characters.


            - **Internationalized domains (IDNs):** Non-ASCII characters (for
            example `ö` or `ñ`) should be submitted as Punycode (`xn--...`) for 
            consistent registry resolution.
          type: array
          items:
            type: string
            minLength: 1
          minItems: 1
          maxItems: 500
          examples:
            - - example.com
              - example.net
              - example.org
            - - test.net
      required:
        - domainNames
    ZoneCheckResponse:
      description: Response for checking domain availability via DNS zone checks.
      type: object
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/ZoneCheckResult'
            minLength: 0
        total:
          description: Total number of records checked
          type: integer
          format: int32
          example: 5
        removed:
          description: >-
            Number of domain strings removed during pre-validation (invalid
            format, unsupported TLD for this service, etc.). This is a count
            only;  the response does not list which strings were removed.
          type: integer
          format: int32
          example: 1
      required:
        - results
        - total
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
    BadGateway502:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Registry Connection Unavailable
    ZoneCheckResult:
      description: Result for checking and individual domain's presense in DNS zone files.
      type: object
      properties:
        domainName:
          description: The domain name that was checked
          type: string
          example: example.com
        available:
          description: >-
            If the domain is potentially available for purchase after checking
            for it's presense in the DNZ zone files.
          type:
            - boolean
            - 'null'
          examples:
            - true
            - false
            - null
      required:
        - domainName
        - available
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