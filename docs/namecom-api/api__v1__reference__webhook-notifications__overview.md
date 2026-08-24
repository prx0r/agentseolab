> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Webhooks Overview

> How name.com webhook notifications work and how to subscribe.

# Webhooks

name.com can send **HTTP POST** requests to a URL you provide when specific domain or account events occur. Each request includes a JSON body with an `eventName` field that identifies the event type.

## How it works

1. **Choose event types** — Pick one or more `eventName` values (for example `domain.transfer.status_change`).
2. **Create a subscription** — Call [Subscribe to Notification](/api/v1/reference/webhook-notifications/subscribe-to-notification) with your callback URL and the event names you want.
3. **Handle POST requests** — Your server receives payloads when those events occur. Respond with `2xx` to acknowledge delivery.
4. **Verify signatures** — Every request includes `X-NAMECOM-SIGNATURE`. Validate it before processing. See [HMAC signature verification](/guides/hmac-examples).

Manage subscriptions anytime with [Get Subscribed Notifications](/api/v1/reference/webhook-notifications/get-subscribed-notifications), [Modify Subscription](/api/v1/reference/webhook-notifications/modify-subscription), or [Delete Subscription](/api/v1/reference/webhook-notifications/delete-subscription).

<Info>
  Event names are stable API identifiers. Use the exact `eventName` string from the payload reference page when subscribing and when routing in your handler (for example `domain.transfer.status_change`, not a display label).
</Info>
