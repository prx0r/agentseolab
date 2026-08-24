> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Contact Verification Compliance

> ICANN contact verification email requirements, reseller logging obligations, and how to integrate contact verification endpoints + webhooks without duplicating documentation.

## What this guide covers

This guide covers:

* **How name.com contact verification works** (timelines, email types, and how to observe verification status).
* **How to integrate status updates** via the `contact.verification.status_change` webhook.
* **What changes when you handle verification yourself** (approved/contracted resellers): logging requirements, required email content, and account-restricted endpoints.

If you’re looking for endpoint request/response schemas, use the API reference pages directly:

* `GET /core/v1/contacts/unverified` → [List Unverified Contacts](/api/v1/reference/contact-verification/list-unverified-contacts)
* `POST /core/v1/contacts/verify/{verificationId}` → [Verify Contact](/api/v1/reference/contact-verification/verify-contact)
* `POST /core/v1/contacts/verify/{verificationId}:resend` → [Resend Verification Email](/api/v1/reference/contact-verification/resend-verification-email)
* `contact.verification.status_change` → [Contact Verification Status Change webhook](/api/v1/reference/webhook-notifications/contact-verification-status-change)

## When this guide applies

You should follow this guide if you do any of the following:

* Need to understand **when verification emails are sent** and what the **15-day verification timeline** means for domains.
* Want to **monitor verification status** in your product using endpoints and/or webhooks.
* Have an approved / contracted setup where you **send your own verification emails** and/or **sync verified state** to name.com.

<Info>
  For most reseller integrations, **name.com sends the ICANN-required verification emails** for you. If you want to handle verification emails (or verification state syncing) yourself, this is typically an **approved / contracted** workflow so we can confirm you will meet ICANN requirements (including logging and required email content).
</Info>

## Part 1: How contact verification works (most resellers)

This section is for most resellers. It explains how verification works, the ICANN-required email timeline, and how to observe verification status in your integration.

### What “verification” means

Verification means the registrant has demonstrated control of the email address (or phone number, where applicable) associated with the registrant contact.

If verification is not completed within the required window, a verification lock will be applied and the domain will stop resolving. See [Understanding Domain Locks](/guides/domain-locks).

### ICANN verification email timeline (what gets sent)

These requirements apply when **ICANN requires verification** of the registrant contact (typically email).

| Email                                            | Trigger                                                                                                                                 | Required content                                                                                                                                                                                                                                                |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Registrant verification (expires in 15 days)** | Domain registration, incoming or account transfer with unverified contacts, or changes to the registrant’s email, name, or organization | A clear statement that ICANN requires verification of the registrant contact. A unique verification link or token the user must click or use. A warning that failure to verify within 15 days will result in domain suspension.                                 |
| **Verification reminder**                        | Before the 15‑day window expires                                                                                                        | A clear statement that ICANN requires verification of the registrant contact. A unique verification link or token the user must click or use. A warning that failure to verify within 15 days will result in domain suspension, including how many days remain. |
| **Verification expired / suspension notice**     | Day 16+ (when the domain is disabled)                                                                                                   | Notification that the domain is suspended and the reason (failure to verify registrant contact). Mention that this is ICANN-required. Provide a path to resolve (for example: a verification link).                                                             |

<Info>
  For new registrants, you must also communicate:
  The Organization field in your domain’s contact details relates to legal ownership. If this field contains information, the listed organization is considered the legal “Registered Name Holder” (domain owner).
</Info>

### How to observe verification status

* `GET /core/v1/contacts/unverified` → [List Unverified Contacts](/api/v1/reference/contact-verification/list-unverified-contacts)

<Info>
  After a new domain registration or contact change, unverified contacts may take up to \~10 minutes to appear in the API. Build your UI and automation with this delay in mind.
</Info>

### Status updates via webhook

To avoid polling, subscribe to the contact verification status webhook:

* Event: `contact.verification.status_change`
* Reference: [Contact Verification Status Change webhook](/api/v1/reference/webhook-notifications/contact-verification-status-change)

