# Authoritative domain verification contract

Never map `no DNS records` to `available`.

Canonical states:
- AVAILABLE
- TAKEN
- RESERVED
- PREMIUM
- UNKNOWN

Evidence pipeline:
1. validate label/TLD/public suffix
2. DNS signal (fast, non-authoritative)
3. RDAP/registry registration evidence
4. registrar authoritative availability/price API
5. optional independent registrar confirmation

Each evidence item stores:
source, method, status, observed_at, raw_status_code/reference, authoritative flag.

The final state is a deterministic resolver over evidence. Conflicts resolve to UNKNOWN and trigger recheck rather than optimistic availability.

Pricing should store registration, renewal, transfer, privacy/add-ons, currency and timestamp. Rank registrars by total cost over a declared horizon, not only first-year promotional price.
