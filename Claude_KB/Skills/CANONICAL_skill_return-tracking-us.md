# CANONICAL: CS Skill — Return Tracking & Post-Approval (CatalystCase.com — US)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystCase.com (US)
- **Language Style**: American English

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Return Tracking & Post-Approval for CatalystUS.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`

---

## Key Rules (Locked)

- Tracking number required — return processing cannot begin without confirmed tracking
- Refund processing: **5–10 business days** after item is received and inspected
- Exchange ships after return is received and inspected — not before
- Never confirm a refund amount before inspection is complete
- Refund issued to original payment method only

---

## Skill Functions

### Function 1: Tracking Number Request (Missing Tracking)
**Trigger:** Return approved but customer has not provided tracking number, or customer inquires about refund status
**Examples:** "When will I get my refund?" / No tracking received after approval
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Generate a polite reminder email in American English that:
- Requests the tracking number
- Explains why tracking is required (faster processing and customer protection)
- Instructs customer on how to submit tracking information
- Maintains warm, professional, solution-focused tone, avoiding blame or robotic phrasing

**Approved Language:**
> "We haven't received a tracking number for your return yet. Please send it over so we can confirm your item is on its way and start processing as soon as it arrives."
> "Tracking protects both of us and lets us process your return as quickly as possible."

**Forbidden:**
- ❌ Processing or promising a refund before tracking is received
- ❌ Starting the 5–10 business day refund clock before confirmed tracking

---

### Function 2: Tracking Number Received
**Trigger:** Customer provides tracking information
**Examples:** "Here's my tracking number" / "I shipped the return"
**Required Input:**
- Customer first name
- Order number(s)
- Tracking number
- Carrier (if provided)

**Task:** Generate a confirmation email in American English that:
- Acknowledges receipt of tracking number
- Confirms return is now in transit
- Explains inspection upon delivery
- Sets expectations for refund or exchange timeline after receipt
- Uses warm, confident, solution-focused style, reinforcing trust and clarity

**Approved Language:**
> "We've received your tracking number — thank you. Your return is on its way. Once it arrives, we'll inspect it and process your refund or exchange within 5–10 business days."

**Forbidden:**
- ❌ Stating refund will be issued immediately upon tracking receipt
- ❌ Any refund timeline shorter than 5–10 business days after receipt

---

### Function 3: Return Delivered — Processing Update
**Trigger:** Return marked as delivered (via system update or customer inquiry)
**Examples:** "My return shows delivered"
**Required Input:**
- Customer first name
- Order number(s)

**Task:** Write a processing update email in American English that:
- Confirms package has been received
- Explains inspection and review steps
- Provides clear processing timeline for refund or exchange
- Reassures the customer
- Maintains warm, professional, solution-focused tone

**Approved Language:**
> "We've received your return. Our team will inspect the item and process your refund or exchange within 5–10 business days. We'll email you as soon as it's complete."

**Forbidden:**
- ❌ Confirming a refund amount before inspection is complete
- ❌ Any timeline shorter than 5–10 business days
- ❌ "Your refund has been processed" before inspection is done

---

### Function 4: Refund Processed
**Trigger:** Refund successfully processed
**Required Input:**
- Customer first name
- Order number(s)
- Refund method

**Task:** Generate a refund confirmation email in American English that:
- Confirms refund was issued
- States payment method used
- Explains bank processing timelines
- Provides support contact options
- Maintains warm, professional, confident tone

**Approved Language:**
> "Your refund has been issued to your [payment method]. Depending on your bank, it may take 5–10 business days to appear in your account."
> "If you have any questions, reply to this email or reach out at cs@catalystcase.com."

**Forbidden:**
- ❌ Stating a specific posting date (bank processing times vary)
- ❌ "Instant refund" or same-day language

---

### Function 5: Exchange Shipped
**Trigger:** Replacement item has shipped
**Required Input:**
- Customer first name
- Order number(s)
- New tracking number

**Task:** Write a shipment notification email in American English that:
- Confirms exchange has shipped
- Provides tracking details
- Sets delivery expectations
- Maintains warm, professional, solution-focused style

**Approved Language:**
> "Your exchange has shipped. Your tracking number is [tracking number]. You can use it to follow your package at [carrier tracking link]."

**Forbidden:**
- ❌ Guaranteeing a specific delivery date
- ❌ Sending tracking before confirming shipment in Shopify
- ❌ Shipping exchange before return is received and inspected

---

### Function 6: Return Denied / Exception Handling
**Trigger:** Return not eligible or cannot be approved
**Examples:** Outside return window / Item condition issues / Missing requirements
**Required Input:**
- Customer first name
- Order number(s)
- Denial reason

**Task:** Generate a professional, empathetic email in American English that:
- Explains why return was denied
- References the applicable return policy
- Suggests alternatives if possible (warranty claim if within 12 months, etc.)
- Provides support/escalation contact information
- Uses solution-focused, warm, professional tone, avoiding overpromising or harsh language

**Approved Language — Outside Return Window:**
> "Your order is outside our 30-day return window, so we're not able to process a return. If you're having a product issue, it may be covered under our 12-month warranty — visit https://forms.fillout.com/t/8jPGm4Ck6Xus to file a claim."

**Approved Language — Condition / Missing Components:**
> "We weren't able to approve this return because [reason]. Our return policy requires items in original condition with all original packaging and components included."

**Forbidden:**
- ❌ Approving a return outside the 30-day window without management approval
- ❌ Waiving fees or conditions without management approval
- ❌ "We can't help you" — always provide an alternative path
