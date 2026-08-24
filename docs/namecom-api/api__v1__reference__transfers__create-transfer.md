> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create External Transfer In

> Initiates a domain transfer into your name.com account from another registrar. You must provide the domain name and its valid transfer authorization code (EPP code). The domain must not be locked or under any transfer restrictions (e.g. clientTransferProhibited). If successful, the transfer is submitted and tracked through the ICANN transfer process. Once a transfer has been created, you can track its progress via the [GetTransfer](/api/v1/reference/transfers/get-transfer) endpoint.
**Transfer pricing:** Omit `purchasePrice` for standard (non-premium) transfers. For premium transfers, pass `transferPrice` from [Get Pricing For Domain](/api/v1/reference/domains/get-pricing-for-domain) as `purchasePrice`. If sent, it must match Get Pricing `transferPrice` exactly or the request will fail. Premium transfers without `purchasePrice` will fail. See the [Domain pricing guide](/guides/domain-pricing) for how [Get Pricing](/api/v1/reference/domains/get-pricing-for-domain) `transferPrice` relates to the `years` query parameter.



## OpenAPI

````yaml post /core/v1/transfers
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
  /core/v1/transfers:
    post:
      tags:
        - Transfers
      summary: Create Transfer
      description: >-
        Initiates a domain transfer into your name.com account from another
        registrar. You must provide the domain name and its valid transfer
        authorization code (EPP code). The domain must not be locked or under
        any transfer restrictions (e.g. clientTransferProhibited). If
        successful, the transfer is submitted and tracked through the ICANN
        transfer process. Once a transfer has been created, you can track its
        progress via the [GetTransfer](/api/v1/reference/transfers/get-transfer)
        endpoint.

        **Transfer pricing:** Omit `purchasePrice` for standard (non-premium)
        transfers. For premium transfers, pass `transferPrice` from [Get Pricing
        For Domain](/api/v1/reference/domains/get-pricing-for-domain) as
        `purchasePrice`. If sent, it must match Get Pricing `transferPrice`
        exactly or the request will fail. Premium transfers without
        `purchasePrice` will fail. See the [Domain pricing
        guide](/guides/domain-pricing) for how [Get
        Pricing](/api/v1/reference/domains/get-pricing-for-domain)
        `transferPrice` relates to the `years` query parameter.
      operationId: CreateTransfer
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTransferRequest'
        description: >-
          CreateTransferRequest passes the required transfer info to the
          CreateTransfer function.
        required: true
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CreateTransferResponse'
          description: A successful response.
        '400':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
              examples:
                premiumPriceRequired:
                  summary: Premium transfer requires purchasePrice
                  value:
                    message: >-
                      PurchasePrice is required if the domain to transfer is a
                      premium domain
                priceMismatch:
                  summary: Transfer price does not match
                  value:
                    message: Invalid Price
          description: >-
            There was an invalid or missing argument in the request. The
            response messages will indicate which fields are invalid.
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
          description: >-
            The account placing the order has insufficient account credit to
            process this transfer order.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericError500'
              example:
                message: Insufficient Funds
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
        '409':
          description: >-
            The status of the domain indicates that we are unable to process a
            transfer for it.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericConflict409'
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
                pricingUnavailable:
                  summary: Pricing unavailable for domain
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
          description: Unable to retrieve domain status due to blocked-hostname.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GatewayTimeout504'
