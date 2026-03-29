# CANONICAL: CS Skill — Order Shipping & Delivery (CatalystCase.com — US)

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
| 2026-03-24 | 1.0 | Initial version | Converted from Order Shipping & Delivery for CatalystUS.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`
- Topic relates to order shipping or delivery

---

## Known Shipping Methods (US)
- USPS Ground Advantage
- Standard (3 business days)
- [Verify full list from Shopify shipping settings]

---

## Key Rules (Locked)

- **Never state a specific delivery date as guaranteed** — carrier ETAs are estimates only
- Tracking scans may take **24–48 hours** to appear after a shipping label is created
- A package is not confirmed lost until **15+ business days** have passed without movement AND a carrier investigation has been opened — do not confirm "lost" without this
- Never promise reshipping or a refund for a delayed/missing package without internal approval
- Always frame delivery timelines as estimates: "expected to arrive" not "will arrive"
- If tracking shows "delivered" but customer says they didn't receive it: escalate — do not promise reshipment in the same message

---

## Skill Functions

### Skill 1: Order Fulfillment Status Check
**Trigger:** Customer asks if order has shipped or is still processing
**Examples:** "Has my order shipped yet?" / "Is my order still processing?"
**Required Input:** Order number (Ms######) or customer email address
**Task:** Retrieve fulfillment status from Shopify and respond by:
- Identifying whether order is not fulfilled, partially fulfilled, or fully fulfilled
- Explaining the current stage (processing vs. shipped)
- Providing the next expected step (e.g., shipment confirmation email)
- Reassuring the customer without referencing tracking if unavailable
**Style:** American English — professional, calm, informative, clear expectations without overpromising, warm and reassuring

**Approved Language:**
> "Your order is currently processing. Once it ships, you'll receive a shipment confirmation email with your tracking number."
> "Your order has shipped. You can track it with the tracking number in your shipment confirmation email."

**Forbidden:**
- ❌ Stating a specific ship date if the order hasn't shipped yet
- ❌ Promising the order will ship by a specific date

---

### Skill 2: Tracking Information Request
**Trigger:** Customer explicitly requests tracking information
**Examples:** "Can you send me my tracking number?" / "Where can I track my order?"
**Required Input:** Order number or customer email address
**Task:** Retrieve tracking data from Shopify and:
- Identify the tracking number(s)
- Identify the carrier
- Generate and provide a clickable tracking link
- Confirm shipment is in transit
**Style:** American English — clear, direct, helpful, professional with supportive tone, solution-focused

**Approved Language:**
> "Your tracking number is [tracking number] with [carrier]. You can follow your package here: [tracking link]."
> "Tracking may take up to 24–48 hours to show movement after the label is created."

**Forbidden:**
- ❌ Providing tracking before confirming shipment is processed in Shopify
- ❌ Stating tracking is "fully up to date" without verifying carrier scan activity

---

### Skill 3: Package Location / Shipment Status
**Trigger:** Customer asks about package location or progress
**Examples:** "Where is my package?" / "What's the status of my shipment?"
**Required Input:** Tracking number or order number (to retrieve tracking)
**Task:** Query the carrier tracking system and:
- Retrieve latest scan status
- Identify most recent location
- Provide estimated delivery date (if available)
- Reassure customer that shipment is progressing normally
**Style:** American English — reassuring and informative, confident but factual, avoids speculation

**Approved Language:**
> "According to the carrier, your package was last scanned at [location] on [date]. It is expected to arrive by [carrier ETA] — this is an estimate and may shift slightly."
> "There haven't been any new scans since [date], which can happen during transit. The carrier ETA is still showing [date]."

**Forbidden:**
- ❌ Stating a delivery date as confirmed or guaranteed
- ❌ Speculating on why scans have stopped ("probably stuck at the warehouse")
- ❌ Declaring a package lost based on a scan gap alone

---

### Skill 4: Delivery Date Estimate
**Trigger:** Customer asks when their order will arrive
**Examples:** "When will my order arrive?" / "What's the delivery date?"
**Required Input:** Order number or tracking number
**Task:** Determine best delivery estimate by:
- Using carrier ETA when available
- Falling back to shipping method service-level expectations
- Adjusting for weekends, holidays, and business days
- Clearly framing date as an estimate, not a guarantee
**Style:** American English — clear and confidence-calibrated, transparent and realistic, professional and reassuring

**Approved Language:**
> "Based on the carrier's current estimate, your order is expected to arrive by [date]. This is an estimate — actual delivery may vary by a day or two depending on carrier and local conditions."
> "Your order shipped via [method], which typically delivers within [X] business days. Based on the ship date, you can expect it around [date range]."

**Forbidden:**
- ❌ "Your order will arrive on [date]" (guaranteed framing)
- ❌ Providing a delivery estimate without noting it is an estimate
- ❌ Using carrier SLA times as guarantees

---

### Skill 5: Shipping Methods Information
**Trigger:** Customer asks about shipping methods or delivery speed
**Examples:** "What shipping options do you have?" / "Do you offer expedited shipping?"
**Required Input:** Available shipping methods (USPS Ground Advantage, Standard 3 business days, etc.)
**Task:** Provide informational response that:
- Lists available shipping methods
- Explains delivery speed ranges
- Mentions carriers used
- Clarifies whether options apply pre-purchase or post-purchase
**Style:** American English — professional and informative, clear, concise, neutral, premium-brand appropriate

**Approved Language:**
> "We currently offer [list methods]. Delivery timelines are estimates and may vary based on your location and carrier conditions."

**Forbidden:**
- ❌ Guaranteeing delivery within a specific number of days
- ❌ Listing shipping methods without noting they are subject to change — verify from Shopify settings before quoting

---

### Skill 6: Delivery Confirmation
**Trigger:** Customer asks if package was delivered
**Examples:** "Has my order been delivered?" / "Did my package arrive?"
**Required Input:** Tracking number or order number
**Task:** Confirm delivery via carrier data and:
- Provide delivery date and time
- Identify delivery location if available (e.g., front door, mailbox)
- Explain next steps if package cannot be located
**Style:** American English — professional and reassuring, clear and supportive, solution-oriented

**Approved Language:**
> "According to the carrier, your package was delivered on [date] at [time] to [location if available]."
> "If you're not able to locate your package, we'd recommend checking with neighbors and any safe-drop locations before we open a carrier investigation."

**Forbidden:**
- ❌ Promising a reshipment before a carrier investigation is completed
- ❌ "The carrier says it was delivered so there's nothing we can do" — always offer next steps

---

### Skill 7: Delivery Delay Investigation
**Trigger:** Customer reports or suspects delivery delay
**Examples:** "My package is delayed" / "Why hasn't my order arrived?"
**Required Input:** Tracking number or order number
**Task:** Investigate the delay and:
- Identify likely cause (weather, carrier backlog, address issue, etc.)
- Recalculate or update delivery estimate
- Explain whether escalation or monitoring is required
- Provide clear next steps and reassurance
**Style:** American English — transparent and calm, empathetic but policy-aware, avoids assigning blame

**Approved Language:**
> "Your package is showing as in transit — the carrier has it, but there's been a delay in the expected delivery window. The current estimate is [new date], but this may update as the carrier scans the package."
> "If there's been no movement for 10+ business days, we can open a carrier investigation. Let us know and we'll get that started."

**Forbidden:**
- ❌ Promising a replacement or refund for a delay before carrier investigation is complete
- ❌ Confirming a package is lost before 15+ business days of no movement AND a carrier investigation
- ❌ Assigning blame to the carrier in the response text

---

### Skill 8: Tracking Not Working
**Trigger:** Customer reports tracking doesn't work or shows no information
**Examples:** "My tracking number doesn't work" / "The link shows no information"
**Required Input:** Order number or tracking number
**Task:** Validate tracking by:
- Checking fulfillment and carrier assignment
- Determining if shipment is too recent to show scans
- Identifying incorrect or missing tracking data
- Explaining when next update should appear
- Escalating internally if required
**Style:** American English — clear and reassuring, professional and solution-focused, patient and non-defensive

**Approved Language:**
> "It can take 24–48 hours after the shipping label is created for tracking to show activity. If your order shipped recently, this is likely the reason."
> "If it's been more than 48 hours and tracking still shows no movement, let us know and we'll look into it on our end."

**Forbidden:**
- ❌ Telling a customer their tracking number is wrong without verifying in Shopify first
- ❌ Promising a new tracking number without confirming the issue is on the carrier side
