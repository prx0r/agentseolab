> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# List Vanity Nameservers

> Lists all vanity nameserver hostnames configured for a domain.



## OpenAPI

````yaml get /core/v1/domains/{domainName}/vanity_nameservers
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
  /core/v1/domains/{domainName}/vanity_nameservers:
    get:
      tags:
        - Vanity Nameservers
      summary: List Vanity Nameservers
      description: Lists all vanity nameserver hostnames configured for a domain.
      operationId: ListVanityNameservers
      parameters:
        - name: domainName
          in: path
          description: The domain name to list vanity nameservers for.
          required: true
          schema:
            type: string
            example: example.com
            format: hostname
        - name: perPage
          in: query
          description: The number of records to return per page. Defaults to 500.
          schema:
            allOf:
              - $ref: '#/components/schemas/PerPageLimit'
              - default: 500
                example: 50
          style: form
          explode: true
        - name: page
          in: query
          description: The page number to return.
          schema:
            type: integer
            format: int32
            minimum: 1
            default: 1
            example: 2
          style: form
          explode: true
      responses:
        '200':
          description: List of vanity nameservers.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ListVanityNameserversResponse'
          headers:
            Link:
              description: String delimited list of links for pagination
              schema:
                type: string
                example: >-
                  <https://api.dev.name.com?page=3;
                  rel="next">,<https://api.dev.name.com?page=1;
                  rel="prev">,<https://api.dev.name.com?page=10; rel="last">
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
        '404':
          description: Domain not found.
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
    PerPageLimit:
      description: >-
        Maximum number of records to return per page for paginated list
        endpoints.
      type: integer
      format: int32
      minimum: 1
      maximum: 1000
    ListVanityNameserversResponse:
      description: >-
        ListVanityNameserversResponse returns the list of vanity nameservers for
        the domain.
      properties:
        lastPage:
          description: >-
            LastPage is the identifier for the final page of results. It is only
            populated if there is another page of results after the current
            page. If no further pages exist, this field will be null.
          type:
            - integer
            - 'null'
          format: int32
          minimum: 1
          example: 5
        nextPage:
          description: >-
            NextPage is the identifier for the next page of results. It is only
            populated if there is another page of results after the current
            page. If no further pages exist, this field will be null.
          type:
            - integer
            - 'null'
          format: int32
          minimum: 1
          example: 2
        vanityNameservers:
          description: >-
            VanityNameservers is the list of vanity nameservers associated with
            the domain. If no vanity nameservers are configured, this will be an
            empty array.
          type: array
          items:
            $ref: '#/components/schemas/VanityNameserverResponse'
          example: []
      type: object
      required:
        - vanityNameservers
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
    VanityNameserverResponse:
      description: VanityNameserver response schema with full hostname
      allOf:
        - $ref: '#/components/schemas/VanityNameserver'
        - type: object
          properties:
            hostname:
              description: >-
                Hostname is the fully qualified domain name (FQDN) of the vanity
                nameserver. It must be a subdomain of the domain specified in
                'domainName'.
              type: string
              format: hostname
              example: ns1.example.com
    VanityNameserver:
      description: >-
        VanityNameserver represents a custom nameserver associated with a
        domain, including its hostname and a list of IP addresses for glue
        records.
      properties:
        domainName:
          description: >-
            DomainName is the root domain for which this vanity nameserver is
            created. For example, if the hostname is 'ns1.example.com', the
            domainName would be 'example.com'.
          type: string
          format: hostname
          example: example.com
        hostname:
          description: >-
            Hostname is the fully qualified domain name (FQDN) of the vanity
            nameserver. It must be a subdomain of the domain specified in
            'domainName'.
          type: string
          format: hostname
          example: ns1.example.com
        ips:
          description: >-
            IPs is a list of IP addresses that are used for glue records for
            this vanity nameserver. These should be valid IPv4 or IPv6
            addresses.
          type: array
          items:
            type: string
            format: ip
          example:
            - 192.168.1.1
            - 2001:0db8:85a3:0000:0000:8a2e:0370:7334
          minItems: 1
      type: object
      required:
        - domainName
        - hostname
        - ips
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