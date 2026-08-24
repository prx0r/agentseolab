> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Domain Purchase Pricing

> Which endpoints to call for Create, Renew, and Transfer pricing — Search, Check Availability, Zone Check, Get Pricing, and every purchaseType.

Use this guide to answer: **which endpoint(s) do I call to get the price I must send on Create Domain, Renew, or Transfer?**

<Tip>
  **Recommended:** Scope discovery to `purchaseType: registration` unless you explicitly need aftermarket, expiring, or backorder inventory. Registration is the simplest path — predictable pricing, immediate fulfillment, and standard [Get Pricing](/api/v1/reference/domains/get-pricing-for-domain) flows. Other types are supported but add complexity (flat acquisition fees, term quirks, third-party delays). Pass `purchaseType: registration` on [Search](/api/v1/reference/domains/search) and [Check Availability](/api/v1/reference/domains/check-availability) to filter them out; if checkout returns a different type, treat it as unsupported in your UI until you are ready to handle acquisition pricing.
</Tip>

## Endpoint roles

| Endpoint                                                           | Role                                       | Pricing data                                         | `purchaseType`? |
| ------------------------------------------------------------------ | ------------------------------------------ | ---------------------------------------------------- | --------------- |
| [Zone Check](/api/v1/reference/domains/zone-check)                 | Fast DNS signal for bulk browse UI         | **No** — `available` only                            | **No**          |
| [Check Availability](/api/v1/reference/domains/check-availability) | **Discovery** at checkout                  | **Yes** — `purchasePrice`, `premium`, `purchaseType` | **Yes**         |
| [Search](/api/v1/reference/domains/search)                         | **Discovery** for keyword/suggestion flows | **Yes** — `purchasePrice`, `premium`, `purchaseType` | **Yes**         |
| [Get Pricing](/api/v1/reference/domains/get-pricing-for-domain)    | Registry reg/renew/transfer calculator     | `purchasePrice`, `renewalPrice`, `transferPrice`     | **No**          |
| [TLD Pricing](/api/v1/reference/tld-pricing/tld-price-list)        | TLD-level list prices (non-premium)        | TLD tables only                                      | **No**          |

**Check Availability and Search** return the same result field set but serve different use cases. Search offers keyword-based suggestions while Check Availability is used for specific domain checks.

**Zone Check** cannot price a purchase or determine `purchaseType`. It only indicates whether a name appears free in DNS. Use Check Availability or Search to gather information needed to complete a purchase.

## Two pricing sources for Create Domain

1. **Registry pricing** (`purchaseType: registration`) — standard + registry premium
   * [Get Pricing](/api/v1/reference/domains/get-pricing-for-domain) returns authoritative totals for a given `years`
   * Standard non-premium: omit `purchasePrice` on create
   * Registry premium: **required** `purchasePrice` from Get Pricing with matching `years`

2. **Acquisition pricing** (`aftermarket_s`, `aftermarket_b`, `aftermarket_i`, `expiring`, `backorder`) — *advanced; only if you support non-registration inventory*
   * **Search or Check Availability** returns the flat acquisition `purchasePrice`
   * **Always required** on create; does **not** multiply by `years`

## Create Domain: `purchasePrice` and `years`

| Scenario              | `purchaseType`                                    | `premium`    | `purchasePrice`                             | `years`                                                                |
| --------------------- | ------------------------------------------------- | ------------ | ------------------------------------------- | ---------------------------------------------------------------------- |
| Standard registration | `registration`                                    | `false`      | **Omit** (optional quote from Get Pricing)  | **Set term**                                                           |
| Registry premium      | `registration`                                    | `true`       | **Yes** — from Get Pricing                  | **Set term** — same value on Get Pricing                               |
| Aftermarket           | `aftermarket_s`, `aftermarket_b`, `aftermarket_i` | often `true` | **Yes** — from Search or Check Availability | **Omit or TLD default** — does not affect price or registration length |
| Expiring              | `expiring`                                        | varies       | **Yes** — from Search or Check Availability | **Omit or TLD default** — does not affect price or registration length |
| Backorder             | `backorder`                                       | varies       | **Yes** — from Search or Check Availability | **Omit or TLD default** — does not affect price or registration length |

For `purchaseType: registration`, `premium` determines whether `purchasePrice` is required; `years` sets the registration term. When using Get Pricing to preview or validate, pass the same `years`. For any other `purchaseType`, `purchasePrice` is **always required** — regardless of `premium`.

`purchasePrice` is the domain fee only; Whois Privacy is charged separately when `privacyEnabled` is true.

If you send `purchasePrice`, it must match exactly to the cent or the request will fail.

## Getting the price for Create Domain

1. Call **Search** or **Check Availability** (not Zone Check, not Get Pricing alone). Copy `purchaseType`, `premium`, and note `purchasePrice`.

2. Branch on `purchaseType`:

   **`registration` + `premium: false`**

   * Optional: call Get Pricing with the same `years` to quote the total.
   * On create: omit `purchasePrice`, set `years` (no prior Get Pricing call required).

   **`registration` + `premium: true`** (registry premium)

   * Call Get Pricing with same `years` → pass `purchasePrice` exactly to the cent on create.

   **`aftermarket_s` | `aftermarket_b` | `aftermarket_i` | `expiring` | `backorder`**

   * Use Search or Check Availability `purchasePrice` (flat acquisition fee).
   * Re-check discovery immediately before create — price can change.
   * Do **not** use Get Pricing for create price.
   * `years` does not multiply price or guarantee multi-year registration.

3. Renew and Transfer use Get Pricing separately — see sections below.

## Integrator workflow patterns

