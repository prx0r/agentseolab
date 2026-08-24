> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Order

> Fetches full details about a specific order using its ID. This includes domains, prices, and timestamps.  Useful for confirming transactions, receipts, or generating invoices.



## OpenAPI

````yaml get /core/v1/orders/{orderId}
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
  /core/v1/orders/{orderId}:
    get:
      tags:
        - Orders
      summary: Get Order
      description: >-
        Fetches full details about a specific order using its ID. This includes
        domains, prices, and timestamps.  Useful for confirming transactions,
        receipts, or generating invoices.
      operationId: GetOrder
      parameters:
        - description: OrderId is the unique identifier of the requested order.
          in: path
          name: orderId
          required: true
          schema:
            type: integer
            format: int32
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
          description: A successful response.
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
          description: Order not found.
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
    Order:
      description: Order contains all the data for an order.
      properties:
        authAmount:
          description: AuthAmount is the amount authorized to complete the order purchase.
          format: float
          type: number
        createDate:
          description: CreateDate is the date the order was placed.
          type: string
        currency:
          description: Currency indicates currency of the order ('USD', 'CNY').
          type: string
        currencyRate:
          description: >-
            CurrencyRate is the conversion rate from USD to order's currency. 
            This field is only populated if order's currency is non-USD.
          format: float
          type: number
        finalAmount:
          description: >-
            FinalAmount is the final amount of the order, after discounts and
            refunds.
          type: number
          format: float
        id:
          format: int32
          type: integer
          title: Id is the unique identifier of the order.
        orderItems:
          description: OrderItems is the collection of 1 or more items in the order.
          items:
            $ref: '#/components/schemas/OrderItem'
          type: array
        registrar:
          description: Registrar is registrar with which order is placed.
          type: string
        status:
          description: Status indicates the state of the order ('success', 'failed').
          type: string
        totalCapture:
          description: TotalCapture is the amount captured.
          format: float
          type: number
          example: 10.95
        totalRefund:
          description: TotalRefund is the amount, if any, refunded. Default is 0.00.
          format: float
          type: number
          example: 10.95
      type: object
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
    OrderItem:
      description: OrderItem contains all the order item data.
      properties:
        duration:
          description: Duration is the number of intervals.
          format: int32
          type: integer
        id:
          format: int32
          type: integer
          title: Id is the unique identifier of the order item.
        interval:
          description: >-
            Interval is the  unit of time ("year", "month"). May be null for
            items that have no applicable interval.
          type:
            - string
            - 'null'
        name:
          description: Name is name of the item ('example.ninja').
          type:
            - string
            - 'null'
        originalPrice:
          description: OriginalPrice is the original price of the item before discounts.
          format: float
          type:
            - number
            - 'null'
        price:
          description: Price is the final price of the item.
          format: float
          type: number
        priceNonUsd:
          description: PriceNonUsd is the price of the item if order has non-usd currency.
          format: float
          type: number
        quantity:
          description: Quantity is the number of items.
          format: int32
          type: integer
        status:
          description: >-
            Status indicates state of the order ('success', 'failed',
            'refunded').
          type: string
        taxAmount:
          description: TaxAmount is the tax charged for this item, if applicable.
          format: float
          type:
            - number
            - 'null'
        tld:
          description: Tld is (optional) tld of domain name, if applicable ('ninja').
          type:
            - string
            - 'null'
        type:
          description: Type is type of  the item ('registration', 'whois_privacy').
          type: string
        isRefundable:
          description: >-
            IsRefundable indicates whether the item in your order is currently
            eligible for a refund through the refund endpoint based on
            name.com's refund rules. These refunds are only applicable for
            invalid or fraudulent orders within a few days or registration
            (usually 5).
          type: boolean
          example: true
          default: false
      type: object
      required:
        - duration
        - id
        - interval
        - name
        - originalPrice
        - price
        - quantity
        - status
        - type
        - isRefundable
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