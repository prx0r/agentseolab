> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# External Transfers Flow

> How to transfer domains into name.com (transfer in) and prepare domains for transfer out via the Core API, including timing rules and webhooks.

# External Transfers Support — In and Out

This guide covers **external** transfers: moving a domain **from another registrar into name.com** (transfer in), and **preparing a domain to leave name.com** for another registrar (transfer out). The gaining registrar always starts a transfer-out; name.com’s API helps you unlock domains, retrieve auth codes, monitor status, and cancel an outbound transfer when needed.

## Important timing notes

Domains must typically be registered for **at least 60 days** before they can be transferred to a different registrar (ICANN rule).

***

## A) Transfer into name.com (transfer in)

### How it works via the API

#### 1. Initiate a transfer

**`POST /core/v1/transfers`**

Required inputs:

* `domainName`
* `authCode` — EPP / authorization code from the current registrar

See [Create External Transfer In](/api/v1/reference/transfers/create-transfer) for the full request and response schema.

#### 2. Monitor transfer status

* **`GET /core/v1/transfers`** — list transfers\
  [List Transfers](/api/v1/reference/transfers/list-transfers)
* **`GET /core/v1/transfers/{domainName}`** — status for a specific domain\
  [Get Transfer Status](/api/v1/reference/transfers/get-transfer)

Statuses include **pending**, **complete**, **failed**, and others, depending on the API response.

#### 3. Webhook monitoring

Subscribe to **`domain.transfer.status_change`** webhook events to track progress automatically.

See [Webhooks overview](/api/v1/reference/webhook-notifications/overview) (Transfers — external), [Domain Transfer Status Change](/api/v1/reference/webhook-notifications/domain-transfer-status-change), and [Subscribe to Notification](/api/v1/reference/webhook-notifications/subscribe-to-notification).

***

## B) Transfer out of name.com

### How it works

#### 1. Unlock the domain for transfer out

**`PATCH /core/v1/domains/{domainName}`**

Set the domain lock so the domain can leave name.com:

* **`locked`**: `false` (JSON boolean)

See [Update a Domain](/api/v1/reference/domains/update-a-domain).

#### 2. Get the auth code for the customer

**`GET /core/v1/domains/{domainName}:getAuthCode`**

Retrieve the EPP / authorization code to give to the registrant or the gaining registrar.

See [Get Auth Code for Domain](/api/v1/reference/domains/get-auth-code-for-domain).

#### 3. Cancel a transfer-out request (optional)

If you need to cancel a transfer-out request:

**`POST /core/v1/transfers/external/out/{domainName}:cancel`**

See [Cancel External Transfer Out](/api/v1/reference/transfers/cancel-external-transfer-out).

The name.com Core API **does not initiate** transfer-out requests; those are started by the **gaining registrar** after you provide the auth code and the domain is eligible.

#### Webhook monitoring

Subscribe to **`domain.transfer_out.status_change`**:

* **`initiated`** — outbound transfer is pending (domain remains on your account)
* **`completed`** — domain has left name.com
* **`canceled`** — transfer is no longer pending at the registry

See [Webhooks overview](/api/v1/reference/webhook-notifications/overview) and [Domain Transfer Out Status Change](/api/v1/reference/webhook-notifications/domain-transfer-out-status-change).
