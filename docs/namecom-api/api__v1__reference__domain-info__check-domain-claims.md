> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Check Domain Claims

> Performs the actual claims check for a specific domain. This endpoint checks if a specific domain has trademark claims against it, returning detailed information about any matching trademarks and their holders. Use this to verify if a domain can be registered without trademark conflicts. Please see the [claims flow](/guides/claims-flow) for information on how to use this endpoint in your domain purchase flow.



## OpenAPI

````yaml post /core/v1/domaininfo/claims/{domain}
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
  /core/v1/domaininfo/claims/{domain}:
    post:
      tags:
        - Domain Info
      summary: Check Domain Claims
      description: >-
        Performs the actual claims check for a specific domain. This endpoint
        checks if a specific domain has trademark claims against it, returning
        detailed information about any matching trademarks and their holders.
        Use this to verify if a domain can be registered without trademark
        conflicts. Please see the [claims flow](/guides/claims-flow) for
        information on how to use this endpoint in your domain purchase flow.
      operationId: CheckDomainClaims
      parameters:
        - name: domain
          description: >-
            The domain name to check for trademark claims (e.g., 'tiktok.page',
            'example.com'). Include the full domain name including the TLD.
          in: path
          required: true
          schema:
            type: string
            example: tiktok.page
            pattern: >-
              ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$
      requestBody:
        description: >-
          Optional parameters for the claims check. The type defaults to
          'registration' if not specified.
        required: false
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DomainClaimsCheckRequest'
      responses:
        '200':
          description: Domain claims check completed successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DomainClaimsCheckResponse'
              examples:
                claims_found:
                  summary: Domain with trademark claims
                  description: Example of a domain that has trademark claims against it
                  value:
                    domain: tiktok.page
                    claims: []
                    claimsProcessActive: true
                    claimId: 8c3027d30000000000382500785
                    notBefore: '2020-01-01T00:00:00Z'
                    notAfter: '2030-01-01T00:00:00Z'
                no_claims_found:
                  summary: Domain without trademark claims
                  description: Example of a domain that has no trademark claims against it
                  value:
                    domain: mycompany.page
                    claims: []
                    claimsProcessActive: false
                    claimId: null
                    notBefore: null
                    notAfter: null
        '400':
          description: Bad request - invalid domain format or parameters.
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
        '404':
          description: Domain not found or TLD not supported for claims checking.
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
        '415':
          description: >-
            All POST, PUT, PATCH requests for this API must include the
            `Content-Type: application/json` header in the requests.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnsupportedMedia415'
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
    DomainClaimsCheckRequest:
      type: object
      description: Request parameters for domain claims checking
      properties:
        purchaseType:
          type: string
          description: >-
            The type of purchase/registration for which to check claims.
            Defaults to 'registration'. Other values like 'landrush_eap',
            'landrush_auction_a', 'landrush_reserve_a' may be used during new
            gTLD launches.
          default: registration
          enum:
            - registration
            - landrush_eap
            - landrush_auction_a
            - landrush_reserve_a
          example: registration
    DomainClaimsCheckResponse:
      type: object
      description: >-
        Response containing domain-specific claims data and trademark
        information
      required:
        - domain
        - claims
      properties:
        domain:
          type: string
          description: The domain name that was checked for claims
          example: tiktok.page
        claims:
          type: array
          description: List of trademark claims found against this domain
          items:
            $ref: '#/components/schemas/TrademarkClaim'
        claimsProcessActive:
          type: boolean
          description: Whether the TLD of this domain requires claims checking
          example: true
        claimId:
          type:
            - string
            - 'null'
          description: The claim identifier from TMCH (null if no claims found)
          example: 8c3027d30000000000382500785
        notBefore:
          type:
            - string
            - 'null'
          format: date-time
          description: >-
            The date before which the claim acknowledgment is not valid (null if
            no claims found)
          example: '2024-01-15T10:30:00Z'
        notAfter:
          type:
            - string
            - 'null'
          format: date-time
          description: >-
            The date after which the claim acknowledgment expires (null if no
            claims found)
          example: '2024-01-15T10:30:00Z'
        claimsNotice:
          type: string
          description: Markdown content to display about this specific trademark claim
          example: >-
            **This domain may infringe on a trademark claim. Proceeding with
            registration acknowledges that you have received notice of this
            claim.**
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
    TrademarkClaim:
      type: object
      description: Information about a specific trademark claim
      required:
        - trademark
        - holder
      properties:
        trademark:
          type: string
          description: The trademark text that matches the domain
          example: TikTok
        holder:
          type: string
          description: The entity that holds the trademark
          example: ByteDance Ltd.
        jurisdiction:
          type: string
          description: The jurisdiction where the trademark is registered
          example: US
        registrationNumber:
          type: string
          description: The trademark registration number
          example: US123456789
        description:
          type: string
          description: Additional description of the trademark
          example: Social media platform trademark
        noticeHtml:
          type: string
          description: HTML content to display about this specific trademark claim
          example: >-
            <div class='trademark-notice'>This domain may infringe on the TikTok
            trademark held by ByteDance Ltd.</div>
        confidence:
          type: number
          format: float
          minimum: 0
          maximum: 1
          description: Confidence score for the trademark match (0.0 to 1.0)
          example: 0.95
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