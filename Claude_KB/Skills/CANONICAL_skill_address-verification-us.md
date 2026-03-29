# CANONICAL: CS Skill — Address Verification & Order Holds (CatalystCase.com — US)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.0
- **Review Schedule**: Quarterly
- **Store**: CatalystCase.com (US)
- **Language Style**: American English

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-25 | 1.0 | Converted from Address Verification & Order Holds Guide.md + moved to Skills/ | KB governance alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`
- Order is on hold due to address issue or fraud flag

---

## Key Rules (Locked)

- Response deadline for customer: **7 days from notification date**
- If no response by deadline: **cancel the order**
- Carrier requirement: **English characters only** (FedEx, USPS, DHL)
- FedEx: maximum **35 characters per address line**
- Fraud verification: **do not process order until verification is complete**
- Never make exceptions to carrier requirements

---

## Carrier Requirements Reference

| Carrier | Requirement |
|---------|-------------|
| FedEx | English characters only, max 35 chars per line |
| USPS | English characters only, standard US address format |
| DHL | English characters only, complete address, phone recommended |

---

## Skill Functions

### Function 1: Invalid or Incomplete Address
**Trigger:** Address is missing apartment/unit number, street number, city, state, or postal code
**Examples:** "Your address appears incomplete" / missing apt number / invalid postal code
**Required Input:** Order number (Ms######), Customer name, Current address on file, Specific missing element
**Task:** Write a clear, professional email in American English that:
- States the specific issue with the address (missing field or incomplete format)
- Lists exactly what information is needed
- Provides an example of the correct format
- States the 7-day response deadline and cancellation consequence
- Maintains a helpful, non-accusatory tone

**Approved Language:**
> "We've run into an issue with the shipping address on your order and need your help to get it sorted before we ship."
> "Please reply with your corrected address within 7 days. If we don't hear back by [date], we'll need to cancel your order to avoid a delivery failure."
> "Once we have the correct address, we'll process your order immediately."

**Forbidden:**
- ❌ "Your address is wrong" (accusatory — say "we've run into an issue")
- ❌ Cancelling without first sending this notification
- ❌ Processing the order with an incomplete address
- ❌ Promising delivery within a specific timeframe before the address is confirmed

---

### Function 2: Non-English Characters in Address
**Trigger:** Address contains characters that carrier systems cannot process (e.g., accented, Chinese, Arabic, Korean characters)
**Examples:** International customer with native-language address / Address field contains special characters
**Required Input:** Order number (Ms######), Customer name, Current address on file
**Task:** Write a professional, empathetic email in American English that:
- Explains that shipping carriers require English characters
- Clarifies this is a carrier requirement, not a policy preference
- Requests an English-language version of the address
- States the 7-day deadline and cancellation consequence
- Provides a clear format example

**Approved Language:**
> "Our shipping carriers (FedEx, USPS, DHL) require all addresses to be written in English characters. This is a carrier requirement that we're not able to override."
> "Could you please provide your address using English characters only? Here's the format we need: [example]"
> "Please reply within 7 days. If we don't receive the corrected address by [date], we'll need to cancel your order."

**Forbidden:**
- ❌ Implying the customer made an error — frame it as a carrier limitation
- ❌ "Unfortunately we cannot ship to you" — the goal is to resolve, not decline
- ❌ Making exceptions to the English-only requirement

---

### Function 3: Address Too Long for Carrier Systems
**Trigger:** Address exceeds carrier character limits (FedEx: 35 characters per line)
**Required Input:** Order number (Ms######), Customer name, Specific line that exceeds limit
**Task:** Write a clear email in American English that:
- Explains the character limit requirement
- Identifies which part of the address needs to be shortened
- Suggests acceptable abbreviations (St. for Street, Apt for Apartment, etc.)
- States the 7-day deadline

**Approved Language:**
> "Our carrier system has a 35-character limit per address line. The [line] in your address is [X] characters, which is just over the limit."
> "Standard abbreviations are fine — for example, 'Street' can be 'St.', 'Apartment' can be 'Apt'."

**Forbidden:**
- ❌ Promising to ship without resolving the character limit first
- ❌ Manually truncating the address without customer confirmation

---

### Function 4: Fraud Risk Verification Request
**Trigger:** Order flagged as medium or high risk by fraud detection (e.g., PayPal MID/HIGH RISK flag, billing/shipping mismatch, high-value new customer)
**Required Input:** Order number (Ms######), Customer name
**Task:** Write a professional, reassuring email in American English that:
- Explains this is a standard security check
- Lists exactly what documents are needed (utility bill or bank statement, PayPal screenshot, phone number)
- States the 7-day deadline and cancellation consequence
- Reassures the customer that their information is secure and used only for verification
- Does NOT mention fraud explicitly — frame as "standard security verification"

**Approved Language:**
> "As part of our standard order security process, we need to verify a few details before we can ship your order. This is routine and helps us protect all of our customers."
> "Please provide the following within 7 days: [list]. Once verified, we'll process your order immediately."
> "Your information is kept completely secure and will only be used for this verification."

**Forbidden:**
- ❌ "Your order has been flagged for fraud" (accusatory and damaging)
- ❌ Requesting sensitive information beyond what is listed (no passwords, no full account numbers)
- ❌ Processing the order before verification is complete
- ❌ Threatening language about fraud consequences

---

### Function 5: No-Response Deadline Reminder
**Trigger:** 3–4 days have passed since the initial verification request with no customer response
**Required Input:** Order number (Ms######), Customer name, Original request date, Final deadline
**Task:** Write a brief, urgent follow-up email in American English that:
- References the original request
- States the final deadline clearly
- States the cancellation consequence plainly
- Provides the corrected address format or document list again (brief)
- Keeps tone firm but professional — not threatening

**Approved Language:**
> "We sent you a request on [date] regarding your order #[ORDER_NUMBER] but haven't heard back yet."
> "Your final deadline to respond is [date]. After this date, we will cancel your order."
> "Reply to this email with your [corrected address / verification documents] to keep your order active."

**Forbidden:**
- ❌ Extending the deadline without management approval
- ❌ Cancelling without first sending this reminder
- ❌ Threatening language

---

## Policy Reference

- Deadline for customer response: 7 days from initial notification
- After deadline with no response: cancel order, log in Shopify order notes
- Carrier English requirement: non-negotiable, applies to FedEx, USPS, DHL
- Fraud verification: do not ship until complete
- Support contact: cs@catalystcase.com
