> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# List URLForwardings

> Returns all URL forwarding settings configured for a domain. **Deprecated.** Use [List URL Forwardings by domain](/api/v1/reference/url-forwardings/list-urlforwardings-by-domain) instead, which returns entries with an `id` for use with by-ID endpoints.



## OpenAPI

````yaml get /core/v1/domains/{domainName}/url/forwarding
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
  /core/v1/domains/{domainName}/url/forwarding:
    get:
      tags:
        - URL Forwardings
      summary: List URLForwardings
      description: >-
        Returns all URL forwarding settings configured for a domain.
        **Deprecated.** Use [List URL Forwardings by
        domain](/api/v1/reference/url-forwardings/list-urlforwardings-by-domain)
        instead, which returns entries with an `id` for use with by-ID
        endpoints.
      operationId: ListURLForwardings
      parameters:
        - description: DomainName is the domain to list URL forwarding entries for.
          in: path
          name: domainName
          required: true
          schema:
            type: string
            example: example.com
            format: hostname
        - description: >-
            Per Page is the number of records to return per request. Per Page
            defaults to 500.
          in: query
          name: perPage
          schema:
            allOf:
              - $ref: '#/components/schemas/PerPageLimit'
              - default: 500
                example: 100
        - description: Page is which page to return. Starts at 1 for first page.
          in: query
          name: page
          schema:
            format: int32
            type: integer
            default: 1
            minimum: 1
            example: 1
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ListURLForwardingsResponse'
          headers:
            Link:
              description: String delimited list of links for pagination
              schema:
                type: string
                example: >-
                  <https://api.dev.name.com?page=3;
                  rel="next">,<https://api.dev.name.com?page=1;
                  rel="prev">,<https://api.dev.name.com?page=10; rel="last">
          description: A successful response containing the list of URL forwarding entries.
        '400':
          description: Bad Request - Invalid parameters or malformed request.
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
          description: Domain not found or not owned by the authenticated account.
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
      deprecated: true
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
    ListURLForwardingsResponse:
      description: >-
        ListURLForwardingsResponse is the response for the ListURLForwardings
        function.
      type: object
      properties:
        lastPage:
          description: >-
            LastPage is the identifier for the final page of results. It is only
            populated if there is another page of results after the current
            page.
          format: int32
          type:
            - integer
            - 'null'
          example: 5
          minimum: 0
        nextPage:
          description: >-
            NextPage is the identifier for the next page of results. It is only
            populated if there is another page of results after the current
            page.
          format: int32
          type:
            - integer
            - 'null'
          example: 2
          minimum: 0
        urlForwarding:
          description: URLForwarding is the list of URL forwarding entries.
          items:
            $ref: '#/components/schemas/URLForwardingResponse'
          type: array
          example: []
          minItems: 0
      required:
        - urlForwarding
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
    URLForwardingResponse:
      description: >-
        URLForwarding represents a URL forwarding entry response, allowing a
        domain to redirect to another URL using different forwarding methods.
      allOf:
        - $ref: '#/components/schemas/URLForwarding'
        - type: object
          properties:
            id:
              description: >-
                Server-assigned unique identifier for the URL forwarding record.
                Use this ID with the URL Forwarding by-ID endpoints to get,
                update, or delete records.
              type: integer
              format: int32
              example: 12345
            host:
              title: The subdomain portion of the hostname
              description: The subdomain portion of the hostname that is being forwarded.
              type: string
              example: www
    URLForwarding:
      description: >-
        URLForwarding represents a URL forwarding entry, allowing a domain to
        redirect to another URL using different forwarding methods.
      type: object
      required:
        - host
        - forwardsTo
        - type
      properties:
        domainName:
          description: The domain name (without subdomains) that is being forwarded.
          type: string
          format: hostname
          example: example.org
        forwardsTo:
          description: The destination URL to which this hostname will be forwarded.
          type: string
          format: uri
          example: https://destination-site.com
        host:
          title: The subdomain portion of the hostname
          description: The subdomain portion of the hostname that is being forwarded.
          type: string
          example: www
        meta:
          description: >
            Meta tags to include in the HTML page when using "masked"
            forwarding.

            Ignored for other forwarding types.

            Example: `<meta name='keywords' content='fish, denver, platte'>`
          type:
            - string
            - 'null'
          example: <meta name='keywords' content='website, forwarding, masked'>
        title:
          description: >
            The title to be used for the HTML page when using "masked"
            forwarding.

            Ignored for other forwarding types.
          type:
            - string
            - 'null'
          example: Welcome to my forwarded website
        type:
          description: |
            The type of URL forwarding. Valid values:
              - `masked`: Retains the original domain in the address bar, preventing the user from seeing the actual destination URL. Sometimes called iframe forwarding.
              - `redirect`: Uses a standard HTTP redirect (301), which changes the address bar to the destination URL.
              - `302`: Uses a temporary HTTP redirect (302), which changes the address bar to the destination URL but indicates the resource is temporarily located elsewhere.
          type: string
          enum:
            - masked
            - redirect
            - '302'
          example: redirect
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