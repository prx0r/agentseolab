> ## Documentation Index
> Fetch the complete documentation index at: https://docs.name.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Registrant Communications

> Registrant email obligations (verification, renewals, transfers) plus recommended contact approaches and communication options for resellers.

## Contacts approach

**Reseller-as-Contact** optimizes for speed and reliability, while **End-User-as-Contact** optimizes for clear ownership at the cost of verification and email complexity.

Name.com offers three routes you can take with comms:

* **Reseller as contact** (you set yourself as the registrant contact): end users will not receive emails from name.com; your contact will
* **Name.com sends required emails on your behalf** (whitelabeling available upon request; see [Reseller Whitelabeled Email Examples](https://docs.google.com/presentation/d/158CMhH2HcHzg9RzqgCQDk0iFlYijY4vDqtkDkjVDTfw/edit?usp=sharing))
* **You send your own emails** (requires logging evidence)

Please reach out to [reseller@name.com](mailto:reseller@name.com) for more information.

To learn more about verification flows and logging requirements for sending your own emails, see the [Contact Verification Compliance Guide](/guides/contact-verification).

## Reseller as contact

### Pros

* Simplified onboarding
* High contact verification success (no domains disabled due to verification)
* Full control over domain management

### Key risk: reseller as registrant of record

When the reseller is set as the registrant/admin contact, the reseller is the legal owner of the domain in ICANN and registry systems. While this reduces friction at registration time, it shifts ongoing responsibility to the reseller, including:

* Mediating ownership and transfer requests if a customer wants to move or reclaim a domain
* Receiving and responding to ICANN compliance, abuse, and policy notices
* Managing all domain issues, recovery requests, and edge cases on behalf of customers

<Warning>
  Because the reseller is the registrant of record, legal notices (e.g., cease-and-desist letters, takedown requests, and potential lawsuits) are served to the reseller, not the end customer.
</Warning>

As domain volume grows, this model can increase support load, compliance responsibility, and operational risk. Resellers using this approach should clearly document domain ownership and customer rights in their terms of service.

## End user as contact

### Pros

* Clear end-customer ownership of domains
* Avoids reseller legal ownership and liability described above

### Cons

* Lower contact verification success rates
* Requires reliable end-user email delivery
* Verification, renewal, and compliance emails must either be white-labeled or fully owned by the reseller. If you’d like to fully take over emails and the verification process, please reach out to our team.
* Higher onboarding and operational complexity

## ICANN-required registrant emails

### Verification

| Email                                            | Trigger                                                                                                                    | Content                                                                                                                                                                                                                                                                              |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Registrant verification (expires in 15 days)** | Domain registration or incoming transfer with an unverified registrant contact, **or** changes to the registrant’s contact | A clear statement that ICANN requires verification of the registrant contact. A unique verification link or token the user must click or use. A warning that failure to verify within 15 days will result in domain suspension.                                                      |
| **Verification reminder**                        | Before the 15‑day window expires                                                                                           | A clear statement that ICANN requires verification of the registrant contact. A unique verification link or token the user must click or use. A warning that failure to verify within 15 days will result in domain suspension and note how many days registrant has left to verify. |
| **Verification expired / suspension notice**     | Day 16+ (when domain is disabled)                                                                                          | Notification that the domain is suspended. The reason: failure to verify registrant contact (usually email). Mention that this is an ICANN-required process. A path to resolve (e.g., verification link).                                                                            |

<Info>
  The below also must be shared with new registrants:
  The Organization field in your domain’s contact details relates to legal ownership. If this field contains information, the listed organization is considered the legal “Registered Name Holder” (domain owner).
</Info>

### Renewal

| Email                               | Trigger                                                                                    | Content                                                                                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Renewal notices (pre-expiry)**    | At least 2 notices before expiration: (1) \~30 days before, (2) \~5 days before expiration | Remind registrant of upcoming expiration. Must clearly state domain name, expiration date, and renewal instructions.                   |
| **Renewal failure / expiry notice** | Within 5 days after expiration (if domain not renewed)                                     | Notice that the domain has expired but may still be renewed/redeemed. Must include info on how to recover the domain and the deadline. |

### Transfers, change of registrant, and contact review

| Email                                     | Trigger                                                                                                                             | Content                                                                                                                                                                                                                                                                                            |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Transfer out (FOA – losing registrar)** | When a transfer is requested away from the current registrar (the “losing” registrar)                                               | Confirmation email to both old and new registrant addresses (if applicable). Must explain that a change has been requested and provide means to cancel.                                                                                                                                            |
| **Change of registrant confirmation**     | Registrant contact information changed                                                                                              | Confirmation email to both old and new registrant addresses. Must explain that a change has been made.                                                                                                                                                                                             |
| **Whois Data Reminder Policy (WDRP)**     | Annually for each domain (usually 120–30 days before expiration). Must be sent once per year per domain regardless of renewal cycle | Reminder to review and update WHOIS contact information. Provide a path to update if needed. Must state that providing false contact info can lead to suspension or cancellation. Contact information includes: Registrant Name, Organization (if provided), Email Address, Phone Number, Address. |
