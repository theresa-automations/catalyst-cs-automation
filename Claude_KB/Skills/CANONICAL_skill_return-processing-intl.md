# CANONICAL: CS Skill — Return Processing (CatalystLifestyle.com — International)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystLifestyle.com (International)
- **Language Style**: International English
- **Related Policy**: CANONICAL_policy_returns.md

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Return Processing for Catalystlifestyle.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions in this skill apply when:
- Email contains an order number in format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`

> Note: International order numbers do NOT use the `Ms#######` format. They are numeric only (e.g., #67702).

---

## Key Rules (Locked)

- Return window: **30 days from delivery date** (not order date)
- Restocking fee: **5% of order value**; **15% if original packaging or components are missing**
- RMA number required; valid for **15 days** from issuance
- Tracking number required — returns cannot be processed without confirmed tracking
- Refund processing: **5–10 business days** after item is received and inspected
- Return portal: **https://catalystlifestyle.com/pages/returns**
- Support contact: **info@catalystlifestyle.com**
- Never approve or deny a return without verifying eligibility first
- Never promise a refund amount before inspection is complete

---

## Skill Functions

### Function 1: Return Policy Explanation
**Trigger:** Customer asks about return rules without initiating a return
**Examples:** "What's your return policy?" / "How long do I have to return?" / "Are returns allowed?"
**Required Input:** Customer first name (optional)
**Task:** Generate a concise, professional email in **International English** that:
- Explains the return window (30 days from delivery)
- Outlines high-level eligibility criteria
- Reassures the customer
- Provides the self-service return portal URL: https://catalystlifestyle.com/pages/returns
- Uses a warm but professional tone, solution-focused, confident language
- Avoids robotic or legalistic language

**Approved Language:**
> "Our return window is 30 days from the date of delivery. Items must be in original condition with all original packaging and components included."
> "To start a return, please visit our self-service portal at https://catalystlifestyle.com/pages/returns."

**Forbidden:**
- ❌ Any return window other than "30 days from delivery"
- ❌ "No questions asked" — eligibility criteria apply
- ❌ Promising a refund before the return is received and inspected

---

### Function 2: Return Initiation Instructions
**Trigger:** Customer explicitly requests a return, refund, or exchange
**Examples:** "I want to return this item" / "How do I get a refund?" / "Can I exchange for a different size?"
**Required Input:**
- Customer first name
- Order number(s)
- Product name(s)
- Return reason
- Account login URL: https://catalystlifestyle.com/pages/returns
- Return window: 30 days

**Task:** Write a 200–250 word structured instructional email in **International English** that:
- Greets the customer by name
- Directs the customer to the self-service return portal
- Explains how to log in and locate the order
- Lists portal capabilities (bulleted)
- Includes a return eligibility checklist
- Highlights the mandatory tracking requirement
- Sets expectations for approval and next steps
- Uses warm, professional, solution-focused style, avoiding overpromising

**Approved Language:**
> "To get started, please visit our return portal at https://catalystlifestyle.com/pages/returns. Log in with the email address on your order, locate your order, and follow the steps to submit your return request."
> "To avoid a restocking fee, please include all original packaging and components with your return."
> "A tracking number is required to process your return — please send it to us once you have shipped the item."

**Forbidden:**
- ❌ Any return window other than 30 days from delivery
- ❌ Accepting return requests via email without directing to the portal
- ❌ Skipping or minimising the tracking number requirement
- ❌ Approving return eligibility before checking order status

---

### Function 3: Return Approved Notification
**Trigger:** Return has been approved or customer asks about next steps after approval
**Required Input:**
- Customer first name
- Order number(s)
- Product name(s)
- Product photos

**Task:** Generate a professional email in **International English** that:
- Confirms the return is approved
- Instructs the customer to ship the item
- Emphasizes that a tracking number is required
- Explains where and how to send tracking details
- Maintains a warm, solution-focused, confident tone

**Approved Language:**
> "Your return has been approved. Please ship the item back to us and send us your tracking number — we need it to process your return once it arrives."
> "Once we receive and inspect your item, we will process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Issuing or promising a refund before the item has been received
- ❌ Any refund timeline shorter than "5–10 business days after receipt"
- ❌ Confirming the refund amount before inspection is complete

---

### Function 4: Tracking Number Reminder
**Trigger:** Return approved but no tracking provided, or customer asks about refund status
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Write a polite reminder email in **International English** that:
- Requests the tracking number
- Explains why tracking is required
- Instructs how to submit tracking
- Maintains warm, professional, solution-focused tone

