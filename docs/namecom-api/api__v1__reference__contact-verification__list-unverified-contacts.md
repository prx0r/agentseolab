> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# List Unverified Contacts

> Returns a list of contacts, related to domains within your account, that require verification as per ICANN procedures.
When a new domain is created, unverified contacts are not immediately available in API responses.  Records are added by a scheduled process that runs approximately every 10 minutes.  As a result, there may be up to a 10-minute delay before unverified contacts appear in the API. This delay also applies to related events such as webhooks or other downstream systems that depend on contact verification data. 



## OpenAPI

````yaml get /core/v1/contacts/unverified
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
  /core/v1/contacts/unverified:
    get:
      tags:
        - Contact Verification
      summary: List Unverified Contacts
      description: >-
        Returns a list of contacts, related to domains within your account, that
        require verification as per ICANN procedures.

        When a new domain is created, unverified contacts are not immediately
        available in API responses.  Records are added by a scheduled process
        that runs approximately every 10 minutes.  As a result, there may be up
        to a 10-minute delay before unverified contacts appear in the API. This
        delay also applies to related events such as webhooks or other
        downstream systems that depend on contact verification data. 
      operationId: UnverifiedContactsList
      parameters:
        - description: >-
            PerPage is the number of records to return per request. If not
            passed in the request, the default value is 100 records.
          in: query
          name: perPage
          schema:
            allOf:
              - $ref: '#/components/schemas/PerPageLimit'
              - default: 100
                example: 100
        - description: >-
            Page is which page to return. If not passed in the request, the
            default page is 1.
          in: query
          name: page
          schema:
            type: integer
            format: int32
            minimum: 1
            default: 1
            example: 2
      responses:
        '200':
          description: >-
            A successful response containing an array of unverified contacts. 
            This array may be empty if there are no unverified contacts related
            to domains in your account.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnverifiedContactsResponse'
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
    UnverifiedContactsResponse:
      description: A list of unverified contacts that relate to your account.
      type: object
      properties:
        unverifiedContacts:
          type: array
          items:
            $ref: '#/components/schemas/UnverifiedContact'
        from:
          description: From is the starting record for the current page.
          type: integer
          format: int32
          example: 1
        to:
          description: To is the ending record for the current page.
          type: integer
          format: int32
          example: 25
        lastPage:
          description: >-
            LastPage is the identifier for the final page of results. This value
            will be null if there is not a previous result page.
          type: integer
          format: int32
        nextPage:
          description: >-
            NextPage is the identifier for the next page of results. This value
            will be null if there is not a next page of results.
          type:
            - integer
            - 'null'
          format: int32
        totalCount:
          description: TotalCount is total number of domains returned for request.
          format: int32
          type: integer
      required:
        - unverifiedContacts
        - from
        - to
        - lastPage
        - nextPage
        - totalCount
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
    UnverifiedContact:
      type: object
      description: >-
        The pertinent information used to identifiy a domain contact that
        requires verification as per ICANN requirements.
      properties:
        verificationId:
          description: >-
            The id of the verification record for the contact. Please note, this
            is different than the `contact_id` that may be returned in other API
            contexts. This id specifically relates to the verification record
            and will be different than a `contact_id` for the same contact
            record in other contexts.
          type: integer
          format: int64
          example: 4897668
        createDate:
          description: The date the record requiring verification was created.
          type: string
          format: date-time
          example: '2025-01-01T15:35:06Z'
          readOnly: true
        verifyBy:
          description: >-
            The date/time that the contact record **must** be verified by.  If
            the contact record is not verified by this date, the domain may
            become locked by the registry. This is typically 15 days from the
            creation date of the verification record, but may vary by TLD and
            registry.
          type: string
          format: date-time
          example: '2025-01-16T15:35:06Z'
          readOnly: true
        email:
          description: >-
            The email address of the contact to be verified. This is the primary
            identifier used for verification.
          type: string
          format: email
          example: admin@example.com
          readOnly: true
        domains:
          description: >-
            A list of the domains that the contact verification record is
            applied to.
          type: array
          items:
            type: string
            format: hostname
          minItems: 1
      required:
        - verificationId
        - createDate
        - verifyBy
        - email
        - domains
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