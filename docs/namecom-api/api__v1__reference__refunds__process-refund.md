> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Process Refund

> Deletes eligible domains and security products during the Add Grace Period (AGP) and automatically issues refunds for the associated order items.

### Eligibility Requirements

- **Product Types**: Only `registration` and `whois_privacy` product types are eligible for refunds.
- **AGP Timing**: Items must be within the Add Grace Period (typically 5 days from registration, varies by TLD).
- **Order Ownership**: All `orderItemIds` must belong to the specified `orderId`.

### Refund Processing

Refunds are processed in the following order:
1. Domain deletion is attempted for each eligible order item
2. Upon successful deletion, the refund is issued
3. Refunds are sent to the original payment method on file
4. If the original payment method is unavailable, the refund is credited to the account balance

### Idempotency

This endpoint supports idempotent requests via the `X-Idempotency-Key` header. If you retry a request with the same idempotency key, you will receive the same response as the original request. This is useful for safely retrying requests without risk of processing duplicate refunds.




## OpenAPI

````yaml post /core/v1/refund
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
  /core/v1/refund:
    post:
      tags:
        - Refunds
      summary: Process Refund
      description: >
        Deletes eligible domains and security products during the Add Grace
        Period (AGP) and automatically issues refunds for the associated order
        items.


        ### Eligibility Requirements


        - **Product Types**: Only `registration` and `whois_privacy` product
        types are eligible for refunds.

        - **AGP Timing**: Items must be within the Add Grace Period (typically 5
        days from registration, varies by TLD).

        - **Order Ownership**: All `orderItemIds` must belong to the specified
        `orderId`.


        ### Refund Processing


        Refunds are processed in the following order:

        1. Domain deletion is attempted for each eligible order item

        2. Upon successful deletion, the refund is issued

        3. Refunds are sent to the original payment method on file

        4. If the original payment method is unavailable, the refund is credited
        to the account balance


        ### Idempotency


        This endpoint supports idempotent requests via the `X-Idempotency-Key`
        header. If you retry a request with the same idempotency key, you will
        receive the same response as the original request. This is useful for
        safely retrying requests without risk of processing duplicate refunds.
      operationId: ProcessRefund
      parameters:
        - name: X-Idempotency-Key
          in: header
          description: >-
            A unique string (e.g., a UUID v4) to make the request idempotent.
            This key ensures that if the request is retried, the operation will
            not be performed multiple times. Subsequent requests with the same
            key will return the original result. Idempotency keys are valid for
            1 hour.
          schema:
            type: string
            example: 083910ef-04e4-4bd1-a0bf-3737fe005ca8
          required: false
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RefundRequest'
            examples:
              singleItem:
                summary: Refund a single order item
                description: >-
                  Request to refund a single domain registration from an order. 
                  If there is a security product associated with the domain, it
                  will also be refunded.
                value:
                  orderId: 123456
                  orderItemIds:
                    - 987654
              multipleItems:
                summary: Refund multiple order items
                description: >-
                  Request to refund multiple items (e.g., domain registration
                  and security product) from a single order.
                value:
                  orderId: 123456
                  orderItemIds:
                    - 987654
                    - 987655
        description: >-
          RefundRequest contains the order ID and array of order item IDs to be
          refunded.
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
                $ref: '#/components/schemas/RefundResponse'
              examples:
                successfulRefund:
                  summary: Successful refund of domain registration
                  value:
                    results:
                      - orderId: 123456
                        orderItemId: 987654
                        orderItemStatus: refunded
                        refundAmount: 10.99
                        message: Domain successfully deleted and refund processed.
                    totalRefundAmount: 10.99
          description: >-
            Refund processed successfully. The response includes the detailed
            results for each refunded item.
        '400':
          description: >-
            Bad request - Invalid input data or order item has already been
            refunded.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
              examples:
                alreadyRefunded:
                  summary: Order item already refunded
                  value:
                    message: Bad Request
                    details: Order item 987654 has already been refunded.
                invalidProductType:
                  summary: Invalid product type
                  value:
                    message: Bad Request
                    details: >-
                      Order item 987654 is not eligible for refund. Only
                      'registration' and 'whois_privacy' product types are
                      supported.
                emptyOrderItems:
                  summary: Empty order items array
                  value:
                    message: Bad Request
                    details: orderItemIds array must contain at least one item.
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
          description: >-
            Not Found - Order ID or order item ID does not exist, or order items
            do not belong to the specified order.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotFound404'
              examples:
                orderNotFound:
                  summary: Order not found
                  value:
                    message: Not Found
                    details: Order with ID 123456 does not exist.
                itemNotFound:
                  summary: Order item not found
                  value:
                    message: Not Found
                    details: >-
                      Order item 987654 does not exist or does not belong to
                      order 123456.
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
            Conflict - Idempotency key reused for different request, or AGP
            delete threshold exceeded.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Conflict409'
              examples:
                idempotencyConflict:
                  summary: Idempotency key reused
                  value:
                    message: Conflict
                    details: Idempotency key has been reused for a different request.
                thresholdExceeded:
                  summary: AGP threshold exceeded
                  value:
                    message: Conflict
                    details: >-
                      AGP delete threshold has been exceeded for this account.
                      Please contact support.
        '415':
          description: >-
            Unsupported Media Type - All POST requests must include the
            `Content-Type: application/json` header.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnsupportedMedia415'
        '423':
          description: >-
            Locked - The deletion timing is outside registry limits. The Add
            Grace Period (AGP) has expired for one or more items.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Locked423'
              examples:
                agpExpired:
                  summary: AGP window expired
                  value:
                    message: Resource Locked
                    details: >-
                      The Add Grace Period (AGP) deletion window has expired for
                      domain example.com. AGP deletes are only allowed within 5
                      days of registration.
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
            Bad Gateway - Registry connection unavailable or registry-related
            problem occurred.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/BadGateway502'
              examples:
                registryError:
                  summary: Registry connection error
                  value:
                    message: Registry Connection Unavailable
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
    RefundRequest:
      description: >-
        RefundRequest contains the order and order items to be refunded. Only
        domain registrations and security products purchased within the Add
        Grace Period (AGP) are eligible for refunds.
      type: object
      required:
        - orderId
        - orderItemIds
      properties:
        orderId:
          type: integer
          format: int32
          description: >-
            The unique identifier of the order containing the item(s) to be
            refunded. Use the List Orders endpoint to retrieve order IDs.
          example: 123456
        orderItemIds:
          type: array
          items:
            type: integer
            format: int32
          minItems: 1
          description: >
            An array of order item IDs to be refunded. All items must belong to
            the specified order. Use the List Orders endpoint to retrieve order
            item IDs.
          example:
            - 987654
            - 987655
    RefundResponse:
      description: >
        RefundResponse contains the results of a refund operation, including the
        individual order item results.

        Refunds are issued to the original payment method on file. If the
        original payment method is unavailable, the refund will be credited to
        the account balance.
      type: object
      required:
        - results
        - totalRefundAmount
      properties:
        results:
          type: array
          items:
            $ref: '#/components/schemas/RefundItemResult'
          description: An array of refund results for each order item that was processed.
          minItems: 1
        totalRefundAmount:
          type: number
          format: float
          description: The total amount refunded across all order items in USD.
          example: 21.98
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
    Conflict409:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Conflict
        details:
          type: string
          description: Additional context or information about the pricing error
          example: >-
            You are attempting to subscribe to an event you have already
            subscribed to.
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
    Locked423:
      type: object
      description: >-
        Error response returned when a resource is locked and cannot be
        modified. Used when the Add Grace Period (AGP) deletion window has
        expired.
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Resource Locked
        details:
          type:
            - string
            - 'null'
          description: Additional context or information about the error
          example: >-
            The Add Grace Period (AGP) deletion window has expired for this
            domain.
    BadGateway502:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: A human-readable message providing more details about the error
          example: Registry Connection Unavailable
    RefundItemResult:
      description: >-
        RefundItemResult contains the result of a refund operation for a single
        order item.
      type: object
      required:
        - orderId
        - orderItemId
        - orderItemStatus
        - refundAmount
      properties:
        orderId:
          type: integer
          format: int32
          description: The unique identifier of the Order that was processed.
          example: 987654
        orderItemId:
          type: integer
          format: int32
          description: The unique identifier of the Order Item that was processed.
          example: 987654
        orderItemStatus:
          type: string
          description: The status of the refund operation for this item.
          enum:
            - refunded
            - failed
            - initialized
            - canceled
          example: refunded
        refundAmount:
          type: number
          format: float
          description: The amount refunded for this order item in USD.
          example: 10.99
        message:
          type:
            - string
            - 'null'
          description: >-
            Additional information about the refund result, especially useful
            for failed items.
          example: Domain successfully deleted and refund processed.
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