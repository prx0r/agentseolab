> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# FAQ & Troubleshooting

> Frequently asked questions and troubleshooting guide for name.com Core API

# name.com CORE API – FAQ

<AccordionGroup>
  <Accordion title="What authentication method is required?">
    Use HTTP Basic Authentication with your name.com username and API token. You can use curl's `-u username:token` shorthand or send an explicit `Authorization: Basic <base64(username:token)>` header. See the full [Authentication](/guides/authentication) guide for Linux/macOS and Windows PowerShell commands to generate the Base64 value.
  </Accordion>

  <Accordion title="Is Two-Factor Authentication (2FA) supported with the API?">
    ✅ Yes. You can keep 2FA enabled on your account, but it will block API access until you allow API access as well. Enable the 2FA API Access option in your account settings -> two-step verification to use the API while 2FA remains active.
  </Accordion>

  <Accordion title="Can I call the API from JavaScript in the browser?">
    ❌ No. The API is for server-side use only. Browser requests are blocked due to CORS restrictions.
  </Accordion>

  <Accordion title="Can I use PowerShell?">
    ✅ Yes. Any tool that can send HTTPS requests — including PowerShell, curl, Python, or Node.js — is supported. For a PowerShell example to generate the Basic Auth header, see [Authentication](/guides/authentication).
  </Accordion>

  <Accordion title="Which port should I use?">
    All API requests must use HTTPS on port 443.
  </Accordion>

  <Accordion title="Are production and sandbox accounts synced?">
    ❌ No. Domains, DNS records, and user data are completely separate between environments.
  </Accordion>

  <Accordion title="Does the sandbox environment exactly match production?">
    ❌ No. The sandbox uses registry test data, so domain availability and behavior may differ.
  </Accordion>

  <Accordion title="How can I test domain registration without real charges?">
    Use the sandbox environment (`https://api.dev.name.com`) with your -test username and sandbox API token. Sandbox domains are not live or publicly registered. See [Testing environment](/guides/testing-environment) for sandbox constraints and differences from production.
  </Accordion>

  <Accordion title="What status codes does the API use?">
    The API uses standard RESTful HTTP codes like 200 OK, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, and 429 Too Many Requests.
  </Accordion>

  <Accordion title="Why is my GetDomain request failing?">
    The domain must exist in the environment you're querying. Check whether you're using sandbox or production.
  </Accordion>

  <Accordion title="What is the domain search limit?">
    You can check up to 50 domains per checkAvailability call.
  </Accordion>

  <Accordion title="What happens if I hit the rate limit?">
    You'll receive a 429 Too Many Requests error. Use backoff logic and retry after a delay.
  </Accordion>

  <Accordion title="Can I use saved payment profiles with the API?">
    ✅ Yes. You can use saved credit card profiles and account credit for domain purchases via the API. Ensure your preferred payment method is set as the default payment method within your account.
  </Accordion>

  <Accordion title="How do I know when a new API version is available?">
    🔔 Check the Changelog for the latest version releases, features, and any upcoming deprecations.
  </Accordion>
</AccordionGroup>

## Next Steps

<CardGroup cols={2}>
  <Card title="Getting Started Guide" icon="rocket" href="/guides/getting-started">
    Set up authentication, environments, and make your first API call
  </Card>

  <Card title="Explore API Resources" icon="code" href="/api/v1/reference">
    View endpoints for domains, DNS, transfers, and more
  </Card>

  <Card title="Changelog" icon="calendar" href="/api/v1/changelog">
    Track new features, breaking changes, and deprecations
  </Card>

  <Card title="Contact Support" icon="mail" href="mailto:reseller@name.com">
    Reach out for help with advanced issues or account-specific questions
  </Card>
</CardGroup>
