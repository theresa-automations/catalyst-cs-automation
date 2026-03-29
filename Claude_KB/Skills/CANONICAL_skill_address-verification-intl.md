# CANONICAL: CS Skill — Address Verification & Order Holds (CatalystLifestyle.com — International)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.0
- **Review Schedule**: Quarterly
- **Store**: CatalystLifestyle.com (International)
- **Language Style**: International English

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-25 | 1.0 | Created as International counterpart to address-verification-us.md | KB governance alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`
- Order is on hold due to address issue or fraud flag

---

## Key Rules (Locked)

- Response deadline for customer: **7 days from notification date**
- If no response by deadline: **cancel the order**
- Carrier requirement: **English characters only** (DHL, HongKong Post, local carriers)
- Complete address required: street, city, postal code, country
- Fraud verification: **do not process order until verification is complete**
- Never make exceptions to carrier requirements

---

## Carrier Requirements Reference

| Carrier | Requirement |
|---------|-------------|
| DHL | English characters only, complete address, phone number recommended |
| HongKong Post | English characters preferred, complete address required, limited tracking |
| Local carriers | English characters required, country-specific format |

---

## Skill Functions

### Function 1: Invalid or Incomplete Address
**Trigger:** Address is missing required fields (street number, city, postal code, country)
**Required Input:** Order number (######), Customer name, Current address on file, Specific missing element
**Task:** Write a clear, professional email in International English that:
- States the specific issue with the address
- Lists exactly what information is needed
- Provides a clear format example
- States the 7-day response deadline and cancellation consequence
- Uses neutral, internationally accessible language — avoids idioms or regional phrasing

**Approved Language:**
> "We have encountered an issue with the shipping address on your order and need your assistance before we can proceed."
> "Please reply with your corrected address within 7 days. If we do not receive a response by [date], we will need to cancel your order to avoid a delivery failure."
> "Once we have the correct address, we will process your order promptly."

**Forbidden:**
- ❌ "Your address is wrong" (accusatory)
- ❌ Processing with an incomplete address
- ❌ Promising delivery within a specific timeframe before address is confirmed
- ❌ Using US-specific address format as the example (use international format)

---

### Function 2: Non-English Characters in Address
**Trigger:** Address contains characters that carrier systems cannot process
**Required Input:** Order number (######), Customer name, Current address on file
**Task:** Write a professional, empathetic email in International English that:
- Explains that shipping carriers require English characters
- Clarifies this is a carrier requirement, not a company preference
- Requests an English-language version of the address
- States the 7-day deadline and cancellation consequence
- Acknowledges the inconvenience for international customers

**Approved Language:**
> "Our shipping carriers require all addresses to be written in English characters. This is a carrier requirement that applies internationally and is not something we are able to override."
> "Could you please provide your address using English characters? Here is the format we need: [example]"
> "We understand this may require an extra step, and we appreciate your patience."
> "Please reply within 7 days. If we do not receive the corrected address by [date], we will need to cancel your order."

**Forbidden:**
- ❌ Implying the customer made an error
- ❌ Making exceptions to the English-only requirement
- ❌ Using informal or region-specific phrasing

---

### Function 3: Address Too Long or Incomplete for Carrier Systems
**Trigger:** Address exceeds carrier character limits or lacks required fields for international routing
**Required Input:** Order number (######), Customer name, Specific issue with the address
**Task:** Write a clear email in International English that:
- Explains the specific formatting requirement
- Identifies which part needs to be corrected
- Provides guidance on acceptable abbreviations if relevant
- States the 7-day deadline

**Approved Language:**
> "Our carrier system requires that each address line be within a specific character limit. The [section] of your address needs to be shortened or reformatted."
> "Standard abbreviations are acceptable — for example, 'Street' as 'St', 'Apartment' as 'Apt'."

**Forbidden:**
- ❌ Shipping without resolving the issue
- ❌ Modifying the address without customer confirmation

---

### Function 4: Fraud Risk Verification Request
**Trigger:** Order flagged for additional verification (billing/shipping mismatch, high-value new customer, payment flag)
**Required Input:** Order number (######), Customer name
**Task:** Write a professional, reassuring email in International English that:
- Frames this as a standard security check
- Lists required documents (proof of address document, payment confirmation screenshot, phone number)
- States the 7-day deadline and cancellation consequence
- Reassures the customer that information is secure and used only for this verification
- Does NOT mention fraud explicitly

**Approved Language:**
> "As part of our standard order security process, we need to verify a few details before we can ship your order. This is a routine step that helps us protect our customers."
> "Please provide the following within 7 days: [list]. Once we have verified your information, we will process your order immediately."
> "Your information is kept completely secure and will be used solely for verification purposes."

**Forbidden:**
- ❌ "Your order has been flagged for fraud"
- ❌ Requesting passwords, full account numbers, or unnecessary personal data
- ❌ Processing the order before verification is complete

---

### Function 5: No-Response Deadline Reminder
**Trigger:** 3–4 days have passed since initial request with no response
**Required Input:** Order number (######), Customer name, Original request date, Final deadline
**Task:** Write a brief, professional follow-up email in International English that:
- References the original request
- States the final deadline clearly
- States the cancellation consequence plainly
- Repeats the required action concisely

**Approved Language:**
> "We sent you a request on [date] regarding your order #[ORDER_NUMBER] but have not yet received a response."
> "Your final deadline to respond is [date]. If we do not hear from you by this date, we will cancel your order."
> "Please reply to this email with your [corrected address / verification documents] to keep your order active."

**Forbidden:**
- ❌ Extending the deadline without management approval
- ❌ Cancelling without this reminder being sent first
- ❌ Threatening or aggressive language

---

## Key Difference from US Skill
- **Language:** International English (neutral, no US idioms, metric-compatible phrasing)
- **Order number format:** #67702 style
- **Carriers:** DHL, HongKong Post, local international carriers
- **Support email:** info@catalystlifestyle.com