<Tip>
  Verify webhook authenticity using HMAC signatures. See [HMAC Signature Verification](/guides/hmac-examples).
</Tip>

To create/manage webhook subscriptions:

* [Subscribe to notification](/api/v1/reference/webhook-notifications/subscribe-to-notification)
* [Get subscribed notifications](/api/v1/reference/webhook-notifications/get-subscribed-notifications)
* [Modify subscription](/api/v1/reference/webhook-notifications/modify-subscription)
* [Delete subscription](/api/v1/reference/webhook-notifications/delete-subscription)

## Part 2: Handling your own verification (approved / contracted resellers)

This section is for resellers who have agreed to additional terms and are handling contact verification themselves. This typically includes additional compliance requirements and may include account-restricted endpoint access.

If you want to discuss enablement, email [reseller@name.com](mailto:reseller@name.com).

### Logging requirements

If you send your own verification emails (and disable name.com-sent emails) and/or use account-restricted contact verification endpoints, you must maintain the following logs.

#### Email logs (ICANN verification emails)

Keep logs for every verification-related email you send:

* **Domain**
* **Email send event**
* **Timestamp**
* **Recipient**
* **Subject**
* **Content** (or a reference to a stored template + the rendered variables used)

#### Verification logs

Keep logs that show how you verified the registrant contact off-platform:

* **Domain** and the **`verificationId`** being verified
* **Verification method** (email or phone)
* **Email address or phone number** used for verification
* **Verification timestamp**

#### Retention and access

* **Retention**: All required logs must be kept for the duration of the domain registration and for at least **two (2) years thereafter**.
* **Access**: name.com may request access to these logs at any time.

#### What you must provide before enablement

Before we grant you access to programmatic contact verification and allow you to disable name.com-sent emails, you must provide:

* **Sample logs** demonstrating the format above
* **Sample email copies** (templates and/or example sends)

### Endpoint usage & policy

Some Contact Verification endpoints are **account-restricted**. The reference pages will call this out, and you can email [reseller@name.com](mailto:reseller@name.com) to request access.

#### List Unverified Contacts

**Purpose**: Identify contacts that require verification under ICANN rules.

* Endpoint: `GET /core/v1/contacts/unverified` → [List Unverified Contacts](/api/v1/reference/contact-verification/list-unverified-contacts)
* Typical use: Drive your own verification flow (email or phone) before calling Verify Contact (if approved).

#### Verify Contact

**Purpose**: Programmatically marks a contact’s email address as verified for domains under your account (to satisfy ICANN contact-verification requirements).

* Endpoint: `POST /core/v1/contacts/verify/{verificationId}` → [Verify Contact](/api/v1/reference/contact-verification/verify-contact)
* Availability: **Account-restricted (approved reseller accounts only)**
* Retry safety: Send `X-Idempotency-Key` so retries are safe

<Info>
  This endpoint is account-restricted. Enablement is typically associated with handling your own verification process and meeting ICANN compliance requirements (logging and required email content).
</Info>

#### Allowed use

* **You are the reseller of record** and the contact belongs to a domain in your account.
* You have **already verified** control of the email address or phone number **off-platform** (for example: your own email verification link flow) and are syncing that verified state to name.com.
* You are acting on behalf of the registrant and have their permission to mark the contact as verified.

#### Not allowed

* Verifying contacts you don’t manage
* Marking contacts verified without actually verifying the email/phone
* Acting without registrant authorization

#### Enforcement

We may suspend access to this endpoint if we detect misuse.

#### Resend the initial verification email

If a contact verification is pending and you need to resend the initial verification email, use:

* `POST /core/v1/contacts/verify/{verificationId}:resend` → [Resend Verification Email](/api/v1/reference/contact-verification/resend-verification-email)

<Info>
  This endpoint is throttled (for example: per-`verificationId` and per-account rate limits). See the endpoint reference for the current limits and the `nextEligibleAt` cooldown timestamp returned in responses.
</Info>

## Other ICANN-required emails

For more detailed information about ICANN-required emails, see [Registrant Communication Options](/guides/registrant-communications).
