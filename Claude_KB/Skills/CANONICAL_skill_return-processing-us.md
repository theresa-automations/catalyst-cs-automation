# CANONICAL: CS Skill — Return Processing (CatalystCase.com — US)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystCase.com (US)
- **Language Style**: American English
- **Related Policy**: CANONICAL_policy_returns.md

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Return Processing for CatalystUS.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions in this skill apply when:
- Email contains an order number in format `Ms#######`
- Email domain is `catalystcase.com`

---

## Key Rules (Locked)

- Return window: **30 days from delivery date** (not order date)
- Restocking fee: **5% of order value**; **15% if original packaging or components are missing**
- RMA number required; valid for **15 days** from issuance
- Tracking number required — returns cannot be processed without confirmed tracking
- Refund processing: **5–10 business days** after item is received and inspected
- Return portal: **https://catalystcase.com/pages/returns**
- Never approve or deny a return without verifying eligibility in Shopify first
- Never promise a refund amount before inspection is complete

---

## Skill Functions

### Function 1: Return Policy Explanation
**Trigger:** Customer asks about return rules without initiating a return
**Examples:** "What's your return policy?" / "How long do I have to return?" / "Are returns allowed?"
**Required Input:** Customer first name (optional)
**Task:** Generate a concise, professional email in American English that:
- Explains the return window (30 days from delivery)
- Outlines high-level eligibility criteria
- Reassures the customer
- Provides the self-service return portal URL: https://catalystcase.com/pages/returns
- Uses a warm but professional tone, solution-focused, confident language
- Avoids robotic or legalistic language

**Approved Language:**
> "Our return window is 30 days from the date of delivery. Items must be in original condition with all original packaging and components included."
> "To start a return, visit our self-service portal at https://catalystcase.com/pages/returns — you can log in with your order email and submit the request directly."

**Forbidden:**
- ❌ Any return window other than "30 days from delivery"
- ❌ "No questions asked" — eligibility criteria apply
- ❌ Promising a refund before the return is received and inspected

---

### Function 2: Return Initiation Instructions
**Trigger:** Customer explicitly requests a return, refund, or exchange
**Examples:** "I want to return this item" / "How do I get a refund?" / "Can I exchange for a different size?" / "Not satisfied, want to send this back"
**Required Input:**
- Customer first name
- Order number(s)
- Product name(s)
- Return reason
- Account login URL: https://catalystcase.com/pages/returns
- Return window: 30 days

**Task:** Write a 200–250 word structured instructional email in American English that:
- Greets the customer by name
- Directs the customer to the self-service return portal
- Explains how to log in and locate the order
- Lists portal capabilities (bulleted)
- Includes a return eligibility checklist
- Highlights the mandatory tracking requirement
- Sets expectations for approval and next steps
- Uses warm, professional, solution-focused style, avoiding overpromising

**Approved Language:**
> "To get started, visit our return portal at https://catalystcase.com/pages/returns. Log in with the email address on your order, find your order, and follow the prompts to request your return."
> "To avoid a restocking fee, please include all original packaging and components with your return."
> "A tracking number is required to process your return — please send it to us once you've shipped the item."

**Forbidden:**
- ❌ Any return window other than 30 days from delivery
- ❌ Accepting return requests via email without directing to the portal
- ❌ Skipping or minimizing the tracking number requirement
- ❌ Approving return eligibility before checking order status

---

### Function 3: Return Approved Notification
**Trigger:** Return has been approved or customer asks about next steps after approval
**Examples:** "Has my return been approved?" / "What do I do now?"
**Required Input:**
- Customer first name
- Order number(s)
- Product name(s)
- Product photos (for condition verification)

**Task:** Generate a professional email in American English that:
- Confirms the return is approved
- Instructs the customer to ship the item
- Emphasizes that a tracking number is required
- Explains where and how to send tracking details
- Maintains a warm, solution-focused, confident tone

**Approved Language:**
> "Your return has been approved. Please ship the item back to us and send us your tracking number — we need it to process your return once it arrives."
> "Once we receive and inspect your item, we'll process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Issuing or promising a refund before the item has been received
- ❌ Any refund timeline shorter than "5–10 business days after receipt"
- ❌ Confirming the refund amount before inspection is complete

---

### Function 4: Tracking Number Reminder
**Trigger:** Return is approved but tracking has not been provided, or customer asks about refund status
**Examples:** "When will I get my refund?" / No tracking received after approval
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Write a polite reminder email in American English that:
- Requests the tracking number
- Explains why tracking is required (faster processing, protection for the customer)
- Instructs the customer on how to submit tracking
- Maintains a warm, professional, solution-focused tone

