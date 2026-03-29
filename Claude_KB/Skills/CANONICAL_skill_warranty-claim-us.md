# CANONICAL: CS Skill — Warranty Claims (CatalystCase.com — US)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystCase.com (US)
- **Language Style**: American English
- **Related Policy**: CANONICAL_policy_warranty.md

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Warranty Claim for CatalystUS.xlsx |
| 2026-03-25 | 1.1 | Added locked phrases + merged templates from Warranty Claims Guide.md | Temperature Zero alignment + KB governance |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`

---

## Warranty Form URL
https://forms.fillout.com/t/8jPGm4Ck6Xus

---

## Key Rules (Locked)

- Warranty period: **12 months from purchase date**
- Replacement warranty: **3 months from replacement shipment date** (never 12 months)
- Agent does **not** approve or deny claims — human reviewer does
- Do not process claims without photos
- Out-of-warranty (<2 years old): offer goodwill discount — do not approve full claim
- Out-of-warranty (>2 years old): decline and offer discount on new purchase
- Never promise shipping is free for replacements without verifying current policy

---

## Skill Functions

### Function 1: Warranty Policy Explanation
**Trigger:** Customer asks about warranty coverage without filing a claim
**Examples:** "Is my device still under warranty?" / "What does the warranty cover?" / "How long is the warranty?"
**Required Input:**
- Customer first name (optional)
- Warranty form URL: https://forms.fillout.com/t/8jPGm4Ck6Xus

**Task:** Generate a concise, professional email in American English that:
- States the warranty period (12 months from purchase)
- Explains what is covered (manufacturing defects only)
- Provides the warranty form URL for reference
- Uses warm but professional tone, solution-focused, confident language
- Avoids overpromising or robotic phrasing

**Approved Language:**
> "All Catalyst products come with a 12-month limited warranty from the purchase date. This covers defects in materials and workmanship — manufacturing issues, not accidental damage or normal wear."
> "To file a warranty claim, visit: https://forms.fillout.com/t/8jPGm4Ck6Xus"

**Forbidden:**
- ❌ Any warranty period other than "12 months from purchase date"
- ❌ "Your product may be covered" without reviewing the claim
- ❌ Stating replacement warranty as 12 months — it is 3 months from replacement shipment

---

### Function 2: Warranty Claim Initiation
**Trigger:** Customer reports a product defect within the warranty period
**Examples:** "My device stopped working" / "Under warranty but broken" / "Manufacturer defect" / "Product failed within 1 year"
**Required Input:**
- Customer first name
- Product name/type
- Purchase date
- Order number
- Warranty form URL: https://forms.fillout.com/t/8jPGm4Ck6Xus

**Task:** Write a 150–200 word professional email in American English that:
- Greets the customer by name
- Acknowledges the issue and expresses empathy (warm but not over-casual)
- Explains warranty coverage clearly (confident and reassuring)
- Provides next steps including the warranty form link
- Lists required documentation: photos (front, back, top, bottom, close-up of defect), order number, purchase date
- Closes with a supportive, solution-focused statement

**Approved Language:**
> "I'm sorry to hear you're having trouble with your [product] — that's not the experience we want you to have."
> "To start your warranty claim, please complete our form at https://forms.fillout.com/t/8jPGm4Ck6Xus. You'll need clear photos of the defect (front, back, top, bottom, plus a close-up), your order number, and your purchase date."
> "Once we receive your submission, our team will review it within 24–48 hours and follow up with next steps."

**Forbidden:**
- ❌ "This is definitely covered" — claim has not been reviewed yet
- ❌ "We'll send a replacement right away" — approval is required first
- ❌ Collecting the claim information manually without directing to the form

---

### Function 3: Warranty Claim Submitted Confirmation
**Trigger:** Customer has submitted the warranty form
**Examples:** "I submitted the warranty form" / "Form filled out"
**Required Input:**
- Customer first name
- Customer email
- Order number

**Task:** Generate a confirmation email in American English that:
- Thanks the customer for submitting the claim
- Confirms receipt of all required information
- States review timeline (24–48 hours for standard; 5–7 business days for complex)
- Reassures the customer that the claim is being processed

**Approved Language:**
> "We've received your warranty claim submission. Our team will review it within 24–48 hours and follow up with next steps."
> "If we need any additional information, we'll reach out to you directly."

**Forbidden:**
- ❌ Any resolution promise before review is complete
- ❌ "Your claim will be approved" — decision has not been made

---

### Function 4: Warranty Claim Status Update
**Trigger:** Claim is under review or customer asks about status
**Examples:** "What's the status of my warranty claim?" / "Has my warranty request been approved?"
**Required Input:**
- Customer first name
- Customer email
- Order number

**Task:** Generate a professional, reassuring status update in American English that:
- Confirms the claim is being reviewed
- Sets timeline expectations (5–7 business days for most claims)
- Maintains warm, confident, solution-focused tone

**Approved Language:**
> "Your claim is currently under review. We typically complete reviews within 5–7 business days and will contact you as soon as a decision is made."

**Forbidden:**
- ❌ "Your claim will be approved" (decision not yet made)
- ❌ Any specific resolution before review is complete

---

### Function 5: Warranty Claim Approval Notification
**Trigger:** Claim approved for replacement
**Examples:** "My warranty claim was approved" / "What do I do now?"
**Required Input:**
- Customer first name
- Product name
- Order number

**Task:** Generate an email in American English that:
- Confirms claim approval
- Presents resolution options: Replacement (with 3-month warranty) / Refund to original payment / Store credit
- Explains next steps clearly
- Notes that a shipping fee may apply for the replacement

**Approved Language:**
> "Your warranty claim has been approved. You can choose from the following options:"
> "**Replacement:** We'll send you a new [product]. Your replacement comes with a 3-month limited warranty from the shipment date."
> "**Refund:** We'll refund the full purchase price to your original payment method within 3–5 business days."
> "**Store credit:** We'll issue store credit for a future purchase."
> "Please reply and let us know which option you prefer."

**Forbidden:**
- ❌ "Your replacement comes with a full warranty" — replacement warranty is 3 months only
- ❌ "Free replacement" without confirming current shipping fee policy
- ❌ Shipping the replacement before the customer chooses their option

---

### Function 6: Warranty Claim Denial Notification
**Trigger:** Claim not eligible (outside warranty, accidental damage, condition issues, missing requirements)
**Examples:** Outside warranty period / Accidental damage / Missing documentation
**Required Input:**
- Customer first name
- Product name/type
- Denial reason (choose from: outside warranty period, accidental damage, normal wear and tear, missing documentation)
- Whether product is <2 years or >2 years old (for out-of-warranty cases)

**Task:** Generate a professional, empathetic email in American English that:
- Explains the specific reason for denial
- References the warranty policy clearly
- For out-of-warranty (<2 years): offers goodwill discount on a replacement
- For out-of-warranty (>2 years): declines and offers discount on a new purchase
- For accidental damage: explains the distinction between manufacturing defect and accidental damage
- Provides escalation contact: cs@catalystcase.com

**Approved Language — Accidental Damage:**
> "After reviewing your photos, the damage appears consistent with impact damage rather than a manufacturing defect. Our warranty covers manufacturing issues only. However, we'd like to help — here are some options: [alternatives]."

**Approved Language — Out of Warranty (<2 years):**
> "Your product is outside the 12-month warranty period. While we can't process a full warranty claim, we'd like to offer you [X]% off a replacement to make things right."

**Approved Language — Out of Warranty (>2 years):**
> "Your product is outside our warranty period. We're not able to process a claim at this stage, but we'd be happy to offer you a discount on a new purchase."

**Forbidden:**
- ❌ Approving claims for yellowing (cosmetic — not a manufacturing defect)
- ❌ Approving claims for accidental damage
- ❌ Making exceptions to warranty terms without management approval
- ❌ "We can't help you" — always offer an alternative path

---

### Function 7: Warranty Claim Resolution Notification
**Trigger:** Claim resolved (replacement shipped or store credit issued)
**Required Input:**
- Customer first name
- Product name/type
- Resolution type (replacement, store credit, refund)
- Tracking details or confirmation number

**Task:** Generate a resolution email in American English that:
- Confirms the claim resolution
- Provides tracking info if replacement shipped
- States expected arrival timeframe (if available)
- Reminds customer that replacement carries a 3-month warranty
- Offers support if any issues arise

**Approved Language:**
> "Your replacement [product] has been shipped. Your tracking number is [tracking]. It should arrive within [timeframe]."
> "Your replacement comes with a 3-month limited warranty from today's shipment date."
> "If you have any questions or run into any issues, reply to this email and we'll take care of you."

**Forbidden:**
- ❌ "Your replacement has the same warranty as the original" — it is 3 months, not 12
- ❌ Stating a delivery date without carrier confirmation

---

## Policy Reference (Source of Truth)

See: CANONICAL_policy_warranty.md for all policy details including:
- 12-month warranty from purchase date
- Coverage: manufacturing defects only
- NOT covered: accidental damage, misuse, normal wear, unauthorized modifications, yellowing
- Replacement warranty: 3 months from replacement shipment date
- Shipping fee may apply for replacement shipments
- Out-of-warranty (<2 years): goodwill discount
- Out-of-warranty (>2 years): discount on new purchase only
