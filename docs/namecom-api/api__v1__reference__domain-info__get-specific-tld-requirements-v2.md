> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get TLD Requirements as JSON Schema

> Returns the registration requirements as a JSON Schema (Draft 7) document. This endpoint is designed for form generation and validation libraries that consume JSON Schema directly.



## OpenAPI

````yaml get /core/v1/domaininfo/requirementsV2/{tld}
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
  /core/v1/domaininfo/requirementsV2/{tld}:
    get:
      tags:
        - Domain Info
      summary: Get TLD Requirements as JSON Schema
      description: >-
        Returns the registration requirements as a JSON Schema (Draft 7)
        document. This endpoint is designed for form generation and validation
        libraries that consume JSON Schema directly.
      operationId: GetTldRequirementsV2
      parameters:
        - name: tld
          description: >-
            TLD indicates which domain requirements to retrieve (without the dot
            prefix, e.g., 'fr' for .fr domains). For punycode TLDs, use the
            ASCII version instead of the UTF-8. So for the `онлайн` TLD, you
            would submit `xn--80asehdb`.
          in: path
          required: true
          schema:
            type: string
            example: fr
            pattern: >-
              ^((?!xn--)[a-z0-9-]{1,63}|xn--[a-z0-9-]{1,63})((?:\.(?!-)[a-z0-9-]{1,63})|(?:\.xn--[a-z0-9-]{1,63}))*$
      responses:
        '200':
          description: JSON Schema document describing TLD registration requirements.
          content:
            application/schema+json:
              schema:
                $ref: '#/components/schemas/RequirementsJsonSchema'
              examples:
                it_tld_schema:
                  summary: Example for .it TLD
                  value:
                    $schema: http://json-schema.org/draft-07/schema#
                    type: object
                    title: .it Domain Registration Requirements Schema
                    description: Registration requirements for .it domains
                    properties:
                      tldInfo:
                        tld: .it
                        ccTld: true
                        supportsTransferLock: true
                        supportsDnssec: true
                        supportsPremium: false
                        supportsPrivacy: false
                        supportsInternalTransfer: true
                        requiresPreDelegation: false
                        expirationGracePeriod: 25
                        allowedRegistrationYears:
                          - 1
                          - 3
                          - 5
                          - 8
                          - 10
                        idnLanguages:
                          IT: Italian
                        hsts: false
                        minDomainLength: 3
                        minIdnDomainLength: 5
                        registryOperator: nic.it
                        claimsCheckRequired: []
                        requireIdnSld: false
                        readOnly: true
                      contacts:
                        type: object
                        properties:
                          registrant:
                            type: object
                            properties:
                              firstName:
                                type: string
                                title: First Name
                                description: First name of registrant contact
                              email:
                                type: string
                                format: email
                                title: Email
                                description: Email address of registrant contact
                            required:
                              - firstName
                              - email
                        required:
                          - registrant
                      tldRequirements:
                        type: object
                        properties:
                          X-IT-ENTITY-TYPE:
                            type: string
                            title: Registrant Entity Type
                            enum:
                              - '1'
                              - '2'
                              - '3'
                              - '4'
                              - '5'
                              - '6'
                              - '7'
                          X-IT-PIN:
                            type: string
                            title: .IT PIN number
                            description: >-
                              16 alphanumeric characters (tax code) for natural
                              persons or 11 digits (VAT number) for
                              organizations
                    required:
                      - tldInfo
                      - contacts
                      - tldRequirements
            application/json:
              schema:
                $ref: '#/components/schemas/RequirementsJsonSchema'
              examples:
                it_tld_schema:
                  summary: Example for .it TLD
                  value:
                    $schema: http://json-schema.org/draft-07/schema#
                    type: object
                    title: .it Domain Registration Requirements Schema
                    description: Registration requirements for .it domains
                    properties:
                      tldInfo:
                        tld: .it
                        ccTld: true
                        supportsTransferLock: true
                        supportsDnssec: true
                        supportsPremium: false
                        supportsPrivacy: false
                        supportsInternalTransfer: true
                        requiresPreDelegation: false
                        expirationGracePeriod: 25
                        allowedRegistrationYears:
                          - 1
                          - 3
                          - 5
                          - 8
                          - 10
                        idnLanguages:
                          IT: Italian
                        hsts: false
                        minDomainLength: 3
                        minIdnDomainLength: 5
                        registryOperator: nic.it
                        claimsCheckRequired: []
                        requireIdnSld: false
                        readOnly: true
                      contacts:
                        type: object
                        properties:
                          registrant:
                            type: object
                            properties:
                              firstName:
                                type: string
                                title: First Name
                                description: First name of registrant contact
                              email:
                                type: string
                                format: email
                                title: Email
                                description: Email address of registrant contact
                            required:
                              - firstName
                              - email
                        required:
                          - registrant
                      tldRequirements:
                        type: object
                        properties:
                          X-IT-ENTITY-TYPE:
                            type: string
                            title: Registrant Entity Type
                            enum:
                              - '1'
                              - '2'
                              - '3'
                              - '4'
                              - '5'
                              - '6'
                              - '7'
                          X-IT-PIN:
                            type: string
                            title: .IT PIN number
                            description: >-
                              16 alphanumeric characters (tax code) for natural
                              persons or 11 digits (VAT number) for
                              organizations
                    required:
                      - tldInfo
                      - contacts
                      - tldRequirements
        '400':
          description: Bad request.
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
          description: TLD not found.
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
        '422':
          description: TLD not supported.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UnprocessableEntity422'
              examples:
                tldNotSupported:
                  summary: Registration price unavailable
                  value:
                    message: Unsupported TLD
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
    RequirementsJsonSchema:
      description: >-
        A JSON Schema Draft 7 document that describes the registration
        requirements for a TLD. This schema follows the JSON Schema Draft 7
        specification (http://json-schema.org/draft-07/schema#) and can be used
        directly by form generation and validation libraries that consume JSON
        Schema.

        The schema structure includes: - A `tldInfo` property containing general
        TLD information (read-only, always present) - A `contacts` property
        containing contact field requirements (e.g., registrant, admin, tech) -
        A `tldRequirements` property containing TLD-specific registration fields

        The `contacts` and `tldRequirements` properties may be empty objects,
        while `tldInfo` will always contain data. The exact structure varies by
        TLD, as different TLDs have different registration requirements.
      type: object
      properties:
        $schema:
          description: >-
            The JSON Schema version identifier, should be
            "http://json-schema.org/draft-07/schema#"
          type: string
          example: http://json-schema.org/draft-07/schema#
        type:
          description: The JSON Schema type, typically "object" for requirement schemas
          type: string
          example: object
        title:
          description: A human-readable title for the schema
          type: string
          example: .it Domain Registration Requirements Schema
        description:
          description: A detailed description of the registration requirements
          type: string
          example: Registration requirements for .it domains
        properties:
          description: >-
            An object containing the schema properties. Includes: - `tldInfo`:
            An object containing general TLD information (read-only) -
            `contacts`: An object defining contact field requirements -
            `tldRequirements`: An object defining TLD-specific registration
            fields
          type: object
          properties:
            tldInfo:
              description: >-
                General information about a TLD and it's various requirements.
                This is not a comprehensive list of all information related to a
                TLD.  The structure matches ResellerTldInfo schema. In JSON
                Schema document examples, this property will contain a schema
                definition object  with `allOf` referencing ResellerTldInfo and
                `readOnly: true`.
              allOf:
                - $ref: '#/components/schemas/TldInfoJsonSchema'
            contacts:
              description: >-
                An object defining contact field requirements. May be an empty
                object if no contact requirements exist for the TLD.
              type: object
              additionalProperties: true
            tldRequirements:
              description: >-
                An object defining TLD-specific registration fields. May be an
                empty object if no TLD-specific requirements exist.
              type: object
              additionalProperties: true
          additionalProperties: false
        required:
          description: An array of required property names
          type: array
          items:
            type: string
          example:
            - tldInfo
            - contacts
            - tldRequirements
        allOf:
          description: >-
            An array of schema objects that must all be valid. Used for
            conditional validation with multiple conditions.
          type: array
          items:
            type: object
            additionalProperties: true
        if:
          description: >-
            The condition schema for conditional validation. When this condition
            is true, the 'then' schema applies.
          type:
            - object
            - 'null'
          additionalProperties: true
        then:
          description: The schema to apply when the 'if' condition is true.
          type:
            - object
            - 'null'
          additionalProperties: true
        else:
          description: The schema to apply when the 'if' condition is false (optional).
          type:
            - object
            - 'null'
          additionalProperties: true
      example:
        $schema: http://json-schema.org/draft-07/schema#
        type: object
        title: .it Domain Registration Requirements Schema
        description: Registration requirements for .it domains
        properties:
          tldInfo:
            tld: .it
            ccTld: true
            supportsTransferLock: true
            supportsDnssec: true
            supportsPremium: false
            supportsPrivacy: false
            supportsInternalTransfer: true
            requiresPreDelegation: false
            expirationGracePeriod: 25
            allowedRegistrationYears:
              - 1
              - 3
              - 5
              - 8
              - 10
            idnLanguages:
              IT: Italian
            hsts: false
            minDomainLength: 3
            minIdnDomainLength: 5
            registryOperator: nic.it
            claimsCheckRequired: []
            requireIdnSld: false
            readOnly: true
          contacts:
            type: object
            properties:
              registrant:
                type: object
                properties:
                  firstName:
                    type: string
                    title: First Name
                    description: First name of registrant contact
                  email:
                    type: string
                    format: email
                    title: Email
                    description: Email address of registrant contact
                required:
                  - firstName
                  - email
            required:
              - registrant
          tldRequirements:
            type: object
            properties:
              X-IT-ENTITY-TYPE:
                type: string
                title: Registrant Entity Type
                enum:
                  - '1'
                  - '2'
                  - '3'
                  - '4'
                  - '5'
                  - '6'
                  - '7'
              X-IT-PIN:
                type: string
                title: .IT PIN number
                description: >-
                  16 alphanumeric characters (tax code) for natural persons or
                  11 digits (VAT number) for organizations
        required:
          - tldInfo
          - contacts
          - tldRequirements
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
    TldInfoJsonSchema:
      description: >-
        A JSON Schema Draft 7 definition for tldInfo that wraps ResellerTldInfo
        with readOnly metadata. This schema can be referenced in JSON Schema
        documents using $ref.
      type: object
      allOf:
        - $ref: '#/components/schemas/ResellerTldInfo'
      readOnly: true
    ResellerTldInfo:
      description: >-
        General information about a TLD and it's various requirements. This is
        not a comprehensive list of all information related to a TLD.
      type: object
      properties:
        tld:
          description: The TLD this information relates to.
          type: string
          example: .fr
        ccTld:
          description: Whether the TLD is a Country Code TLD.
          type: boolean
          example: true
        supportsTransferLock:
          description: Whether the TLD supports implementing a Transfer Lock.
          type: boolean
          example: true
        supportsDnssec:
          description: Whether the TLD supports DNSSEC.
          type: boolean
          example: true
        supportsPremium:
          description: Whether there are premium domains for this TLD.
          type: boolean
          example: true
        supportsPrivacy:
          description: Whether the TLD supports WHOIS Privacy.
          type: boolean
          example: true
        supportsInternalTransfer:
          description: >-
            Whether the TLD supports internal transfer between reseller
            accounts.
          type: boolean
          example: true
        requiresPreDelegation:
          description: >-
            Whether this TLD requires pre-delegation. If this is true, these
            domains must be added to the name servers before the domain creation
            is completed.
          type: boolean
          example: true
        expirationGracePeriod:
          description: >-
            The number of days you have to renew your domain after it has
            expired, but before it is removed from your account.
          type: integer
          format: int32
          example: 25
        allowedRegistrationYears:
          description: The years that a domain is allowed to be registered for.
          type: array
          items:
            type: integer
          example:
            - 1
            - 3
            - 5
            - 8
            - 10
        idnLanguages:
          description: The IND Languages that the TLD supports (if any).
          type: object
          additionalProperties:
            type: string
          example:
            DE: German
            DK: Danish
            ES: Spanish
            IT: Italian
            JP: Japanese
        hsts:
          description: >-
            The entire TLD namespace has been added to the HSTS Preload list. As
            such, all second-level domains under .TLD will only load on modern
            browsers if a valid SSL certificate has been configured and the
            webserver is serving HTTPS.
          type: boolean
          example: true
        minDomainLength:
          description: >-
            The minimum allowed length for the second level domain (SLD) for a
            given TLD. The SLD would be the `example` part of `example.com`.
            Attempts to register a domain with a shorter length than allowed
            will result in a failure of a Create Domain request.
          type: integer
          format: int32
          example: 3
        minIdnDomainLength:
          description: >-
            The minimum allowed length for the second level domain (SLD) that
            utilizes an IDN character for a given TLD.  The SLD would be the
            `èxample` part of `èxample.com`. Attempts to register a domain with
            a shorter length than allowed will result in a failure of a Create
            Domain request. This value will often be different from the
            `minDomainLength` for non-IDN registrations.  This parameter will
            return as `null` for any TLDs that do not support IDN registrations.
          type:
            - integer
            - 'null'
          format: int32
          example: 5
        registryOperator:
          description: The registry that operates the given TLD.
          type: string
          example: verisign
        claimsCheckRequired:
          description: >-
            Array of valid purchase types if claims check is required for this
            TLD for current date/time.  If claims checking is required, returns
            an array of valid purchase types (e.g., ["registration",
            "landrush_eap"]).  If claims checking is not required, returns an
            empty array [].
          type: array
          items:
            type: string
            enum:
              - registration
              - landrush_eap
              - landrush_auction_a
              - landrush_reserve_a
          example:
            - registration
        requireIdnSld:
          description: >-
            When true, the TLD only accepts IDN (punycode) second-level domain
            names in the required script. ASCII/Latin SLDs are not valid for
            registration.
          type: boolean
          example: false
      required:
        - tld
        - ccTld
        - supportsTransferLock
        - supportsDnssec
        - supportsPremium
        - supportsPrivacy
        - supportsInternalTransfer
        - requiresPreDelegation
        - expirationGracePeriod
        - idnLanguages
        - allowedRegistrationYears
        - hsts
        - minDomainLength
        - minIdnDomainLength
        - registryOperator
        - claimsCheckRequired
        - requireIdnSld
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