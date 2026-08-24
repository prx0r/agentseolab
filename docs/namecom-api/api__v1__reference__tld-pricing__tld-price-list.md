> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# TLD Price List

> This endpoint returns an alphabetical list of all TLDs supported by name.com, including pricing for each supported order type. All prices are in US Dollars (USD) and apply to non-premium domains. name.com provides three pricing types for each TLD:
- Account-Level Pricing - Your price, including any applicable rebates, promotions, or account-level discounts. This is referenced as 'registrationprice', 'renewalprice', 'transferinprice' and 'domainrestorationprice' in this endpoint.
- Original Pricing (No Discounts Applied) - The suggested retail price (MSRP) before any discounts are applied.
- Retail Pricing (Public Site Pricing) - The current public retail price on name.com, including any public rebates or promotions, but before any account-level discounts.

**Important Notes:**
- Promo codes are not supported through the API, and therefore are not reflected in any pricing values returned.
- General TLD pricing only: This represents standard pricing for domains registered under the specified TLD. Pricing for specific domains may differ based on multiple factors (e.g., premium classifications, registry pricing rules). To retrieve pricing for an individual domain, use the GetPricingForDomain endpoint.
- Availability: If a pricing value is returned as null, that product type is not currently supported for the TLD. (Example: registrationPrice = null means registrations are not currently available.)
- If you do not have account level pricing, the retail price will always match your account level price. (e.g., registration price = registration retail price)




## OpenAPI

