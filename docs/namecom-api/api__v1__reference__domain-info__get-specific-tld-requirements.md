> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Specific TLD Requirements

> Returns the registration requirements some general information for a specific TLD. The response contains a detailed description of eligibility criteria and a fields object with all required and optional fields, including validation rules, conditional logic, and nested field structures. Provide the TLD as a path parameter to retrieve its complete registration requirements. Useful when you only need details for one TLD (e.g., when a user selects .fr from a dropdown).



## OpenAPI

````yaml get /core/v1/domaininfo/requirements/{tld}
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
  /core/v1/domaininfo/requirements/{tld}:
    get:
      tags:
        - Domain Info
      summary: Get Specific TLD Requirements
      description: >-
        Returns the registration requirements some general information for a
        specific TLD. The response contains a detailed description of
        eligibility criteria and a fields object with all required and optional
        fields, including validation rules, conditional logic, and nested field
        structures. Provide the TLD as a path parameter to retrieve its complete
        registration requirements. Useful when you only need details for one TLD
        (e.g., when a user selects .fr from a dropdown).
      operationId: GetRequirement
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
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GetRequirementResponse'
              examples:
                complex_requirement_set:
                  summary: Complex requirement set
                  description: >-
                    Example of a complex requirement set with multiple fields,
                    conditional logic, and nested requirements
                  value:
                    tldInfo:
                      tld: fr
                      ccTld: true
                      supportsTransferLock: true
                      supportsDnssec: true
                      supportsPremium: true
                      supportsPrivacy: true
                      supportsInternalTransfer: true
                      requiresPreDelegation: true
                      expirationGracePeriod: 3
                      idnLanguages: {}
                      allowedRegistrationYears:
                        - 1
                        - 2
                        - 3
                        - 4
                        - 5
                        - 6
                        - 7
                        - 8
                        - 9
                        - 10
                      hsts: false
                      minDomainLength: 5
                      minIdnDomainLength: 5
                      registryOperator: registryfr
                      claimsCheckRequired: []
                      requireIdnSld: false
                    contacts:
                      description: The contacts required to be submitted for registration
                      type: string
                      required: true
                      label: contacts
                      fields:
                        registrant:
                          description: Registrant contact requirements
                          type: string
                          required: true
                          fields:
                            firstName:
                              description: First name of registrant contact
                              type: string
                              required: true
                            lastName:
                              description: Last name of registrant contact
                              type: string
                              required: true
                            address1:
                              description: First part of mailing address
                              type: string
                              required: true
                            address2:
                              description: Second part of mailing address
                              type: string
                              required: false
                            companyName:
                              description: Company name of registrant contact
                              type: string
                              required: false
                            phone:
                              description: Phone number of registrant contact
                              type: string
                              required: true
                            fax:
                              description: Fax number of registrant contact
                              type: string
                              required: false
                            email:
                              description: Email address of registrant contact
                              type: string
                              required: true
                              validation: valid_email
                            city:
                              description: City of registrant contact
                              type: string
                              required: true
                            state:
                              description: >-
                                State/Province of registrant. Only values from
                                this list are allowed
                              type: string
                              required: true
                            zip:
                              description: Postal code of registrant contact
                              type: string
                              required: true
                            country:
                              description: >-
                                Country of registrant, only options in this list
                                are allowed
                              type: enum
                              required: true
                              options:
                                - value: AT
                                  label: Austria
                                - value: AX
                                  label: Åland Islands
                                - value: BE
                                  label: Belgium
                                - value: BG
                                  label: Bulgaria
                                - value: CH
                                  label: Switzerland
                                - value: CY
                                  label: Cyprus
                                - value: CZ
                                  label: Czech Republic
                                - value: DE
                                  label: Germany
                                - value: DK
                                  label: Denmark
                                - value: EE
                                  label: Estonia
                                - value: ES
                                  label: Spain
                                - value: FI
                                  label: Finland
                                - value: FR
                                  label: France
                                - value: GF
                                  label: Guiana
                                - value: GP
                                  label: Guadeloupe
                                - value: GR
                                  label: Greece
                                - value: HU
                                  label: Hungary
                                - value: IE
                                  label: Ireland
                                - value: IS
                                  label: Iceland
                                - value: IT
                                  label: Italy
                                - value: LI
                                  label: Liechtenstein
                                - value: LT
                                  label: Lithuania
                                - value: LU
                                  label: Luxembourg
                                - value: LV
                                  label: Latvia
                                - value: MQ
                                  label: Martinique
                                - value: MT
                                  label: Malta
                                - value: NC
                                  label: New Caledonia
                                - value: NL
                                  label: Netherlands
                                - value: 'NO'
                                  label: Norway
                                - value: PF
                                  label: Polynesia (French)
                                - value: PL
                                  label: Poland
                                - value: PM
                                  label: St. Pierre & Miquelon
                                - value: PT
                                  label: Portugal
                                - value: RE
                                  label: Reunion
                                - value: RO
                                  label: Romania
                                - value: SE
                                  label: Sweden
                                - value: SI
                                  label: Slovenia
                                - value: SK
                                  label: Slovakia
                                - value: TF
                                  label: French Southern and Antarctic Lands
                                - value: WF
                                  label: Wallis & Futuna Is.
                                - value: YT
                                  label: Mayotte
                        tech:
                          description: Technical contact requirements
                          type: string
                          required: true
                          fields:
                            firstName:
                              description: First name of tech contact
                              type: string
                              required: true
                            lastName:
                              description: Last name of tech contact
                              type: string
                              required: true
                            address1:
                              description: First part of mailing address
                              type: string
                              required: true
                            address2:
                              description: Second part of mailing address
                              type: string
                              required: false
                            companyName:
                              description: Required company name of tech contact
                              type: string
                              required: true
                            phone:
                              description: Phone number of tech contact
                              type: string
                              required: true
                            fax:
                              description: Fax number of tech contact
                              type: string
                              required: false
                            email:
                              description: Email address of tech contact
                              type: string
                              required: true
                              validation: valid_email
                            city:
                              description: City of tech contact
                              type: string
                              required: true
                            state:
                              description: >-
                                State/Province of tech contact. Only values from
                                this list are allowed
                              type: string
                              required: true
                            zip:
                              description: Postal code of tech contact
                              type: string
                              required: true
                            country:
                              description: Country of tech contact
                              type: enum
                              required: true
                    requirements:
                      description: Registration requirements for .fr domains
                      fields:
                        firstName:
                          description: First name of registrant
                          type: string
                          required: true
                        lastName:
                          description: Last name of registrant
                          type: string
                          required: true
                        address1:
                          description: First part of mailing address
                          type: string
                          required: true
                        address2:
                          description: Second part of mailing address
                          type: string
                          required: false
                        companyName:
                          description: Company name of registrant
                          type: string
                          required: false
                        phone:
                          description: Phone number of registrant
                          type: string
                          required: true
                        fax:
                          description: Fax number of registrant
                          type: string
                          required: false
                        email:
                          description: Email address of registrant
                          type: string
                          required: true
                          validation: valid_email
                        city:
                          description: City of registrant
                          type: string
                          required: true
                        state:
                          description: State/Province of registrant
                          type: string
                          required: true
                        zip:
                          description: Postal code of registrant
                          type: string
                          required: true
                        country:
                          description: >-
                            Country of registrant, only options in this list are
                            allowed
                          type: enum
                          required: true
                          options:
                            - value: AT
                              label: Austria
                            - value: AX
                              label: Åland Islands
                            - value: BE
                              label: Belgium
                            - value: BG
                              label: Bulgaria
                            - value: CH
                              label: Switzerland
                            - value: CY
                              label: Cyprus
                            - value: CZ
                              label: Czech Republic
                            - value: DE
                              label: Germany
                            - value: DK
                              label: Denmark
                            - value: EE
                              label: Estonia
                            - value: ES
                              label: Spain
                            - value: FI
                              label: Finland
                            - value: FR
                              label: France
                            - value: GF
                              label: Guiana
                            - value: GP
                              label: Guadeloupe
                            - value: GR
                              label: Greece
                            - value: HU
                              label: Hungary
                            - value: IE
                              label: Ireland
                            - value: IS
                              label: Iceland
                            - value: IT
                              label: Italy
                            - value: LI
                              label: Liechtenstein
                            - value: LT
                              label: Lithuania
                            - value: LU
                              label: Luxembourg
                            - value: LV
                              label: Latvia
                            - value: MQ
                              label: Martinique
                            - value: MT
                              label: Malta
                            - value: NC
                              label: New Caledonia
                            - value: NL
                              label: Netherlands
                            - value: 'NO'
                              label: Norway
                            - value: PF
                              label: Polynesia (French)
                            - value: PL
                              label: Poland
                            - value: PM
                              label: St. Pierre & Miquelon
                            - value: PT
                              label: Portugal
                            - value: RE
                              label: Reunion
                            - value: RO
                              label: Romania
                            - value: SE
                              label: Sweden
                            - value: SI
                              label: Slovenia
                            - value: SK
                              label: Slovakia
                            - value: TF
                              label: French Southern and Antarctic Lands
                            - value: WF
                              label: Wallis & Futuna Is.
                            - value: YT
                              label: Mayotte
                        business:
                          description: ''
                          type: enum
                          required: true
                          label: business
                          options:
                            - value: 'no'
                              label: I am an individual
                              fields:
                                X-FR-BIRTHDATE:
                                  description: ''
                                  type: string
                                  required: false
                                  label: Date of Birth (YYYY-MM-DD)
                                X-FR-BIRTHPLACE:
                                  description: ''
                                  type: string
                                  required: true
                                  label: Birth Country (2 Letter Code)
                                  fields:
                                    X-FR-BIRTHCITY:
                                      description: ''
                                      type: string
                                      required: false
                                      label: Birth City
                                      required_when: FR
                                    X-FR-BIRTHPC:
                                      description: ''
                                      type: string
                                      required: false
                                      label: Birth Postal Code
                                      required_when: FR
                            - value: 'yes'
                              label: I am an organization
                              fields:
                                X-FR-LOCAL:
                                  description: 'Local company registration #, or tax ID'
                                  type: string
                                  required: false
                                  label: 'Local company registration #, or tax ID'
                simple_acknowledgement_requirement:
                  summary: Simple acknowledgement requirement
                  description: >-
                    Example of a simple requirement with just an acknowledgement
                    field
                  value:
                    tldInfo:
                      tld: security
                      ccTld: false
                      supportsTransferLock: true
                      supportsDnssec: true
                      supportsPremium: true
                      supportsPrivacy: true
                      supportsInternalTransfer: true
                      requiresPreDelegation: true
                      expirationGracePeriod: 25
                      hsts: false
                      minDomainLength: 3
                      minIdnDomainLength: 4
                      idnLanguages:
                        AR: Arabic
                        GREK: Greek
                        HE: Hebrew
                        JA: Japanese
                        KO: Korean
                        LATN: Latin
                        LO: Lao
                        RU: Russian
                        TH: Thai
                        ZH: Chinese
                      allowedRegistrationYears:
                        - 1
                        - 2
                        - 3
                        - 4
                        - 5
                        - 6
                        - 7
                        - 8
                        - 9
                        - 10
                      registryOperator: centralnic
                      claimsCheckRequired: []
                      requireIdnSld: false
                    contacts:
                      description: The contacts required to be submitted for registration
                      type: string
                      required: true
                      label: contacts
                      fields: {}
                    requirements:
                      description: Registration requirements for .security domains
                      fields:
                        acknowledgement:
                          description: >-
                            .SECURITY domains will not resolve unless they have
                            both DNSSEC and an SSL on the domain.
                          type: acknowledgement
                          required: false
                          label: I understand
                          value: accepted
                simple_notification_requirement:
                  summary: Simple notification requirement
                  description: Example of a simple requirement with just a notice field
                  value:
                    tldInfo:
                      tld: at
                      ccTld: true
                      supportsTransferLock: false
                      supportsDnssec: true
                      supportsPremium: false
                      supportsPrivacy: false
                      supportsInternalTransfer: false
                      requiresPreDelegation: false
                      expirationGracePeriod: 3
                      hsts: true
                      minDomainLength: 3
                      minIdnDomainLength: null
                      idnLanguages: {}
                      allowedRegistrationYears:
                        - 1
                        - 2
                        - 3
                        - 4
                        - 5
                        - 6
                        - 7
                        - 8
                        - 9
                        - 10
                      registryOperator: nicat
                      claimsCheckRequired: []
                      requireIdnSld: false
                    contacts:
                      description: The contacts required to be submitted for registration
                      type: string
                      required: true
                      label: contacts
                      fields: {}
                    requirements:
                      description: Registration requirements for .at domains
                      fields:
                        description:
                          description: >-
                            The .AT registry has special rules regarding the
                            expiration and deletion of .AT domains. Customers
                            who may choose not to renew .AT domains at their
                            expiration should take note of these requirements.
                            If you do not intend to renew your .AT domain when
                            it comes up for renewal, you will need to complete
                            the official NIC.AT cancellation form at least 28
                            days before it's expiration date and return it
                            directly to the .AT registry. If an official
                            cancellation form is not received by the .AT
                            registry 28 days prior to the domain's expiration
                            date, name.com will be required to withdraw the
                            registration, which will result in NIC.AT billing
                            you directly for the subsequent registration period
                            at the NIC.AT standard rate.
                          type: notice
                          required: false
                          label: ''
          description: The complete registration requirements for the specified TLD.
        '400':
          description: Bad request - Invalid TLD format.
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
          description: Tld not found.
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
                  summary: TLD not supported
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
    GetRequirementResponse:
      description: >-
        GetRequirementResponse has TLD Info and registration requirements for
        the specified TLD. The requirements field will always be present but may
        be an empty object when no specific requirements exist for the TLD.
      type: object
      properties:
        tldInfo:
          $ref: '#/components/schemas/ResellerTldInfo'
          description: >-
            General information about a specific TLD. These are not registration
            requirements, but contain useful information for domain reseller and
            domain registrants in general.
        contacts:
          $ref: '#/components/schemas/ContactsRequirement'
          description: >-
            The registration requirements for the contacts for this TLD,
            including required fields, validation rules, and conditional logic. 
            This field will always be present but may be an empty object when no
            specific requirements exist for the TLD.

            Only a few CC Tlds have specific contact requirements. These
            contacts must be submitted as part of the domain object when
            registering a domain, and not part of the `tldRequirements`
            parameter.

            Please check the contact requirements carefully, as different fields
            may be required for different roles, and there may be additional
            validation rules that must be followed.
        requirements:
          $ref: '#/components/schemas/Requirement'
          description: >-
            The registration requirements for this TLD, including required
            fields, validation rules, and conditional logic. This field will
            always be present but may be an empty object when no specific
            requirements exist for the TLD.
      required:
        - requirements
        - tldInfo
        - contacts
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
    ContactsRequirement:
      description: >-
        ContactsRequirement defines the registration requirements for contact
        fields for a specific TLD, including required fields, validation rules,
        and conditional logic. This follows the RequirementField structure with
        contact roles as nested fields.
      type: object
      required:
        - type
        - required
      properties:
        description:
          description: >-
            A detailed description of the contact requirements for this TLD,
            including eligibility criteria, restrictions, and important notes.
          type: string
          example: The contacts required to be submitted for registration
        type:
          description: The requirement type, which will be "string" for contacts.
          type: string
          example: string
        required:
          description: Whether contact information is mandatory for domain registration.
          oneOf:
            - type: boolean
              example: true
            - type: string
              example: 'true'
          example: true
        label:
          description: A user-friendly label for the contacts field.
          type: string
          example: contacts
        fields:
          description: >-
            An object containing contact roles (registrant, tech, admin, etc.)
            with their individual field requirements.
          type: object
          additionalProperties:
            type: object
            description: Contact role requirements (e.g., registrant, tech, admin)
            properties:
              description:
                description: Description of the contact role requirements.
                type: string
              type:
                description: The requirement type for this contact role.
                type: string
                example: string
              required:
                description: Whether this contact role is required.
                oneOf:
                  - type: boolean
                  - type: string
                example: true
              fields:
                description: >-
                  Individual contact fields for this role, following
                  RequirementField structure.
                type: object
                additionalProperties:
                  $ref: '#/components/schemas/RequirementField'
    Requirement:
      description: >-
        Requirement defines the registration requirements for a specific TLD,
        including required fields, validation rules, and conditional logic.
      type: object
      properties:
        description:
          description: >-
            A detailed description of the registration requirements for this
            TLD, including eligibility criteria, restrictions, and important
            notes.
          type: string
          example: Required fields to register an .fr domain
        fields:
          description: >-
            An object containing all required and optional fields for domain
            registration, with their validation rules and conditional logic.
          type: object
          additionalProperties:
            $ref: '#/components/schemas/RequirementField'
    RequirementField:
      description: >-
        A field definition for TLD registration requirements, including
        validation rules, conditional logic, and nested field structures.
      type: object
      required:
        - type
        - required
      properties:
        description:
          description: >-
            A detailed description of what this field is for and any specific
            requirements or constraints.
          type: string
          example: First name of registrant
        type:
          description: >
            The requirement type of this field. Each requirement type has
            different information.


            Possible values and their details:

              - **`string`**: These are open string fields that cannot be submitted as empty. They will always have a label. A description is optional as the label may convey all of the required information the user would need to submit.
                  Note: Some string fields may have a required format (i.e. date format of YYYY/MM/DD). The format will be listed in the "validation" parameter if required.
                  Example TLDs: abogado, law, com.br (and more)

              - **`notice`**: These field types will just have a description, and contain information that must be displayed to the user prior to registration. There is no data that will be required to be submitted, so all notice type fields will have a "required" value of `false`.
                  Example TLDs: at (notice only), ca (1 notice field)

              - **`acknowledgement`**: These field types will have a description, label and value. The description must be displayed to the user, the label is the required label for the acknowledgement, and the value is what must be submitted.
                  Example TLDs: security, ngo, music (and more)

              - **`enum`**: The field types have a list of predefined options that the user must choose from in order to submit. Only the values returned in the "options" array will be allowed, or the request will fail validation. Options MAY include dependent fields, as some registries required additional information depending on what was chosen for the "parent" option. All dependent fields will follow the same field patterns as the parent fields.
                  Options: These are the predefined options for the enum type fields. They will always have a label and a value. The value is what must be submitted. The options MAY include a description, but will mostly only have a label parameter.
                  Note: There may be a single option returned for an enum. This is because that is the ONLY OPTION ALLOWED by the registry.
                  Example TLDs with simple lists: ca, es (and more)
                  Example TLDs with dependent fields: fr, se, com.br

              - **`boolean`**: Boolean fields for simple true/false acknowledgements or selections.
                  Example TLDs: security
          enum:
            - string
            - notice
            - acknowledgement
            - enum
            - boolean
          example: string
        required:
          description: >-
            Whether this field is mandatory for domain registration. If true,
            the field must be provided.
          oneOf:
            - type: boolean
              example: true
            - type: string
              example: 'true'
          example: true
        label:
          description: A user-friendly label for this field that can be used in UI forms.
          type: string
          example: First Name
        validation:
          description: >-
            Validation rule to apply to this field. Common validations include
            'valid_email', 'valid_phone', etc.
          type:
            - string
            - 'null'
          example: valid_email
        options:
          description: >-
            For fields with predefined choices, this can be either an array of
            complex option objects, a simple array of string values, or null if
            no options are available.
          oneOf:
            - type: array
              items:
                $ref: '#/components/schemas/RequirementFieldOption'
              minItems: 0
            - type: array
              items:
                type: string
              minItems: 0
              example:
                - English
                - French
            - type: 'null'
        required_when:
          description: >-
            For conditional fields, specifies when this field becomes required
            (e.g., when a parent option has a specific value).
          type:
            - string
            - 'null'
          example: FR
        fields:
          description: >-
            For complex fields or when options are selected, contains nested
            field definitions that become relevant.
          type:
            - object
            - 'null'
          additionalProperties:
            $ref: '#/components/schemas/RequirementField'
        value:
          description: >-
            For acknowledgement fields, this is the value that must be submitted
            when the user acknowledges the requirement.
          type:
            - string
            - 'null'
          example: accepted
    RequirementFieldOption:
      description: >-
        An option within a field that has predefined choices, including the
        option value, label, and any nested fields that become relevant when
        this option is selected.
      type: object
      required:
        - value
      properties:
        value:
          description: >-
            The actual value of this option. This is what must be submitted when
            this option is selected.
          type: string
          example: 'no'
        label:
          description: >-
            A user-friendly label for this option that can be displayed in UI
            forms.
          type: string
          example: I am an individual
        fields:
          description: >-
            When this option is selected, these nested fields become relevant
            and may be required. This allows for conditional field logic.
          type:
            - object
            - 'null'
          additionalProperties:
            $ref: '#/components/schemas/RequirementField'
          example:
            X-FR-BIRTHDATE:
              description: DOB in format yy/mm/dd
              type: string
              required: true
            X-FR-BIRTHPLACE:
              required: true
              description: Nation of Birth
              type: enum
              options:
                - FR
                - GB
                - USA
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