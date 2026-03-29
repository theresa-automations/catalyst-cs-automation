# CANONICAL: CS Skill — Order Shipping & Delivery (CatalystLifestyle.com — International)

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
| 2026-03-24 | 1.0 | Initial version | Converted from Order Shipping & Delivery for Catalystlifestyle.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`

---

## Key Rules (Locked)

- **Never state a specific delivery date as guaranteed** — carrier ETAs are estimates only
- Tracking scans may take **24–48 hours** to appear after a shipping label is created
- International shipments may take longer to show tracking updates due to customs clearance
- A package is not confirmed lost until **15+ business days** have passed without movement AND a carrier investigation has been opened
- Never promise reshipping or a refund for a delayed/missing package without internal approval
- Always frame delivery timelines as estimates: "expected to arrive" not "will arrive"
- If tracking shows "delivered" but customer says they didn't receive it: escalate — do not promise reshipment in the same message
- Support contact: **info@catalystlifestyle.com**

---

## Skill Functions

### Skill 1: Order Fulfillment Status Check
**Trigger:** Customer asks if order shipped or is processing
**Examples:** "Has my order shipped yet?" / "Is my order still processing?"
**Required Input:** Order number or customer email
**Task:** Retrieve fulfillment status from Shopify — identify fulfillment state, explain current stage, provide next expected step, reassure customer without referencing unavailable tracking.
**Style:** International English — professional, calm, informative, no overpromising, warm and reassuring

**Approved Language:**
> "Your order is currently processing. Once it ships, you will receive a shipment confirmation email with your tracking number."
> "Your order has shipped. You can track it using the tracking number in your shipment confirmation email."

**Forbidden:**
- ❌ Stating a specific ship date if the order has not shipped yet
- ❌ Promising the order will ship by a specific date

---

### Skill 2: Tracking Information Request
**Trigger:** Customer requests tracking
**Required Input:** Order number or customer email
**Task:** Retrieve tracking from Shopify — identify tracking number(s) and carrier, provide clickable tracking link, confirm in transit.
**Style:** International English — clear, direct, helpful, professional and supportive

**Approved Language:**
> "Your tracking number is [tracking number] with [carrier]. You can follow your package here: [tracking link]."
> "Please note that tracking may take 24–48 hours to show movement after the label is created, and international shipments may experience delays at customs."

**Forbidden:**
- ❌ Providing tracking before confirming shipment is processed
- ❌ Stating tracking is "fully up to date" without verifying carrier scan activity

---

### Skill 3: Package Location / Status
**Trigger:** Customer asks about package location or progress
**Required Input:** Tracking number or order number
**Task:** Query carrier tracking — retrieve latest scan status, most recent location, estimated delivery date, reassure customer.
**Style:** International English — reassuring and informative, confident but factual, avoids speculation

**Approved Language:**
> "According to the carrier, your package was last scanned at [location] on [date]. It is expected to arrive by [carrier ETA] — this is an estimate and may shift."
> "International shipments sometimes show a gap in tracking scans during transit or customs processing. The carrier ETA is still showing [date]."

**Forbidden:**
- ❌ Stating a delivery date as confirmed or guaranteed
- ❌ Speculating on why scans have stopped
- ❌ Declaring a package lost based on a scan gap alone

---

### Skill 4: Delivery Date Estimate
**Trigger:** Customer asks when order will arrive
**Required Input:** Order number or tracking number
**Task:** Determine delivery estimate — use carrier ETA, fall back to service-level expectations, adjust for local holidays/weekends, frame as estimate not guarantee.
**Style:** International English — clear and confidence-calibrated, transparent, professional and reassuring

**Approved Language:**
> "Based on the carrier's current estimate, your order is expected to arrive by [date]. This is an estimate — international delivery times can vary depending on customs and local carrier conditions."
> "Your order shipped via [method]. Estimated delivery to your region is typically [X–Y] business days from shipment, though this can vary."

**Forbidden:**
- ❌ "Your order will arrive on [date]" (guaranteed framing)
- ❌ Providing a delivery estimate without noting it is an estimate
- ❌ Using carrier SLA times as guarantees for international shipments

---

### Skill 5: Shipping Methods Information
**Trigger:** Customer asks about shipping options or speed
**Required Input:** Available international shipping methods [verify from Shopify settings]
**Task:** List available methods, explain delivery speed ranges, mention carriers, clarify pre/post-purchase applicability.
**Style:** International English — professional and informative, clear, concise, neutral

**Approved Language:**
> "We currently ship internationally via [carriers]. Delivery timelines are estimates and vary by destination, customs processing, and local carrier conditions."

**Forbidden:**
- ❌ Guaranteeing delivery within a specific number of days for international orders
- ❌ Listing shipping methods without verifying from Shopify settings — international options may differ by region

---

### Skill 6: Delivery Confirmation
**Trigger:** Customer asks if package was delivered
**Required Input:** Tracking number or order number
**Task:** Confirm delivery — provide date and time, delivery location if available, explain next steps if not located.
**Style:** International English — professional and reassuring, clear, solution-oriented

**Approved Language:**
> "According to the carrier, your package was delivered on [date] at [time] to [location if available]."
> "If you are not able to locate your package, we recommend checking with household members and any safe-drop locations. If it still cannot be found, please contact us and we will open a carrier investigation."

**Forbidden:**
- ❌ Promising a reshipment before a carrier investigation is completed
- ❌ "The carrier says it was delivered so there is nothing we can do" — always offer next steps

---

### Skill 7: Delivery Delay Investigation
**Trigger:** Customer reports or suspects delay
**Required Input:** Tracking number or order number
**Task:** Investigate delay — identify likely cause, recalculate estimate, explain next steps, provide reassurance.
**Style:** International English — transparent and calm, empathetic but policy-aware, avoids blame

**Approved Language:**
> "Your package is showing as in transit. There has been a delay in the expected delivery window, which can happen with international shipments due to customs or carrier backlogs. The current estimate is [date]."
> "If there has been no tracking movement for 10+ business days, we can open a carrier investigation. Please let us know and we will arrange that."

**Forbidden:**
- ❌ Promising a replacement or refund for a delay before a carrier investigation is complete
- ❌ Confirming a package is lost before 15+ business days of no movement AND a carrier investigation
- ❌ Assigning blame to the carrier in the response

---

### Skill 8: Tracking Not Working
**Trigger:** Customer reports tracking not working
**Required Input:** Order number or tracking number
**Task:** Validate tracking — check fulfillment status, determine if too recent, identify data issues, explain when next update appears, escalate if needed.
**Style:** International English — clear and reassuring, professional, patient

**Approved Language:**
> "It can take 24–48 hours after the label is created for tracking to show activity. For international orders, there may also be a gap in scans while the package clears customs."
> "If it has been more than 48 hours and tracking is still showing no information, please contact us at info@catalystlifestyle.com and we will investigate."

**Forbidden:**
- ❌ Telling a customer their tracking number is wrong without verifying first
- ❌ Promising a new tracking number without confirming the issue is on the carrier side

---

## Key Difference from US Skill
- **Language:** International English
- **Order number format:** #67702 style
- **Carriers:** International carriers (Hongkong Post, DHL, etc.) — verify current carrier list from Shopify settings
- **Support email:** info@catalystlifestyle.com
