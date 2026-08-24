> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Internal Transfer In

> Pulls a domain from another [name.com](https://www.name.com) account into your reseller (gaining) account using a valid authorization code. This is an **internal** name.com-to-name.com move; it is separate from [Create Transfer](/api/v1/reference/transfers/create-transfer), which brings domains in from **external** registrars.
Check if a TLD is eligible for internal transfer in by calling [Tld Requirements](/api/v1/reference/domaininfo/requirementsV2) for the TLD and checking property `supportsInternalTransfer`.
This API is only available to approved reseller accounts. Contact name.com support to request access.
#### Losing account (dashboard only)
The party that holds the domain today must use the name.com dashboard on the **losing** account to **unlock** the domain (remove registrar transfer lock) and to **copy the authorization code** to provide to your integration. This endpoint does not unlock the domain or retrieve the auth code for the losing account.
#### Gaining account (this API)
Call this endpoint with `domainName`, `authCode`, and optional `contacts` using the **gaining** reseller's API credentials.
#### Contacts and post-transfer lock
If `contacts` is omitted, the gaining account's default contacts are applied. If `contacts` is provided, any roles included in the request are applied and omitted roles use the gaining account's default contacts (same pattern as [Create Domain](/api/v1/reference/domains/create-domain) and [Set Contacts](/api/v1/reference/domains/set-contacts)). The 60-day contact-change transfer lock is enforced based on the **gaining** account's settings, consistent with Set Contacts.
#### Access
Restricted to approved enterprise resellers; other callers receive `403 Forbidden`.



## OpenAPI

````yaml post /core/v1/transfers/internal/in
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
  /core/v1/transfers/internal/in:
    post:
      tags:
        - Transfers
      summary: Create Internal Transfer In
      description: >-
        Pulls a domain from another [name.com](https://www.name.com) account
        into your reseller (gaining) account using a valid authorization code.
        This is an **internal** name.com-to-name.com move; it is separate from
        [Create Transfer](/api/v1/reference/transfers/create-transfer), which
        brings domains in from **external** registrars.

        Check if a TLD is eligible for internal transfer in by calling [Tld
        Requirements](/api/v1/reference/domaininfo/requirementsV2) for the TLD
        and checking property `supportsInternalTransfer`.

        This API is only available to approved reseller accounts. Contact
        name.com support to request access.

        #### Losing account (dashboard only)

        The party that holds the domain today must use the name.com dashboard on
        the **losing** account to **unlock** the domain (remove registrar
        transfer lock) and to **copy the authorization code** to provide to your
        integration. This endpoint does not unlock the domain or retrieve the
        auth code for the losing account.

        #### Gaining account (this API)

        Call this endpoint with `domainName`, `authCode`, and optional
        `contacts` using the **gaining** reseller's API credentials.

        #### Contacts and post-transfer lock

        If `contacts` is omitted, the gaining account's default contacts are
        applied. If `contacts` is provided, any roles included in the request
        are applied and omitted roles use the gaining account's default contacts
        (same pattern as [Create
        Domain](/api/v1/reference/domains/create-domain) and [Set
        Contacts](/api/v1/reference/domains/set-contacts)). The 60-day
        contact-change transfer lock is enforced based on the **gaining**
        account's settings, consistent with Set Contacts.

        #### Access

        Restricted to approved enterprise resellers; other callers receive `403
        Forbidden`.
      operationId: CreateInternalTransferIn
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateInternalTransferInRequest'
        required: true
      responses:
        '200':
          description: >-
            The domain was accepted into the gaining account. The response body
            matches the domain resource representation used elsewhere in the API
            (same shape as Get Domain / Set Contacts).
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DomainResponsePayload'
        '400':
          description: >-
            Validation failed (missing or invalid fields, invalid authorization
            code, or other bad input). The `message` and `details` fields
            describe what to correct.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InvalidArgument400'
              examples:
                missingAuthCode:
                  summary: Missing auth code
                  value:
                    message: Bad Request
                    details: '''authCode'' is required'
                invalidAuthCode:
                  summary: Invalid authorization code
                  value:
                    message: Bad Request
                    details: The authorization code is invalid or has expired.
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
          description: >-
            Forbidden — for example, when the authenticated account is not
            allowlisted for internal transfers (enterprise-only; initial rollout
            is limited to designated partners), or when the caller otherwise
            lacks permission to use this operation.
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
            The domain could not be found for an internal transfer from another
            name.com account, or it is not eligible to be pulled into the
            gaining account.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NotFound404'
              examples:
                domainNotFound:
                  summary: Domain not found for internal transfer
                  value:
                    message: Not Found
                    details: >-
                      No eligible domain was found in another name.com account
                      for this request.
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
            The domain is in a state that blocks the operation — for example,
            **registrar transfer lock** is still active
            (`clientTransferProhibited` or equivalent). The losing account must
            remove transfer lock in the name.com dashboard before retrying.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericConflict409'
              examples:
                transferLockActive:
                  summary: Registrar transfer lock still enabled
                  value:
                    message: Conflict
                    details: >-
                      The domain is locked for transfer at the registrar. Unlock
                      the domain in the losing account's name.com dashboard,
                      then retry.
        '415':
          description: 'POST requests must include `Content-Type: application/json`.'
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
    CreateInternalTransferInRequest:
      description: >-
        Request body for transferring a domain from another name.com account
        into the authenticated reseller (gaining) account.
      properties:
        domainName:
          description: >-
            Fully qualified domain name to transfer in. The domain must be
            registered in another name.com account (the losing account).
          type: string
          example: example.com
          minLength: 1
        authCode:
          description: >-
            Transfer authorization code (EPP/auth code) for the domain. The
            losing account holder must obtain this code from the
            [name.com](https://www.name.com) dashboard; it is not exposed by
            this API for the losing account.
          type: string
          example: ABC123
          minLength: 1
        contacts:
          description: >-
            WHOIS contacts to apply after the transfer. If omitted, the gaining
            account's default contacts are applied. If provided, include any
            roles to override; omitted roles use the gaining account's default
            contacts. Each supplied role must include complete contact fields. A
            registrar contact-change transfer lock may apply according to the
            gaining account's settings, consistent with the Set Contacts
            endpoint.
          allOf:
            - $ref: '#/components/schemas/ContactsRequest'
      required:
        - domainName
        - authCode
      type: object
    DomainResponsePayload:
      description: The response format for a domain.
      allOf:
        - $ref: '#/components/schemas/Domain'
        - type: object
          properties:
            domainName:
              $ref: '#/components/schemas/domainName'
            createDate:
              $ref: '#/components/schemas/createDate'
            expireDate:
              $ref: '#/components/schemas/expireDate'
            autorenewEnabled:
              $ref: '#/components/schemas/autorenewEnabled'
            locked:
              $ref: '#/components/schemas/locked'
            transferLockExpiresAt:
              $ref: '#/components/schemas/transferLockExpiresAt'
            privacyEnabled:
              $ref: '#/components/schemas/privacyEnabled'
            contacts:
              $ref: '#/components/schemas/Contacts'
            nameservers:
              $ref: '#/components/schemas/nameservers'
            renewalPrice:
              $ref: '#/components/schemas/renewalPrice'
          required:
            - domainName
            - createDate
            - expireDate
            - autorenewEnabled
            - locked
            - privacyEnabled
            - contacts
            - nameservers
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
    ContactsRequest:
      description: >-
        Contacts stores the contact information for the roles related to
        domains. This schema is used for requests.
      properties:
        admin:
          $ref: '#/components/schemas/ContactRequest'
        billing:
          $ref: '#/components/schemas/ContactRequest'
        registrant:
          $ref: '#/components/schemas/RegistrantContactRequest'
        tech:
          $ref: '#/components/schemas/ContactRequest'
      type: object
    Domain:
      description: Domain contains all relevant data for a domain.
      type: object
      properties:
        domainName:
          description: The punycode-encoded value of the domain name.
          type: string
          example: example.com
        createDate:
          description: The date and time when the domain was created at the registry.
          type: string
          format: date-time
          example: '2023-01-15T14:30:00Z'
          readOnly: true
        expireDate:
          description: The date and time when the domain will expire.
          type: string
          format: date-time
          example: '2025-01-15T14:30:00Z'
          readOnly: true
        autorenewEnabled:
          description: >-
            Indicates whether the domain is set to renew automatically before
            expiration.
          type: boolean
          example: true
        locked:
          description: >-
            Indicates if the domain is **transfer locked**, preventing transfers
            to another registrar.
          type: boolean
          example: true
        locks:
          description: >-
            List of all registry locking statuses currently applied to the
            domain. Use this to see which locks are active (e.g.
            clientTransferProhibited, clientHold). Empty when the domain has no
            locks applied.
          type: array
          items:
            type: string
          readOnly: true
          example:
            - clientTransferProhibited
            - clientHold
        transferLockExpiresAt:
          description: >-
            When present, the domain has an active ICANN-mandated transfer lock
            (new registration, transfer-in, or material registrant contact
            change) that blocks client unlock via the API until this time. When
            omitted, there is no active policy transfer lock with a known expiry
            — the domain may still be locked (`locked: true`) due to a voluntary
            user lock. Does not represent RegistrarLock, AccountLock,
            verification holds, trademark-claim locks, or admin TransferLock
            with no expiry date.
          type: string
          format: date-time
          example: '2023-03-16T14:30:00Z'
          readOnly: true
        privacyEnabled:
          description: Indicates if Whois Privacy is enabled for this domain.
          type: boolean
          example: true
        contacts:
          $ref: '#/components/schemas/Contacts'
        nameservers:
          description: >-
            The list of nameservers assigned to this domain. If unspecified, it
            defaults to the account's default nameservers.
          type: array
          items:
            type: string
          example:
            - ns1.example.com
            - ns2.example.com
        renewalPrice:
          description: >-
            The cost to renew the domain. This may be required for the
            RenewDomain operation.
          type: number
          format: double
          example: 12.99
          readOnly: true
    domainName:
      description: The punycode-encoded value of the domain name.
      type: string
      example: example.com
    createDate:
      description: The date and time when the domain was created at the registry.
      type: string
      format: date-time
      example: '2023-01-15T14:30:00Z'
      readOnly: true
    expireDate:
      description: The date and time when the domain will expire.
      type: string
      format: date-time
      example: '2025-01-15T14:30:00Z'
      readOnly: true
    autorenewEnabled:
      description: >-
        Indicates whether the domain is set to renew automatically before
        expiration.
      type: boolean
      example: true
    locked:
      description: >-
        Indicates if the domain is **transfer locked**, preventing transfers to
        another registrar.
      type: boolean
      example: true
    transferLockExpiresAt:
      description: >-
        When present, the domain has an active ICANN-mandated transfer lock (new
        registration, transfer-in, or material registrant contact change) that
        blocks client unlock via the API until this time. When omitted, there is
        no active policy transfer lock with a known expiry — the domain may
        still be locked (`locked: true`) due to a voluntary user lock. Does not
        represent RegistrarLock, AccountLock, verification holds,
        trademark-claim locks, or admin TransferLock with no expiry date.
      type: string
      format: date-time
      example: '2023-03-16T14:30:00Z'
      readOnly: true
    privacyEnabled:
      description: Indicates if Whois Privacy is enabled for this domain.
      type: boolean
      example: true
    Contacts:
      description: >-
        Contacts stores the contact information for the roles related to
        domains.
      properties:
        admin:
          $ref: '#/components/schemas/Contact'
        billing:
          $ref: '#/components/schemas/Contact'
        registrant:
          $ref: '#/components/schemas/RegistrantContact'
        tech:
          $ref: '#/components/schemas/Contact'
      type: object
    nameservers:
      description: >-
        The list of nameservers assigned to this domain. If unspecified, it
        defaults to the account's default nameservers.
      type: array
      items:
        type: string
      example:
        - ns1.example.com
        - ns2.example.com
    renewalPrice:
      description: >-
        The cost to renew the domain. This may be required for the RenewDomain
        operation.
      type: number
      format: double
      example: 12.99
      readOnly: true
    ContactRequest:
      description: >-
        Contact contains all relevant contact data for a domain registrant. 
        This schema is used for creating and updating contacts (POST/PUT
        requests) and includes all validation requirements. All fields listed in
        the `required` array must be provided and cannot be null or empty.
      allOf:
        - $ref: '#/components/schemas/Contact'
        - type: object
          properties:
            firstName:
              description: First name of the contact.
              type: string
              example: John
              minLength: 1
            lastName:
              description: Last name of the contact.
              type: string
              example: Doe
              minLength: 1
            address1:
              description: The first line of the contact's address.
              type: string
              example: 123 Main Street
              minLength: 1
            city:
              description: City of the contact's address.
              type: string
              example: New York
              minLength: 1
            state:
              description: State or Province of the contact's address.
              type: string
              example: NY
              minLength: 1
            zip:
              description: >-
                ZIP or Postal Code of the contact's address. This field is
                required and must be a non-empty string.
              type: string
              example: '10001'
              minLength: 1
            country:
              description: >-
                Country code for the contact's address. Must be an ISO 3166-1
                alpha-2 country code.
              type: string
              example: US
              pattern: ^[A-Z]{2}$
            email:
              description: >-
                Email address of the contact. Must be a valid email format. The
                validation is performed against the `addr-spec` syntax in [RFC
                822](https://datatracker.ietf.org/doc/html/rfc822)
              type: string
              format: email
              example: john.doe@example.com
            phone:
              description: >-
                Phone number of the contact. Should follow the E.164
                international format: "+[country code][number]".
              type: string
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15551234567'
            fax:
              description: >-
                Fax number of the contact. Should follow the E.164 international
                format: "+[country code][number]".
              type:
                - string
                - 'null'
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15557654321'
          required:
            - firstName
            - lastName
            - address1
            - city
            - state
            - zip
            - country
            - email
            - phone
    RegistrantContactRequest:
      description: >-
        Contact contains all relevant contact data for a domain registrant. 
        This schema is used for creating and updating contacts (POST/PUT
        requests) and includes all validation requirements. All fields listed in
        the `required` array must be provided and cannot be null or empty.
      allOf:
        - $ref: '#/components/schemas/RegistrantContact'
        - type: object
          properties:
            firstName:
              description: First name of the contact.
              type: string
              example: John
              minLength: 1
            lastName:
              description: Last name of the contact.
              type: string
              example: Doe
              minLength: 1
            address1:
              description: The first line of the contact's address.
              type: string
              example: 123 Main Street
              minLength: 1
            city:
              description: City of the contact's address.
              type: string
              example: New York
              minLength: 1
            state:
              description: State or Province of the contact's address.
              type: string
              example: NY
              minLength: 1
            zip:
              description: >-
                ZIP or Postal Code of the contact's address. This field is
                required and must be a non-empty string.
              type: string
              example: '10001'
              minLength: 1
            country:
              description: >-
                Country code for the contact's address. Must be an ISO 3166-1
                alpha-2 country code.
              type: string
              example: US
              pattern: ^[A-Z]{2}$
            email:
              description: >-
                Email address of the contact. Must be a valid email format. The
                validation is performed against the `addr-spec` syntax in [RFC
                822](https://datatracker.ietf.org/doc/html/rfc822)
              type: string
              format: email
              example: john.doe@example.com
            phone:
              description: >-
                Phone number of the contact. Should follow the E.164
                international format: "+[country code][number]".
              type: string
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15551234567'
            fax:
              description: >-
                Fax number of the contact. Should follow the E.164 international
                format: "+[country code][number]".
              type:
                - string
                - 'null'
              pattern: ^\+[1-9]\d{7,14}$
              example: '+15557654321'
          required:
            - firstName
            - lastName
            - address1
            - city
            - state
            - zip
            - country
            - email
            - phone
    Contact:
      description: >-
        Contact contains all relevant contact data for a domain registrant. This
        schema is used for API responses and may contain null values for legacy
        data. For creating or updating contacts, use ContactRequest which
        enforces all validation requirements.
      type: object
      properties:
        firstName:
          description: First name of the contact.
          type:
            - string
            - 'null'
          example: John
        lastName:
          description: Last name of the contact.
          type:
            - string
            - 'null'
          example: Doe
        companyName:
          description: >-
            Company name of the contact. Leave blank if the contact is an
            individual, as some registries may assume it is a corporate entity
            otherwise.
          type:
            - string
            - 'null'
          example: Example Inc.
        address1:
          description: The first line of the contact's address.
          type:
            - string
            - 'null'
          example: 123 Main Street
        address2:
          description: The second line of the contact's address (optional).
          type:
            - string
            - 'null'
          example: Suite 400
        city:
          description: City of the contact's address.
          type:
            - string
            - 'null'
          example: New York
        state:
          description: State or Province of the contact's address.
          type:
            - string
            - 'null'
          example: NY
        zip:
          description: ZIP or Postal Code of the contact's address.
          type:
            - string
            - 'null'
          example: '10001'
        country:
          description: >-
            Country code for the contact's address. Must be an ISO 3166-1
            alpha-2 country code.
          type:
            - string
            - 'null'
          example: US
        email:
          description: >-
            Email address of the contact. Must be a valid email format. The
            validation is performed against the `addr-spec` syntax in [RFC
            822](https://datatracker.ietf.org/doc/html/rfc822)
          type:
            - string
            - 'null'
          example: john.doe@example.com
        phone:
          description: >-
            Phone number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15551234567'
        fax:
          description: >-
            Fax number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15557654321'
        isVerified:
          description: >-
            Indicates if the contact has been verified as per ICANN
            requirements. If the value is `false` it indicates that the contact
            has not completed the required verification process. This property
            is read-only and will be included in responses but should not be
            included in requests.
          type: boolean
          example: true
          readOnly: true
        verificationId:
          description: >-
            When the contact is unverified, this is the ID of the pending
            verification record. Use this ID with the resend verification email
            and verify contact endpoints. Omitted or null when the contact is
            verified.
          type:
            - integer
            - 'null'
          format: int64
          example: 12345
          readOnly: true
    RegistrantContact:
      description: >-
        Contact contains all relevant contact data for a domain registrant. This
        schema is used for API responses and may contain null values for legacy
        data. For creating or updating contacts, use RegistrantContactRequest
        which enforces all validation requirements.
      type: object
      properties:
        firstName:
          description: First name of the contact.
          type:
            - string
            - 'null'
          example: John
        lastName:
          description: Last name of the contact.
          type:
            - string
            - 'null'
          example: Doe
        companyName:
          description: >-
            Company name of the contact. Leave blank if the contact is an
            individual. Please be advised that ICANN policy links the "Company
            Name" field (Organization) in your domain's contact details to its
            legal ownership. If this field contains information, the listed
            organization is considered the legal "Registered Name Holder"
            (domain owner).
          type:
            - string
            - 'null'
          example: Example Inc.
        address1:
          description: The first line of the contact's address.
          type:
            - string
            - 'null'
          example: 123 Main Street
        address2:
          description: The second line of the contact's address (optional).
          type:
            - string
            - 'null'
          example: Suite 400
        city:
          description: City of the contact's address.
          type:
            - string
            - 'null'
          example: New York
        state:
          description: State or Province of the contact's address.
          type:
            - string
            - 'null'
          example: NY
        zip:
          description: ZIP or Postal Code of the contact's address.
          type:
            - string
            - 'null'
          example: '10001'
        country:
          description: >-
            Country code for the contact's address. Must be an ISO 3166-1
            alpha-2 country code.
          type:
            - string
            - 'null'
          example: US
        email:
          description: >-
            Email address of the contact. Must be a valid email format. The
            validation is performed against the `addr-spec` syntax in [RFC
            822](https://datatracker.ietf.org/doc/html/rfc822)
          type:
            - string
            - 'null'
          example: john.doe@example.com
        phone:
          description: >-
            Phone number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15551234567'
        fax:
          description: >-
            Fax number of the contact. Should follow the E.164 international
            format: "+[country code][number]".
          type:
            - string
            - 'null'
          example: '+15557654321'
        isVerified:
          description: >-
            Indicates if the contact has been verified as per ICANN
            requirements. If the value is `false` it indicates that the contact
            has not completed the required verification process. This property
            is read-only and will be included in responses but should not be
            included in requests.
          type: boolean
          example: true
          readOnly: true
        verificationId:
          description: >-
            When the contact is unverified, this is the ID of the pending
            verification record. Use this ID with the resend verification email
            and verify contact endpoints. Omitted or null when the contact is
            verified.
          type:
            - integer
            - 'null'
          format: int64
          example: 12345
          readOnly: true
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