````yaml get /core/v1/tldpricing
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
  /core/v1/tldpricing:
    get:
      tags:
        - TLD Pricing
      summary: TLD Price List
      description: >
        This endpoint returns an alphabetical list of all TLDs supported by
        name.com, including pricing for each supported order type. All prices
        are in US Dollars (USD) and apply to non-premium domains. name.com
        provides three pricing types for each TLD:

        - Account-Level Pricing - Your price, including any applicable rebates,
        promotions, or account-level discounts. This is referenced as
        'registrationprice', 'renewalprice', 'transferinprice' and
        'domainrestorationprice' in this endpoint.

        - Original Pricing (No Discounts Applied) - The suggested retail price
        (MSRP) before any discounts are applied.

        - Retail Pricing (Public Site Pricing) - The current public retail price
        on name.com, including any public rebates or promotions, but before any
        account-level discounts.


        **Important Notes:**

        - Promo codes are not supported through the API, and therefore are not
        reflected in any pricing values returned.

        - General TLD pricing only: This represents standard pricing for domains
        registered under the specified TLD. Pricing for specific domains may
        differ based on multiple factors (e.g., premium classifications,
        registry pricing rules). To retrieve pricing for an individual domain,
        use the GetPricingForDomain endpoint.

        - Availability: If a pricing value is returned as null, that product
        type is not currently supported for the TLD. (Example: registrationPrice
        = null means registrations are not currently available.)

        - If you do not have account level pricing, the retail price will always
        match your account level price. (e.g., registration price = registration
        retail price)
      operationId: TldPriceList
      parameters:
        - description: >-
            Per Page is the number of records to return per request. Per Page
            defaults to 25.
          in: query
          name: perPage
          schema:
            allOf:
              - $ref: '#/components/schemas/PerPageLimit'
              - default: 25
        - name: page
          description: Page is which page to return.
          in: query
          schema:
            format: int32
            type: integer
            default: 1
            minimum: 1
        - name: duration
          description: >-
            The number of years to get pricing for. The requested duration must
            be between 1 and 10 (inclusive). If the duration is not passed in
            the request, it will default to 1.
          required: false
          in: query
          schema:
            type: integer
            format: int32
            minimum: 1
            maximum: 10
            example: 1
            default: 5
        - name: tlds
          description: >-
            A list of specific TLDs to get pricing for. Maximum of 25 TLDs can
            be requested at a time.  When querying for IDN TLDs, due to
            character restrictions within a URL, they must be submitted in ASCII
            format.  This means using "xn--9dbq2a" as opposed to it's unicode
            equivalent. The submitted TLDs will be checked for validity and
            support at name.com, and any invalid TLD will be removed from the
            submitted list. If all submitted TLDs are invalid or not supported
            by name.com, this will be considered a bad request, and a `400 Bad
            Request` will be returned with an appropriate message.
          in: query
          required: false
          schema:
            type: array
            minItems: 1
            maxItems: 25
            items:
              type: string
              minLength: 1
            example:
              - com
              - net
              - org
          style: form
          explode: true
      responses:
        '200':
          description: A successful response.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TldPriceListResponse'
        '400':
          description: Bad request - Invalid query parameters.
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
    PerPageLimit:
      description: >-
        Maximum number of records to return per page for paginated list
        endpoints.
      type: integer
      format: int32
      minimum: 1
      maximum: 1000
    TldPriceListResponse:
      properties:
        lastPage:
          description: >-
            LastPage is the identifier for the final page of results. It is only
            populated if there is another page of results after the current
            page.
          format: int32
          type: integer
        nextPage:
          description: >-
            NextPage is the identifier for the next page of results. It is only
            populated if there is another page of results after the current
            page.
          format: int32
          type:
            - integer
            - 'null'
        totalCount:
          description: TotalCount is total number of results.
          format: int32
          type: integer
        from:
          description: From specifies starting record number on current page.
          format: int32
          type: integer
        to:
          description: To specifies ending record number on current page.
          format: int32
          type: integer
        pricing:
          type: array
          items:
            $ref: '#/components/schemas/TldPriceListEntry'
      type: object
      required:
        - lastPage
        - nextPage
        - totalCount
        - from
        - to
        - pricing
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
    TldPriceListEntry:
      description: >
        The pricing for an individual TLD.


        Please note that if `null` is returned for any of the prices, it means
        that particular product is unavailable at name.com.


        For example, if `registrationPrice` returns as `null` in the response,
        it means that name.com is not currently accepting registrations for that
        TLD.
      properties:
        tld:
          description: >-
            The TLD the pricing applies to. For IDN TLDs, this will be the
            unicode representation of the TLD.
          type: string
          example: com
        duration:
          description: The number of years this pricing is for
          type: integer
          format: int32
          example: 1
        registrationPrice:
          description: >-
            This is your account level price in US Dollars (USD) and is the
            price you pay for non-premium registrations. It includes applicable
            rebates, promotions and/or account-level discounts.
          type:
            - number
            - 'null'
          format: double
          example: 9.99
        registrationRetailPrice:
          description: >-
            This is the current retail price on name.com in US Dollars (USD)
            after including rebates, promotions and/or sales for registering
            non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 10.99
        registrationOriginalPrice:
          description: >-
            This is name.com's suggested retail price (MSRP) in US Dollars (USD)
            before any discounts for registering non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 11.99
        renewalPrice:
          description: >-
            This is your account level price in US Dollars (USD) and is the
            price you pay for non-premium renewals. It includes applicable
            rebates, promotions and/or account-level discounts.
          type:
            - number
            - 'null'
          format: double
          example: 9.99
        renewalRetailPrice:
          description: >-
            This is the current retail price on name.com in US Dollars (USD)
            after including rebates, promotions and/or sales for renewals of
            non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 10.99
        renewalOriginalPrice:
          description: >-
            This is name.com's suggested retail price (MSRP) in US Dollars (USD)
            before any discounts for renewals of non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 11.99
        domainRestorationPrice:
          description: >-
            This is your account level price in US Dollars (USD) and is the
            price you pay for non-premium restorations. It includes applicable
            rebates, promotions and/or account-level discounts.
          type:
            - number
            - 'null'
          format: double
          example: 120.99
        domainRestorationRetailPrice:
          description: >-
            This is the current retail price on name.com in US Dollars (USD)
            after including rebates, promotions and/or sales for restorations of
            non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 130.99
        domainRestorationOriginalPrice:
          description: >-
            This is name.com's suggested retail price (MSRP) in US Dollars (USD)
            before any discounts for restoration of non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 140.99
        transferInPrice:
          description: >-
            This is your account level price in US Dollars (USD) and is the
            price you pay for non-premium transfers. It includes applicable
            rebates, promotions and/or account-level discounts.
          type:
            - number
            - 'null'
          format: double
          example: 19.99
        transferInRetailPrice:
          description: >-
            This is the current retail price on name.com in US Dollars (USD)
            after including rebates, promotions and/or sales for transfers of
            non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 20.99
        transferInOriginalPrice:
          description: >-
            This is name.com's suggested retail price (MSRP) in US Dollars (USD)
            before any discounts for transfer of non-premium domains.
          type:
            - number
            - 'null'
          format: double
          example: 21.99
      required:
        - tld
        - duration
        - registrationPrice
        - registrationRetailPrice
        - registrationOriginalPrice
        - renewalPrice
        - renewalRetailPrice
        - renewalOriginalPrice
        - domainRestorationPrice
        - domainRestorationRetailPrice
        - domainRestorationOriginalPrice
        - transferInPrice
        - transferInRetailPrice
        - transferInOriginalPrice
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