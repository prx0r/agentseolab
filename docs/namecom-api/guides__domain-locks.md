> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Understanding Domain Locks

> Overview of verification, compliance/security, and customer-controlled domain locks, including when they apply and their impact.

## Verification Locks

These locks are applied due to the mandatory ICANN requirement to verify domain contact information within 15 days of registration or change.

### VerificationClientHold (High Volume Reseller Domains)

* Applied to: Reseller domains when contacts are not verified within 15 days. This lock is applied at the registry level.
* Impact: The domain is removed from the DNS and will not resolve (it goes completely offline).

### VerificationHold (Retail Customers and Medium-Low Volume Reseller Domains)

* Applied to: Retail customer and medium-low volume reseller domains when contacts are not verified within 15 days.
* Impact: The domain is redirected to a name.com landing page that explains the ICANN contact verification requirement.

## Compliance & Security Locks

These locks are applied for policy, security, legal reasons, or by the customer for enhanced protection.

### ClientHold (Compliance/Abuse)

* Applied to: Deactivate a domain, typically for serious policy violations or abusive activity (e.g., DNS Abuse, CSAM, Fraud).
* Impact: The domain is removed from the DNS and will not resolve (it goes completely offline).

### ExpirationClientHold (Post-Expiration)

* Applied to: Domains for certain reseller accounts after expiration.
* Purpose: Applies a ClientHold status at the registry to ensure the domain is removed from the DNS and will not resolve. This status removes the domain from the global DNS system, meaning the domain's website, email, and other services will be inaccessible.

### RegistrarLock / AccountLock (Administrative/Legal)

* Applied to: Domains due to compliance or legal complaints.
* Restrictions: Prohibits Client Transfers (Registrar to Registrar) and Account Transfers (internal name.com transfers). All domain modifications are disabled (DNS/nameservers and contact changes).

### TransferLock (60-Day Lock)

* Applied to: Triggered by new domain registrations, transfers into name.com, and specific contact updates (unless the registrant opts out of the 60-day lock).
* Restriction: Prohibits Client Transfers (registrar to registrar) for 60 days.
* Key Difference: This lock does NOT prevent DNS, nameserver, or contact changes—only transfers out are blocked.

### PrivacyLock (Customer Controlled - Requires 2FA)

* Applied to: A security lock controlled by the customer that has the same strong restrictions as RegistrarLock/AccountLock.
* Requirement: Two-Factor Authentication (2FA) must be set up on the account to enable this lock, and a 2FA code is required to disable it.
* API Note: This lock cannot be managed via the API and must be done on the name.com retail site.