components:
  schemas:
    CreateTransferRequest:
      description: >-
        CreateTransferRequest passes the required transfer info to the
        CreateTransfer function.

        See the [Domain pricing guide](/guides/domain-pricing) for how
        `purchasePrice` relates to [Get
        Pricing](/api/v1/reference/domains/get-pricing-for-domain)
        `transferPrice`.
      properties:
        authCode:
          description: >-
            AuthCode is the authorization code for the transfer. Not all TLDs
            require authorization codes, but most do.
          type: string
          example: ABC123
          minLength: 1
        domainName:
          description: DomainName is the domain you want to transfer to name.com.
          type: string
          example: example.com
          minLength: 1
        privacyEnabled:
          description: >-
            PrivacyEnabled is a flag on whether to purchase Whois Privacy with
            the transfer. If this flag is omitted from the request, the system
            will check the account's Whois Privacy auto-add settings. If
            auto-add is enabled in your account settings, Whois Privacy will be
            added by default, provided the TLD supports it.
          type: boolean
          example: true
        purchasePrice:
          description: >-
            PurchasePrice is the USD inbound transfer fee, before VAT. VAT is
            applied when applicable and must not be included here. If sent, must
            match Get Pricing `transferPrice` exactly or the request will fail..
            **Omit** for standard (non-premium) transfers. **Required** for
            premium transfers — use `transferPrice` from [Get
            Pricing](/api/v1/reference/domains/get-pricing-for-domain).
          format: double
          type: number
          example: 12.99
      type: object
      required:
        - domainName
        - authCode
    CreateTransferResponse:
      description: >-
        CreateTransferResponse returns the newly created transfer resource as
        well as the order information.
      properties:
        order:
          description: Order is an identifier for this purchase.
          format: int32
          type: integer
          example: 12345
        totalPaid:
          description: TotalPaid is the total amount paid, including VAT and Whois Privacy.
          format: double
          type: number
          example: 12.99
        transfer:
          $ref: '#/components/schemas/Transfer'
        warnings:
          description: >-
            Optional transfer warnings surfaced by the API when non-blocking
            registry statuses are detected.
          type: object
          properties:
            message:
              type: string
              description: Brief guidance for resolving potential transfer issues.
              example: >-
                Domain has registry statuses that may prevent a successful
                transfer. Please ensure the domain is unlocked and eligible at
                the losing registrar.
            statuses:
              type: array
              description: Registry status values that triggered the warning.
              items:
                type: string
              example:
                - clientTransferProhibited
                - clientUpdateProhibited
      type: object
      required:
        - order
        - totalPaid
        - transfer
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
    GenericError500:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error.
          example: Internal Server Error
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error.
          example: Something went wrong.
    GenericConflict409:
      type: object
      description: A conflict error response.
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable error message describing the conflict
          example: Object already exists.
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: Cannot create multiple objects under same key.
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
    GatewayTimeout504:
      type: object
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Unable to retrieve domain status
    Transfer:
      description: Transfer contains all relevant data for a domain transfer to name.com.
      type: object
      properties:
        domainName:
          description: DomainName is the domain to be transfered to name.com.
          type: string
          example: example.com
        email:
          description: >-
            Email is the email address that the approval email was sent to. Not
            every TLD requries an approval email. This is usually pulled from
            Whois.
          type: string
          format: email
          example: admin@example.com
        status:
          $ref: '#/components/schemas/TransferStatus'
      required:
        - domainName
        - status
    TransferStatus:
      type: string
      description: >
        Terminal (finished; will not change):

        - **completed**: Completed.

        - **failed**: Failed.

        - **canceled**: Canceled by the user.

        - **canceled_pending_refund**: Canceled; refund processing.


        Non-terminal (in progress; may change):

        - **pending**: Requested.

        - **submitting_transfer**: Being submitted to the registry.

        - **pending_new_auth_code**: New auth code required.

        - **pending_unlock**: Waiting for losing registrar unlock.

        - **pending_registry_unlock**: Waiting for registry unlock.

        - **pending_transfer**: Pending at the registry.

        - **pending_insert**: Transfer complete; domain will be added to the
        account.

        - **rejected**: Rejected at the losing registrar.
      enum:
        - canceled
        - canceled_pending_refund
        - completed
        - failed
        - pending
        - pending_insert
        - pending_new_auth_code
        - pending_registry_unlock
        - pending_transfer
        - pending_unlock
        - rejected
        - submitting_transfer
      example: pending_transfer
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