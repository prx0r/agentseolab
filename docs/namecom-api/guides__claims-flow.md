> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Claims Flow

> 4-step guide with examples on how to register domains with claims. Note: Example domain names, trademarks, and other data shown below are dummy data used for illustrative purposes only.

# Steps to Register a Domain with a Claims Check

## 1. Check TLD Info for Claims Support

Use the [TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements) (Domain Info) endpoint to determine whether a TLD supports claims.

**Example Response:**

```json theme={null}
"claimsCheckRequired": [
  "registration"
]
```

Until additional pre-order types are supported in the API, the `purchaseType` should always be `registration`.

## 2. Retrieve Claims Data (if applicable)

If `claimsCheckRequired` is not an empty array, you will need to check your domain using the Claims Lookup endpoint.

Please note: A TLD may support claims, but an individual domain under that TLD might not have any active claims.

The POST `/core/v1/domaininfo/claims/{domain}` returns:

* any trademark claims that apply to the domain (message you must display to the registrant). The purchaser isn’t required to submit any documentation, and it’s not the reseller's responsibility to verify their trademark rights. The reseller's only obligation is to display the required notice before they complete the purchase.
* a `claimID` and `notAfter` that must be included on the Domain Create request. The `notBefore` and `notAfter` is the validity window of the response data. If you are getting claims response data, it's valid only for about 2 days and it needs to be submitted to domainCreate within that validity window. In order to use the claimID output, you'll need to submit the domainCreate before `notAfter` expires.

If there are claims, `claimsNotice` will contain generic copy in markdown. You must display this mandatory trademark notice to your end users. Use the claims array to loop through and display each claim.

**Example Response:**

```json theme={null}
{
  "domain": "hello.page",
  "claims": [
    {
      "trademark": "EXAMPLE",
      "holder": "Acme Global Holdings Inc.",
      "jurisdiction": "United States Patent and Trademark Office (USPTO)",
      "description": "Class 9: Computer software; Class 42: Software as a service (SaaS) - 123 Main Street, Anytown, CA, 90210, US"
    },
    {
      "trademark": "E.X.A.M.P.L.E",
      "holder": "Beta Financial Group",
      "jurisdiction": "Office of the European Union for Intellectual Property (EUIPO)",
      "description": "Class 36: Financial services, banking, insurance, investment consultation, and electronic funds transfer. - Avenue des Champs-Élysées, PARIS, 75008, FR"
    },
    {
      "trademark": "Example!",
      "holder": "Zeta Media Partners",
      "jurisdiction": "Canadian Intellectual Property Office (CIPO)",
      "description": "Class 16: Printed publications, magazines, and periodicals; Class 41: Entertainment services, namely, providing online video content. - 456 Queen Street, TORONTO, ON, M5V 2H7, CA"
    }
  ],
  "claimsProcessActive": true,
  "claimId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
  "notBefore": "2025-12-01T00:00:00.0Z",
  "notAfter": "2025-12-08T00:00:00.0Z",
  "claimsNotice": "You have received this Trademark Notice because you have applied for a domain name which matches at least one trademark record submitted to the Trademark Clearinghouse.\n\nYou may or may not be entitled to register the domain name depending on your intended use and whether it is the same or significantly overlaps with the trademark listed below. **Your rights to register this domain name may or may not be protected as noncommercial use or \"Fair use\" by the laws of your country.**\n\nPlease read the trademark information below carefully, including the trademarks, jurisdictions, and goods and service for which the trademarks are registered. Please be aware that not all jurisdictions review trademark applications closely, so some of the trademark information may exist in a national or regional registry which does not conduct a thorough or substantive review of trademark rights prior to registration. **If you have questions, you may want to consult an attorney or legal expert on trademarks and intellectual property for guidance.**\n\nIf you continue with this registration, you represent that, you have received and you understand this notice and to the best of your knowledge, your registration and use of the requested domain name will not infringe on the trademark rights listed below. For more information concerning the records included in this notice, see [http://claims.clearinghouse.org](http://claims.clearinghouse.org).\n\nThe following Trademarks are listed in the Trademark Clearinghouse:"
}
```

## 3. Check Domain Availability, Fetch Pricing and Purchase Type

Use the [Check Availability](/api/v1/reference/domains/check-availability) endpoint to ensure the domain is available for purchase and to retrieve `purchasePrice` and `purchaseType` needed for the registration request. Domains with active claims may have premium pricing so in these cases pricing information must also be passed on the create domain request.

Please note: If you are using the [ZoneCheck](/api/v1/reference/domains/zone-check) endpoint, continue using it for your existing search experience. Use the Check Availability endpoint only when you need to purchase a domain that has claims.

**Example Response:**

```json theme={null}
{
  "domainName": "hello.page",
  "premium": true,
  "purchasable": true,
  "purchasePrice": 349.95,
  "purchaseType": "registration",
  "renewalPrice": 349.95,
  "sld": "hello",
  "tld": "page"
}
```

## 4. Submit Domain Create Request

Finally, call the [Create Domain](/api/v1/reference/domains/create-domain) endpoint to register the domain.

**Important Notes:**

* The `claims` parameter must be passed.
* The `purchasePrice` parameter also must be passed. The `purchaseType` parameter should be set (and currently defaults) to `registration`.

**Example Request:**

```json theme={null}
{
  "domain": {
    "domainName": "hello.page"
  },
  "claims": {
    "claimId": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    "notBefore": "2025-12-01T00:00:00.0Z",
    "notAfter": "2025-12-08T00:00:00.0Z"
  },
  "purchasePrice": 349.95,
  "purchaseType": "registration"
}



```

Please Note: If the If the trademark owner takes issue with the registration, the trademark owner could:

* Directly contact the registrant - They can attempt to contact the registrant using the email listed in WHOIS. Even when privacy protection is enabled, the privacy or proxy service typically forwards messages to the actual registrant. From there, the registrant can decide whether to transfer, cancel, or otherwise resolve the issue directly.
* File a complaint under the Uniform Domain Name Dispute Resolution Policy (UDRP) - A dispute-resolution process under the UDRP, offered by providers such as WIPO and others, that allows trademark owners to request the transfer or cancellation of a domain by showing that the name is identical or confusingly similar to their mark, the registrant lacks legitimate rights or interests, and the domain was registered and used in bad faith.
