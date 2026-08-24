> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Domain Renewals & Expiration

> How domain renewals and post-expiration recovery work for Core API resellers — auto-renew, manual renew, Guaranteed Renewal Window, webhooks, and when to use the API vs the name.com Renewal Center.

# Domain Renewals & Expiration

This guide covers how to renew domains through the Core API, what happens when a domain expires, which webhooks signal lifecycle changes, and when to use the name.com web UI for recovery after a domain leaves your API account.

Timelines vary by TLD. Always confirm the **Guaranteed Renewal Window** length with [`expirationGracePeriod`](/api/v1/reference/domain-info/get-specific-tld-requirements-v2) from the TLD requirements endpoints.

***

## Renewal options (while the domain is in your account)

You have two primary options for renewing domains **before** they leave your account inventory.

### 1. Enable auto-renew

* Automatically renews domains on your account’s renewal schedule
* Timing is configurable to **\~30 days before expiration** or **\~7 days before expiration**
* Set per domain with `autorenewEnabled` on [Update Domain](/api/v1/reference/domains/update-a-domain), or manage domains in the [name.com portal](https://www.name.com/account/domain)
* Account-wide renewal schedule settings live under [payment / account settings](https://www.name.com/account/paymentprofile) (renewal setting and renewal schedule)

### 2. Manual renewal (API or dashboard)

* Renew programmatically with [Renew Domain](/api/v1/reference/domains/renew-domain), or renew in the [name.com portal](https://www.name.com/account/domain)
* Prefer batching renewals (for example up to \~500 at a time) and always pass idempotency keys
* Manual renewal gives you control over exact timing

If a domain has expired but is still within the **Guaranteed Renewal Window** described below, renewing via [Renew Domain](/api/v1/reference/domains/renew-domain) restores the domain and records so their site can resume service. (typically \~25 days after expiration for many gTLDs; DNS and other services depend on the registry and any locks applied after expiration).

<Info>
  Domain renewals are **non-refundable**. If a customer disputes a domain renewal, advise them to disable auto-renew and let the domain expire naturally out of the account. Provide clear communication leading up to renewal so customers can make adjustments before the domain renews. You can also charge the customer first and renew slightly later if you need tighter billing control.
</Info>

***

## ICANN-required renewal emails

If you manage registrant communications, you are responsible for ICANN-required renewal notices (pre-expiry reminders and a post-expiry recovery notice).

In addition to the ICANN-required emails, we recommend sending supplemental communications based on the renewal type, along with additional reminder emails to improve customer awareness and coverage. The \~month-before and \~week-before expiration messages are reminder communications; send order confirmation emails once renewal actually occurs.

See [Registrant Communications](/guides/registrant-communications#renewal) for required timing, content, and contact models.

***

## Post-expiration lifecycle

If a domain is not renewed before `expireDate`, it moves through the stages below. Day ranges are typical for common gTLDs (for example `.com`); always confirm your TLD with `expirationGracePeriod`.

<img src="https://mintcdn.com/namecom/80UMtVTPsDuNXn4b/assets/domain_lifecycle.png?fit=max&auto=format&n=80UMtVTPsDuNXn4b&q=85&s=72c4c7b355742d53a745e0abf4be9e5a" alt="Domain Name Lifecycle" width="5240" height="800" data-path="assets/domain_lifecycle.png" />

### 1. Domain Expires (day 0)

* The domain reaches its expiration date
* DNS, website, and email may stop working depending on the registry and any post-expiration locks (see [ExpirationClientHold](/guides/domain-locks#expirationclienthold-post-expiration))
* Subscribe to [`domain.expiration`](/api/v1/reference/webhook-notifications/domain-expiration) for an informational signal that the Guaranteed Renewal Window has started — **do not** remove the domain from your systems yet

### 2. Guaranteed Renewal Window (days 1–25)

This is the same as the account / renewal grace period for API inventory. Length comes from [`expirationGracePeriod`](/api/v1/reference/domain-info/get-specific-tld-requirements-v2) on the TLD requirements endpoints — the number of days after expiration you can renew **before the domain is removed from your account**.

* **Typical duration:** up to \~25 days for many gTLDs (for example `.com`). Some TLDs are shorter — use [Get TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements-v2)
* **Pricing:** Standard renewal pricing applies
* **Action:** Renew via [Renew Domain](/api/v1/reference/domains/renew-domain) or the name.com dashboard

This is the window where the Core API **guarantees** you can renew while the expired domain remains in your account.

### 3. Extended Renewal Window (days 26–43)

* The domain **leaves your API inventory**: Get/List no longer return it once `expirationGracePeriod` has passed
* You receive [`account.domain.removal`](/api/v1/reference/webhook-notifications/account-domain-removal) with `reason: expiration` (if subscribed)
* **Further renewal may still be possible** in the name.com [Renewal Center](https://www.name.com/account/renewalcenter) for this limited window (typically \~days 26–43 for common gTLDs; registry and TLD-dependent)
* Extended renewal is **not guaranteed**. It is available through the name.com UI only

### 4. Redemption Grace Period (days 44–74)

* After the registry’s delete / redemption window begins, standard renewal is no longer available
* Domains may still be recoverable via **redemption** (restore) in the [Renewal Center](https://www.name.com/account/renewalcenter)
* Redemption typically includes a redemption fee plus a renewal term; fees and availability are registry-specific
* Redemption is **not guaranteed**. It is available through the name.com UI only

### 5. Pending Delete at Registry (days 75–79)

* The domain is scheduled for final deletion at the registry
* **No recovery** is possible

### 6. Domain Released (day 79+)

* After pending delete completes, the domain may become publicly available again

<Warning>
  After the Guaranteed Renewal Window (`expirationGracePeriod`) ends, treat the domain as **gone from your API account**. Any later renew or redeem action is best-effort through the name.com web UI only. Do not assume Get/List or Renew Domain will succeed.
</Warning>

***

## Where to take each action

| Action                                              | Where               | When / notes                                                                                                                                                       |
| --------------------------------------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Enable or disable auto-renew                        | **Both** (API + UI) | While the domain is still in your account ([Update Domain](/api/v1/reference/domains/update-a-domain) or [domain management](https://www.name.com/account/domain)) |
| Renew at standard renewal price                     | **Both** (API + UI) | Before expiry, and during the Guaranteed Renewal Window (`expirationGracePeriod`) while Get/List still return the domain                                           |
| Get or list the domain                              | **API**             | Only while the domain remains in your account inventory (through the Guaranteed Renewal Window)                                                                    |
| Receive lifecycle push notifications                | **Webhooks**        | `domain.expiration` at day 0; `account.domain.removal` when the Guaranteed Renewal Window ends                                                                     |
| Renew in the Extended Renewal Window (\~days 26–43) | **UI only**         | [Renewal Center](https://www.name.com/account/renewalcenter)                                                                                                       |
| Redeem / restore (Redemption Grace Period)          | **UI only**         | [Renewal Center](https://www.name.com/account/renewalcenter)                                                                                                       |
| Recover after Pending Delete                        | —                   | Not possible                                                                                                                                                       |

***

## Webhooks for lifecycle changes

Subscribe via [Subscribe to Notification](/api/v1/reference/webhook-notifications/subscribe-to-notification). See [Webhooks overview](/api/v1/reference/webhook-notifications/overview) and [HMAC examples](/guides/hmac-examples).

| Event                                                                                                                 | When it fires                                                             | What you should do                                                                                                             |
| --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| [`domain.expiration`](/api/v1/reference/webhook-notifications/domain-expiration)                                      | Domain expires (day 0) and enters the Guaranteed Renewal Window           | Notify your customer and renew via API while still in the Guaranteed Renewal Window. **Keep** the domain in your inventory.    |
| [`account.domain.removal`](/api/v1/reference/webhook-notifications/account-domain-removal) (`reason: expiration`)     | Domain leaves your account when the Guaranteed Renewal Window ends        | Archive / drop from your DB. Further recovery (if any) is in the [Renewal Center](https://www.name.com/account/renewalcenter). |
| [`account.domain.removal`](/api/v1/reference/webhook-notifications/account-domain-removal) (`reason: agp_refund`)     | Domain deleted via AGP refund                                             | Same inventory cleanup; see [Refunds flow](/guides/refunds-flow).                                                              |
| [`account.domain.removal`](/api/v1/reference/webhook-notifications/account-domain-removal) (`reason: administrative`) | Ops / support removal                                                     | Archive from inventory.                                                                                                        |
| [`domain.lock.status_change`](/api/v1/reference/webhook-notifications/domain-lock-status-change)                      | Locks change, including `ExpirationClientHold` for some reseller accounts | Update status in your UI; services may stop resolving. See [Domain locks](/guides/domain-locks).                               |
| [`domain.transfer_out.status_change`](/api/v1/reference/webhook-notifications/domain-transfer-out-status-change)      | Domain transfers to another registrar                                     | Separate from expiration — see [External transfers](/guides/external-transfers-flow).                                          |

***

## Important notes

* Timelines and behavior **vary by TLD and registry**. Confirm the Guaranteed Renewal Window with `expirationGracePeriod` via [Get TLD Requirements](/api/v1/reference/domain-info/get-specific-tld-requirements-v2).
* Some TLDs have a **shorter** Guaranteed Renewal Window than 25 days.
* Redemption fees and policies are **registry-specific**.
* To minimize risk, encourage users to enable **auto-renew** and send clear customer reminders before expiration.
* Post-expiration holds for some reseller configurations are covered under [ExpirationClientHold](/guides/domain-locks#expirationclienthold-post-expiration).
