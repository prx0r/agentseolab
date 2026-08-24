> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Update Record

> Replaces an existing DNS record with new data. This is a full overwrite — all required fields (host, type, answer, ttl) must be included in the request body. If you omit a field, the existing value will not be preserved and the request may fail. Use [GetRecord](/api/v1/reference/dns/get-record) beforehand to retrieve the current values if you intend to modify just one field. The record ID must belong to a domain you manage.



## OpenAPI

````yaml put /core/v1/domains/{domainName}/records/{id}
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
  /core/v1/domains/{domainName}/records/{id}:
    put:
      tags:
        - DNS
      summary: Update Record
      description: >-
        Replaces an existing DNS record with new data. This is a full overwrite
        — all required fields (host, type, answer, ttl) must be included in the
        request body. If you omit a field, the existing value will not be
        preserved and the request may fail. Use
        [GetRecord](/api/v1/reference/dns/get-record) beforehand to retrieve the
        current values if you intend to modify just one field. The record ID
        must belong to a domain you manage.
      operationId: UpdateRecord
      parameters:
        - description: DomainName is the zone that the record belongs to.
          in: path
          name: domainName
          required: true
          schema:
            type: string
        - description: >-
            Unique record id. Value is ignored on Create, and must match the URI
            on Update.
          in: path
          name: id
          required: true
          schema:
            type: integer
            format: int32
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DNSUpdateRecordBody'
        required: true
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Record'
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
        '404':
          description: Domain or DNS record not found.
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
    DNSUpdateRecordBody:
      description: Record is an individual DNS resource record.
      type: object
      properties:
        answer:
          description: >-
            Answer is either the IP address for A or AAAA records; the target
            for ANAME, CNAME, MX, or NS records; the text for TXT records.

            For SRV records, answer has the following format: "{weight} {port}
            {target}" e.g. "1 5061 sip.example.org".
          type: string
          minLength: 1
        fqdn:
          description: >-
            FQDN is the Fully Qualified Domain Name. It is the combination of
            the host and the domain name. It always ends in a ".". FQDN is
            ignored in CreateRecord, specify via the Host field instead.
          type: string
        host:
          description: >-
            Host is the hostname relative to the zone: e.g. for a record for
            blog.example.org, domain would be "example.org" and host would be
            "blog".

            An apex record would be specified by either an empty host "" or "@".

            A SRV record would be specified by "_{service}._{protocol}.{host}":
            e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
          type: string
        priority:
          description: >-
            Priority is only required for MX and SRV records, it is ignored for
            all others.
          format: int64
          type: integer
        ttl:
          description: >-
            TTL is the time this record can be cached for in seconds. name.com
            allows a minimum TTL of 300, or 5 minutes.
          format: int64
          type: integer
        type:
          description: >-
            Type is one of the following: A, AAAA, ANAME, CNAME, MX, NS, SRV, or
            TXT.
          type: string
          enum:
            - A
            - AAAA
            - ANAME
            - CNAME
            - MX
            - NS
            - SRV
            - TXT
      required:
        - type
        - answer
    Record:
      description: Record is an individual DNS resource record.
      type: object
      properties:
        answer:
          description: >-
            Answer is either the IP address for A or AAAA records; the target
            for ANAME, CNAME, MX, or NS records; the text for TXT records.

            For SRV records, answer has the following format: "{weight} {port}
            {target}" e.g. "1 5061 sip.example.org".
          type: string
        domainName:
          description: DomainName is the zone that the record belongs to.
          type: string
        fqdn:
          description: >-
            FQDN is the Fully Qualified Domain Name. It is the combination of
            the host and the domain name. It always ends in a ".". FQDN is
            ignored in CreateRecord, specify via the Host field instead.
          type: string
          readOnly: true
        host:
          description: >-
            Host is the hostname relative to the zone: e.g. for a record for
            blog.example.org, domain would be "example.org" and host would be
            "blog".

            An apex record would be specified by either an empty host "" or "@".

            A SRV record would be specified by "_{service}._{protocol}.{host}":
            e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
          type:
            - string
            - 'null'
        id:
          description: >-
            Unique record id. Value is ignored on Create, and must match the URI
            on Update.
          format: int32
          type: integer
          readOnly: true
        priority:
          description: >-
            Priority is only required for MX and SRV records, it is ignored for
            all others.
          format: int64
          type: integer
        ttl:
          description: >-
            TTL is the time this record can be cached for in seconds. name.com
            allows a minimum TTL of 300, or 5 minutes.
          format: int64
          type: integer
        type:
          description: >-
            Type is one of the following: A, AAAA, ANAME, CNAME, MX, NS, SRV, or
            TXT.
          type:
            - string
            - 'null'
      required:
        - type
        - ttl
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