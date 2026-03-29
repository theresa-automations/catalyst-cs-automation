# CANONICAL: CS Skill — Return Tracking & Post-Approval (CatalystLifestyle.com — International)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystLifestyle.com (International)
- **Language Style**: International English

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Return Tracking & Post-Approval for Catalystlifestyle.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`

---

## Key Rules (Locked)

- Tracking number required — return processing cannot begin without confirmed tracking
- Refund processing: **5–10 business days** after item is received and inspected
- Exchange ships after return is received and inspected — not before
- Never confirm a refund amount before inspection is complete
- Refund issued to original payment method only
- Support contact: **info@catalystlifestyle.com**

---

## Skill Functions

### Function 1: Tracking Number Request
**Trigger:** Return approved but no tracking provided, or customer asks about refund status
**Required Input:** Customer first name, Order number(s)

**Task:** Polite reminder email in **International English** — request tracking number, explain why it is needed, instruct how to submit, warm and solution-focused tone.

**Approved Language:**
> "We have not yet received a tracking number for your return. Please send it to us so we can confirm your shipment and begin processing as soon as your item arrives."
> "Tracking ensures your return is processed as quickly as possible."

**Forbidden:**
- ❌ Processing or promising a refund before tracking is received
- ❌ Starting the 5–10 business day refund clock before confirmed tracking

---

### Function 2: Tracking Number Confirmation
**Trigger:** Customer provides tracking information
**Required Input:** Customer first name, Order number(s), Tracking number, Carrier (if provided)

**Task:** Confirmation email in **International English** — acknowledge tracking, confirm in transit, explain inspection, set refund/exchange timeline expectations, warm and confident.

**Approved Language:**
> "We have received your tracking number — thank you. Your return is on its way. Once it arrives, we will inspect it and process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Stating refund will be issued immediately upon tracking receipt
- ❌ Any refund timeline shorter than 5–10 business days after receipt

---

### Function 3: Return Delivered — Processing Update
**Trigger:** Return marked as delivered
**Required Input:** Customer first name, Order number(s)

**Task:** Processing update email in **International English** — confirm receipt, explain inspection steps, provide timeline, reassure customer, warm and professional.

**Approved Language:**
> "We have received your return. Our team will inspect the item and process your refund or exchange within 5–10 business days. We will contact you as soon as it is complete."

**Forbidden:**
- ❌ Confirming a refund amount before inspection is complete
- ❌ Any timeline shorter than 5–10 business days
- ❌ "Your refund has been processed" before inspection is done

---

### Function 4: Refund Confirmation
**Trigger:** Refund successfully processed
**Required Input:** Customer first name, Order number(s), Refund method

**Task:** Refund confirmation email in **International English** — confirm refund issued, state payment method, explain bank timelines, provide support contact: info@catalystlifestyle.com, warm and confident.

**Approved Language:**
> "Your refund has been issued to your [payment method]. Depending on your bank, it may take 5–10 business days to appear in your account."
> "If you have any questions, contact us at info@catalystlifestyle.com."

**Forbidden:**
- ❌ Stating a specific posting date (international bank processing times vary)
- ❌ "Instant refund" or same-day language

---

### Function 5: Exchange Shipped
**Trigger:** Replacement item has shipped
**Required Input:** Customer first name, Order number(s), New tracking number

**Task:** Shipment notification email in **International English** — confirm exchange shipped, provide tracking, set delivery expectations, warm and professional.

**Approved Language:**
> "Your exchange has shipped. Your tracking number is [tracking number]. You can use it to follow your package at [carrier tracking link]."
> "International delivery times vary by destination — the tracking link will have the most current information."

**Forbidden:**
- ❌ Guaranteeing a specific delivery date
- ❌ Shipping exchange before return is received and inspected

---

### Function 6: Return Denied / Exception
**Trigger:** Return not eligible
**Required Input:** Customer first name, Order number(s), Denial reason

**Task:** Professional, empathetic email in **International English** — explain denial, reference policy, suggest alternatives, provide contact: info@catalystlifestyle.com, solution-focused and warm.

**Approved Language — Outside Return Window:**
> "Your order is outside our 30-day return window, so we are not able to process a return at this stage. If you are experiencing a product issue, it may be covered under our 12-month warranty — please visit https://forms.fillout.com/t/8jPGm4Ck6Xus to submit a claim."

**Approved Language — Condition / Missing Components:**
> "We were not able to approve this return because [reason]. Our return policy requires items in original condition with all original packaging and components included."

**Forbidden:**
- ❌ Approving a return outside the 30-day window without management approval
- ❌ "We cannot help you" — always provide an alternative path

---

## Key Difference from US Skill
- **Language:** International English
- **Order number format:** #67702 style
- **Support email:** info@catalystlifestyle.com
