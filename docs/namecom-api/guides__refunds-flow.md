> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Refunds Flow

> 2-step guide with examples on how to delete and refund domains.

## Steps to Refund a Domain

Use this flow to delete eligible domains and security products during the Add Grace Period (AGP) and automatically issue refunds for the associated order items.

This endpoint:

* Enforces ICANN AGP delete limits
* Applies name.com and reseller-specific refund thresholds
* Supports domain registrations and security product add-ons only

Refunds are issued to the original payment method on file, with a fallback to account credit if the payment method is unavailable or fails. You can check your order history in account settings at [name.com](http://name.com) for this information.

***

## Supported Products

Refunds are supported for the below purchase types:

* `registration`
* `whois_privacy`

All other product types are not eligible. Please note: if a registration refund is requested, associated privacy product will also be deleted/refunded

***

## High-Level Flow

1. Use the [List Orders](/api-reference/orders/list-orders) or [Get Order](/api-reference/orders/get-order) endpoints to verify refund eligibility and retrieve the order ID and order item ID(s) that can be refunded.
2. Request the refund using the [Refunds](/api-reference/refunds/process-refund) endpoint

After submitting a refund request, retrieve the order using the Get Order endpoint to review the updated order details. Once an order item has been officially refunded, its status will be returned as:

```
"status": "refunded"
```

***

## Step 1: Check Refund Eligibility (List Orders)

Use the [List Orders](/api-reference/orders/list-orders) or [Get Order](/api-reference/orders/get-order) endpoints immediately before attempting a refund to validate eligibility and reduce failed refund attempts. If `isRefundable`is true, you can retrieve the `orderID`and associated `orderItemIds`required for the Refunds request.

### How to use

* You can filter `listOrders` results by:
  * `domainName`
  * `createDate`
  * `type`(e.g. `registration`,`whois_privacy`)
  * `orderStatus`
* Check the `isRefundable`field on each order item. If true, you can initiate a refund via the Refunds endpoint. This field already accounts for ICANN AGP limits, reseller-level thresholds, and name.com refund policies.

**Important: Refund eligibility is time-sensitive:**

Even if `isRefundable` is true, eligibility may change between this check and the Refund request (for example, if AGP timing expires or refund thresholds are exceeded).

The Refunds endpoint is the source of truth and may still reject the request.

***

## Step 2: Request a Refund (Refunds Endpoint)

Use the [Refunds](/api-reference/refunds/process-refund) endpoint to delete the domain(s) and issue refunds for eligible order items.

<Warning>
  Send an `X-Idempotency-Key` with your refund request. Retrying the same request with the same key will not trigger duplicate deletions or refunds.
</Warning>

### Request Requirements

* Accepts a JSON body with:
  * `orderId` (required)
  * `orderItemIds` (required array, one or more items)
* Only one `orderId`may be provided per request
* Multiple `orderItemIds`are allowed as long as they belong to the same order
* Supported product types only:
  * `registration`
  * `whois_privacy`
* If WHOIS privacy was purchased on a domain and the domain is refunded, both will be refunded.  It can be an explicit or non-explicit request. (you can submit one item id or two item ids)

Example response: Order with a refunded domain and its associated WHOIS privacy add-on

```
{
  "results": [
    {
      "orderId": 123456,
      "orderItemId": 7891011,
      "orderItemStatus": "refunded",
      "refundAmount": 2.99
    },
    {
      "orderId": 121314,
      "orderItemId": 1516171,
      "orderItemStatus": "refunded",
      "refundAmount": 0
    }
  ],
  "totalRefundAmount": 2.99
}
```

### Full endpoint reference

For the full request/response schema (including errors), see [Refunds: Process Refund](/api-reference/refunds/process-refund).