**Approved Language:**
> "We haven't received a tracking number for your return yet. Please send it over so we can confirm your shipment and start the processing clock as soon as it arrives."
> "Tracking protects both of us — it confirms the return is on its way and lets us process your refund as quickly as possible."

**Forbidden:**
- ❌ Processing the refund before a tracking number is received
- ❌ Starting the 5–10 business day refund clock before confirmed tracking

---

### Function 5: Tracking Number Confirmation
**Trigger:** Customer provides tracking information
**Examples:** "Here's my tracking number" / "I shipped the return"
**Required Input:**
- Customer first name
- Order number(s)
- Tracking number
- Carrier (if provided)

**Task:** Generate a confirmation email in American English that:
- Acknowledges receipt of the tracking number
- Confirms the return is now in transit
- Explains inspection upon delivery
- Sets expectations for refund or exchange timeline after receipt
- Uses warm, confident, solution-focused style

**Approved Language:**
> "We've received your tracking number — thank you. Your return is on its way. Once it arrives, we'll inspect it and process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Stating refund will be issued immediately upon tracking confirmation (inspection required first)
- ❌ Any processing timeline faster than 5–10 business days

---

### Function 6: Return Received Notification
**Trigger:** Return is marked as delivered (system update or customer inquiry)
**Examples:** "My return shows delivered"
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Write a processing update email in American English that:
- Confirms the package has been received
- Explains inspection and review steps
- Provides a clear processing timeline
- Reassures the customer
- Maintains warm, professional, solution-focused tone

**Approved Language:**
> "We've received your return. Our team will inspect the item and process your refund or exchange within 5–10 business days. We'll email you as soon as it's complete."

**Forbidden:**
- ❌ Confirming a refund amount before inspection is complete
- ❌ Any timeline shorter than 5–10 business days
- ❌ "Your refund is on its way" before processing is confirmed

---

### Function 7: Refund Confirmation
**Trigger:** Refund has been successfully processed
**Required Input:**
- Customer first name
- Order number(s)
- Refund method

**Task:** Generate a refund confirmation email in American English that:
- Confirms the refund was issued
- States the payment method used
- Explains bank processing timelines (5–10 business days)
- Provides support contact options
- Uses warm, professional, confident tone

**Approved Language:**
> "Your refund has been issued to your [payment method]. Depending on your bank, it may take 5–10 business days to appear in your account."
> "If you have any questions, reply to this email or reach out at cs@catalystcase.com."

**Forbidden:**
- ❌ Stating a specific posting date (bank processing times vary)
- ❌ "Instant refund" or same-day language
- ❌ Referencing a refund amount that wasn't verified in Shopify

---

### Function 8: Exchange Shipment Notification
**Trigger:** Replacement item has shipped
**Required Input:**
- Customer first name
- Order number(s)
- New tracking number

**Task:** Write a shipment notification email in American English that:
- Confirms the exchange has shipped
- Provides tracking details
- Sets delivery expectations
- Maintains warm, professional, solution-focused style

**Approved Language:**
> "Your exchange has shipped. Your tracking number is [tracking number]. You can use it to follow your package at [carrier tracking link]."
> "Delivery estimates depend on your carrier and location — the tracking link will have the most up-to-date information."

**Forbidden:**
- ❌ Guaranteeing a specific delivery date
- ❌ Sending tracking before confirming shipment in Shopify

---

### Function 9: Return Denial / Exception Notification
**Trigger:** Return is not eligible or cannot be approved
**Examples:** Outside return window / Item condition issues / Missing requirements
**Required Input:**
- Customer first name
- Order number(s)
- Denial reason

**Task:** Generate a professional, empathetic email in American English that:
- Explains why the return was denied
- References the applicable policy
- Suggests alternatives if possible
- Provides support/escalation contact info: cs@catalystcase.com
- Maintains a solution-focused, warm, professional tone, avoiding overpromising

**Approved Language — Outside Return Window:**
> "Your order is outside our 30-day return window, so we're not able to process a return at this stage. If you're experiencing a product issue, it may be covered under our 12-month warranty — visit https://forms.fillout.com/t/8jPGm4Ck6Xus to submit a claim."

**Approved Language — Condition / Missing Components:**
> "We weren't able to approve this return because [reason — missing packaging, used condition, etc.]. Our policy requires items to be returned in original condition with all original packaging and components."

**Forbidden:**
- ❌ Approving a return outside the 30-day window without management approval
- ❌ Waiving the restocking fee without management approval
- ❌ "We can't help you" — always provide policy reason and an alternative path

---

## Policy Reference (Source of Truth)

See: CANONICAL_policy_returns.md for all policy details including:
- 30-day return window
- 5% restocking fee (15% if missing parts/packaging)
- RMA number requirement (valid 15 days)
- Photo submission requirement
- Refund processing: 5–10 business days