**Approved Language:**
> "We have not yet received a tracking number for your return. Please send it to us so we can confirm your shipment and begin processing as soon as your item arrives."
> "Tracking protects both parties and ensures your return is processed as quickly as possible."

**Forbidden:**
- ❌ Processing the refund before a tracking number is received
- ❌ Starting the 5–10 business day refund clock before confirmed tracking

---

### Function 5: Tracking Number Confirmation
**Trigger:** Customer provides tracking information
**Required Input:**
- Customer first name
- Order number(s)
- Tracking number
- Carrier (if provided)

**Task:** Generate a confirmation email in **International English** that:
- Acknowledges receipt of tracking number
- Confirms return is in transit
- Explains inspection upon delivery
- Sets expectations for refund/exchange timeline
- Uses warm, confident, solution-focused style

**Approved Language:**
> "We have received your tracking number — thank you. Your return is on its way. Once it arrives, we will inspect it and process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Stating refund will be issued immediately upon tracking confirmation (inspection required first)
- ❌ Any processing timeline faster than 5–10 business days

---

### Function 6: Return Received Notification
**Trigger:** Return marked as delivered
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Write a processing update email in **International English** that:
- Confirms package received
- Explains inspection and review steps
- Provides clear processing timeline
- Reassures customer
- Maintains warm, professional, solution-focused tone

**Approved Language:**
> "We have received your return. Our team will inspect the item and process your refund or exchange within 5–10 business days. We will contact you as soon as it is complete."

**Forbidden:**
- ❌ Confirming a refund amount before inspection is complete
- ❌ Any timeline shorter than 5–10 business days
- ❌ "Your refund is on its way" before processing is confirmed

---

### Function 7: Refund Confirmation
**Trigger:** Refund successfully processed
**Required Input:**
- Customer first name
- Order number(s)
- Refund method

**Task:** Generate a refund confirmation email in **International English** that:
- Confirms refund was issued
- States payment method used
- Explains bank processing timelines
- Provides support contact: info@catalystlifestyle.com
- Uses warm, professional, confident tone

**Approved Language:**
> "Your refund has been issued to your [payment method]. Depending on your bank, it may take 5–10 business days to appear in your account."
> "If you have any questions, contact us at info@catalystlifestyle.com."

**Forbidden:**
- ❌ Stating a specific posting date (international bank processing times vary)
- ❌ "Instant refund" or same-day language
- ❌ Referencing a refund amount that was not verified first

---

### Function 8: Exchange Shipment Notification
**Trigger:** Replacement item has shipped
**Required Input:**
- Customer first name
- Order number(s)
- New tracking number

**Task:** Write a shipment notification email in **International English** that:
- Confirms exchange has shipped
- Provides tracking details
- Sets delivery expectations
- Maintains warm, professional, solution-focused style

**Approved Language:**
> "Your exchange has shipped. Your tracking number is [tracking number]. You can use it to follow your package at [carrier tracking link]."
> "International delivery estimates vary by destination — the tracking link will have the most current information."

**Forbidden:**
- ❌ Guaranteeing a specific delivery date
- ❌ Sending tracking before confirming shipment is processed

---

### Function 9: Return Denial / Exception Notification
**Trigger:** Return not eligible or cannot be approved
**Required Input:**
- Customer first name
- Order number(s)
- Denial reason

**Task:** Generate a professional, empathetic email in **International English** that:
- Explains why return was denied
- References applicable policy
- Suggests alternatives if possible
- Provides support contact: info@catalystlifestyle.com
- Maintains solution-focused, warm, professional tone, avoiding overpromising

**Approved Language — Outside Return Window:**
> "Your order is outside our 30-day return window, so we are not able to process a return at this stage. If you are experiencing a product issue, it may be covered under our 12-month warranty — please visit https://forms.fillout.com/t/8jPGm4Ck6Xus to submit a claim."

**Approved Language — Condition / Missing Components:**
> "We were not able to approve this return because [reason]. Our policy requires items to be returned in original condition with all original packaging and components included."

**Forbidden:**
- ❌ Approving a return outside the 30-day window without management approval
- ❌ Waiving the restocking fee without management approval
- ❌ "We cannot help you" — always provide policy reason and an alternative path

---

## Policy Reference (Source of Truth)

See: CANONICAL_policy_returns.md for all policy details.

## Key Difference from US Skill
- **Language:** International English (not American English)
- **Order number format:** #67702 style (not Ms#######)
- **Return portal:** https://catalystlifestyle.com/pages/returns
- **Support email:** info@catalystlifestyle.com (not cs@catalystcase.com)
