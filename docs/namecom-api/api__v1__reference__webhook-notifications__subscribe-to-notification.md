> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Subscribe to Notification

> Creates a webhook subscription to receive real-time notifications about specific domain or account events (e.g. transfer completions, renewals). Pass the callback URL and event types. This allows external systems to stay in sync with name.com changes.
Supported webhook event names:
- `account.credit.balance_change` – account credit balance changes (increases or decreases).
- `account.domain.removal` – domain removed from the subscribing account.
- `domain.lock.status_change` – domain lock added or removed.
- `domain.transfer.status_change` – domain transfer IN to name.com; status updates while name.com is the gaining registrar.
- `domain.transfer_out.status_change` – domain transfer OUT from name.com; `initiated`, `completed` (domain removed), or `canceled` (no longer pending at the registry).
- `domain.transfer.internal_in` - name.com domain transfers in to the subscribing account via internal transfer.
- `domain.transfer.internal_out` - name.com domain transfers out of the subscribing account via internal transfer.
- `contact.verification.status_change` - contact verification status changes (verified or unverified).
- `domain.registry.rejection` – domain **create** failed after asynchronous registry processing (uncommon; most creates succeed at request time).
- `domain.expiration` – domain has expired and entered the post-expiry grace period. This is informational only.



## OpenAPI

````yaml post /core/v1/notifications
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
  /core/v1/notifications:
    post:
      tags:
        - Webhook Notifications
      summary: Subscribe to Notification
      description: >-
        Creates a webhook subscription to receive real-time notifications about
        specific domain or account events (e.g. transfer completions, renewals).
        Pass the callback URL and event types. This allows external systems to
        stay in sync with name.com changes.

        Supported webhook event names:

        - `account.credit.balance_change` – account credit balance changes
        (increases or decreases).

        - `account.domain.removal` – domain removed from the subscribing
        account.

        - `domain.lock.status_change` – domain lock added or removed.

        - `domain.transfer.status_change` – domain transfer IN to name.com;
        status updates while name.com is the gaining registrar.

        - `domain.transfer_out.status_change` – domain transfer OUT from
        name.com; `initiated`, `completed` (domain removed), or `canceled` (no
        longer pending at the registry).

        - `domain.transfer.internal_in` - name.com domain transfers in to the
        subscribing account via internal transfer.

        - `domain.transfer.internal_out` - name.com domain transfers out of the
        subscribing account via internal transfer.

        - `contact.verification.status_change` - contact verification status
        changes (verified or unverified).

        - `domain.registry.rejection` – domain **create** failed after
        asynchronous registry processing (uncommon; most creates succeed at
        request time).

        - `domain.expiration` – domain has expired and entered the post-expiry
        grace period. This is informational only.
      operationId: SubscribeToNotification
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SubscribeToNotification'
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SubscribeToNotificationResponse'
          description: A successful response.
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
        '409':
          description: >-
            The API will return this response if you are attempting to subscribe
            to a webhook you have already subscribed to.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Conflict409'
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
    SubscribeToNotification:
      description: Request to subscribe to a specific webhook notification
      properties:
        eventName:
          $ref: '#/components/schemas/AvailableWebhooks'
        url:
          type: string
          description: The URL we will send the notification data to
          example: https://example.com
        active:
          type: boolean
          description: >-
            If the webhook should be active. This allows a webhook to be
            deactivated in our system. It may be useful to deactivate a webhook
            if the server that receives the POST request is undergoing scheduled
            maintenance, for example.
      required:
        - eventName
        - url
        - active
    SubscribeToNotificationResponse:
      properties:
        subscription:
          $ref: '#/components/schemas/SubscriptionRecord'
      title: Response from subscribing to a notification
      type: object
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
    AvailableWebhooks:
      description: The list of configured webhooks you can subscribe to
      type: string
      enum:
        - account.credit.balance_change
        - account.domain.removal
        - domain.lock.status_change
        - domain.transfer.status_change
        - domain.transfer_out.status_change
        - contact.verification.status_change
        - domain.transfer.internal_in
        - domain.transfer.internal_out
        - domain.registry.rejection
        - domain.expiration
    SubscriptionRecord:
      properties:
        active:
          title: Whether or not the subscription is active
          type: boolean
        createDate:
          title: Date the subscription record was created (Date you subscribed)
          type: string
        eventName:
          title: The name of the event you have subscribed to
          type: string
        id:
          format: int32
          title: The ID of the event record. Used for updating and canceling
          type: integer
        updateDate:
          title: Date the subscription record was updated (Date you made changes)
          type:
            - string
            - 'null'
        url:
          title: The URL we will send a POST request to with the notification message
          type: string
      required:
        - active
        - id
        - createDate
        - eventName
        - url
        - updateDate
      title: |-
        *
        The record for each notification you have subscribed to
      type: object
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