Pick the path that matches your UX. Every path should re-run [Check Availability](/api/v1/reference/domains/check-availability) right before [Create Domain](/api/v1/reference/domains/create-domain) as pricing and availability can change.

### Pattern A: Registration only (recommended default)

Standard reseller checkout: fresh registrations and registry premiums only. Pass `purchaseType: registration` on discovery calls.

1. **Discover:** [Search](/api/v1/reference/domains/search) with `purchaseType: registration` — show suggestions, `purchasePrice`, `renewalPrice`; mark premiums.
2. **Checkout:** [Check Availability](/api/v1/reference/domains/check-availability) with `purchaseType: registration` — confirm `purchasable`, `premium`, and `purchasePrice`.
3. **Price:** `premium: false` → omit `purchasePrice`, set `years`. `premium: true` → [Get Pricing](/api/v1/reference/domains/get-pricing-for-domain) with same `years` → pass `purchasePrice` on create.
4. **Purchase:** [Create Domain](/api/v1/reference/domains/create-domain) with `purchaseType: registration`.

Non-matching domains: Check Availability returns them with `purchasable: false`; Search omits them. If checkout still surfaces a non-registration `purchaseType`, treat it as unsupported in your UI.

### Pattern B: Zone Check + Check Availability combination

For bulk browse UIs powered by [Zone Check](/api/v1/reference/domains/zone-check). No Search required — still registration-only.

1. **Browse:** Zone Check → `available` hint for UI only (no pricing or `purchaseType`).
2. **Checkout → purchase:** Follow steps 2–4 of **Registration only** above (`purchaseType: registration` on Check Availability).

### Pattern C: All purchase types (advanced)

Only if you explicitly support aftermarket, expiring, or backorder. **Omit** the `purchaseType: registration` filter.

1. **Discover:** [Search](/api/v1/reference/domains/search) or [Check Availability](/api/v1/reference/domains/check-availability) without a filter — acquisition types may appear alongside registration.
2. **Checkout:** Re-run Check Availability without a filter — confirm `purchaseType`, `premium`, and `purchasePrice` (see [Getting the price for Create Domain](#getting-the-price-for-create-domain); acquisition types use flat discovery fees, not Get Pricing).
3. **Purchase:** [Create Domain](/api/v1/reference/domains/create-domain) with matching `purchaseType` and `purchasePrice` when required.

## Renew Domain

| Scenario         | Price source                                     | `purchasePrice` on renew                         |
| ---------------- | ------------------------------------------------ | ------------------------------------------------ |
| Standard renewal | Get Pricing (optional quote)                     | **Omit**                                         |
| Premium renewal  | Get Pricing `renewalPrice` with matching `years` | **Yes** — pass `renewalPrice` as `purchasePrice` |

Do not use Search or Check Availability `renewalPrice` for premium renewals.

## Transfers

| Scenario          | Price source                 | `purchasePrice` on transfer                       |
| ----------------- | ---------------------------- | ------------------------------------------------- |
| Standard transfer | Get Pricing (optional quote) | **Omit**                                          |
| Premium transfer  | Get Pricing `transferPrice`  | **Yes** — pass `transferPrice` as `purchasePrice` |

Get Pricing `transferPrice` is not affected by the `years` query parameter. `purchasePrice` is the domain transfer fee only; Whois Privacy is charged separately when `privacyEnabled` is true. If you send `purchasePrice`, it must match Get Pricing `transferPrice` exactly to the cent or Create Transfer returns `400` and `"Invalid Price"`. Premium transfers without `purchasePrice` return `"PurchasePrice is required if the domain to transfer is a premium domain"`.

## Registry premium vs acquisition

*Skip this section if you scope discovery to `purchaseType: registration` only.*

Both can show `premium: true` in discovery results, but pricing works differently.

### Registry premium

`purchaseType: registration` with `premium: true`. Call Get Pricing with matching `years`; pass `purchasePrice` on create.

```json theme={null}
{
  "domain": { "domainName": "premiumexample.com" },
  "purchaseType": "registration",
  "years": 2,
  "purchasePrice": 699.90
}
```

### Aftermarket, expiring, and backorder

Flat acquisition fee from Search or Check Availability — `years: 5` with `purchasePrice: 5000` still charges **\$5,000**. Omit `years` or pass the TLD default.

```json theme={null}
{
  "domain": { "domainName": "rarename.com" },
  "purchaseType": "aftermarket_s",
  "purchasePrice": 5000.00
}
```

Check `domain.expireDate` after create; renew to extend registration.

## Standard registration (non-premium)

```json theme={null}
{
  "domain": { "domainName": "example.com" },
  "years": 2
}
```

Omit `purchasePrice` on create. Optionally call Get Pricing with matching `years` to quote the total.

## What not to do

* Do **not** use Zone Check for `purchaseType`, `purchasePrice`, or checkout pricing
* Do **not** use Get Pricing alone to discover how a domain is acquired
* Do **not** use Get Pricing `purchasePrice` for aftermarket, expiring, or backorder create
* Do **not** multiply discovery `purchasePrice` × `years` for acquisition types
* Do **not** use discovery `renewalPrice` for create or premium renew totals
* Do **not** include VAT in `purchasePrice` or derive it from `totalPaid`

## Related endpoints

* [Check Availability](/api/v1/reference/domains/check-availability)
* [Create Domain](/api/v1/reference/domains/create-domain)
* [Create Transfer](/api/v1/reference/transfers/create-transfer)
* [Get Pricing For Domain](/api/v1/reference/domains/get-pricing-for-domain)
* [Renew Domain](/api/v1/reference/domains/renew-domain)
* [Search](/api/v1/reference/domains/search)
* [TLD Price List](/api/v1/reference/tld-pricing/tld-price-list)
* [Zone Check](/api/v1/reference/domains/zone-check)
