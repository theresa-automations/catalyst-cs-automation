# CANONICAL: CS Skill — Warranty Claims (CatalystLifestyle.com — International)

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Monthly
- **Store**: CatalystLifestyle.com (International)
- **Language Style**: International English
- **Related Policy**: CANONICAL_policy_warranty.md

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Converted from Warranty Claim for Catalystlifestyle.xlsx |
| 2026-03-25 | 1.1 | Added locked phrases | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`

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
**Required Input:** Customer first name (optional), Warranty form URL
**Task:** Concise, professional email in **International English** — state 12-month warranty from purchase, explain manufacturing defect coverage, provide form URL, warm and professional tone, no overpromising.

**Approved Language:**
> "All Catalyst products come with a 12-month limited warranty from the purchase date. This covers defects in materials and workmanship — manufacturing issues, not accidental damage or normal wear."
> "To file a warranty claim, please visit: https://forms.fillout.com/t/8jPGm4Ck6Xus"

**Forbidden:**
- ❌ Any warranty period other than "12 months from purchase date"
- ❌ Stating replacement warranty as 12 months — it is 3 months from replacement shipment

---

### Function 2: Warranty Claim Initiation
**Trigger:** Customer reports product defect within warranty period
**Required Input:** Customer first name, Product name/type, Purchase date, Order number, Warranty form URL
**Task:** 150–200 word professional email in **International English** — greet by name, acknowledge issue with empathy, explain coverage clearly, provide form link, list required docs (photos: front, back, top, bottom, close-up; order number; purchase date), solution-focused close.

**Approved Language:**
> "I'm sorry to hear you are having trouble with your [product] — that is not the experience we want for you."
> "To start your warranty claim, please complete our form at https://forms.fillout.com/t/8jPGm4Ck6Xus. You will need clear photos of the defect (front, back, top, bottom, plus a close-up), your order number, and your purchase date."
> "Once we receive your submission, our team will review it within 24–48 hours and follow up with next steps."

**Forbidden:**
- ❌ "This is definitely covered" — claim has not been reviewed
- ❌ "We will send a replacement right away" — approval is required first

---

### Function 3: Warranty Claim Submitted Confirmation
**Trigger:** Customer has submitted the warranty form
**Required Input:** Customer first name, Customer email, Order number
**Task:** Confirmation email in **International English** — thank for submission, confirm receipt, state review timeline (24–48 hours standard; 5–7 business days complex), reassure customer, premium brand voice.

**Approved Language:**
> "We have received your warranty claim submission. Our team will review it within 24–48 hours and follow up with next steps."
> "If we require any additional information, we will contact you directly."

**Forbidden:**
- ❌ Any resolution promise before review is complete
- ❌ "Your claim will be approved"

---

### Function 4: Warranty Claim Status Update
**Trigger:** Claim under review or customer asks about status
**Required Input:** Customer first name, Customer email, Order number
**Task:** Reassuring status update email in **International English** — confirm under review, set timeline (5–7 business days), warm and confident, no robotic language.

**Approved Language:**
> "Your claim is currently under review. We typically complete reviews within 5–7 business days and will contact you as soon as a decision is made."

**Forbidden:**
- ❌ "Your claim will be approved"
- ❌ Any specific resolution before review is complete

---

### Function 5: Warranty Claim Approval
**Trigger:** Claim approved for replacement
**Required Input:** Customer first name, Product name, Order number
**Task:** Approval notification email in **International English** — confirm approval, present resolution options (replacement with 3-month warranty / refund / store credit), explain next steps, note shipping fee may apply.

**Approved Language:**
> "Your warranty claim has been approved. You may choose from the following options:"
> "**Replacement:** We will send you a new [product]. Your replacement comes with a 3-month limited warranty from the shipment date."
> "**Refund:** We will refund the full purchase price to your original payment method within 3–5 business days."
> "**Store credit:** We will issue store credit for a future purchase."

**Forbidden:**
- ❌ "Your replacement comes with a full warranty" — it is 3 months only
- ❌ "Free replacement" without confirming shipping fee policy

---

### Function 6: Warranty Claim Denial
**Trigger:** Claim not eligible (outside warranty, accidental damage, condition issues, missing requirements)
**Required Input:** Customer first name, Product name/type, Denial reason, Whether product is <2 years or >2 years old
**Task:** Professional, empathetic denial email in **International English** — explain denial reason, reference policy, suggest alternatives (goodwill discount if <2 years), provide contact: info@catalystlifestyle.com, solution-focused and warm.

**Approved Language — Accidental Damage:**
> "After reviewing your photos, the damage appears consistent with impact damage rather than a manufacturing defect. Our warranty covers manufacturing issues only. We would still like to help — here are some options: [alternatives]."

**Approved Language — Out of Warranty (<2 years):**
> "Your product is outside the 12-month warranty period. While we are unable to process a full warranty claim, we would like to offer you [X]% off a replacement."

**Approved Language — Out of Warranty (>2 years):**
> "Your product is outside our warranty period. We are not able to process a claim at this stage, but we would be happy to offer you a discount on a new purchase."

**Forbidden:**
- ❌ Approving claims for yellowing (cosmetic — not a manufacturing defect)
- ❌ Approving claims for accidental damage
- ❌ Making exceptions without management approval

---

### Function 7: Warranty Claim Resolution
**Trigger:** Claim resolved (replacement shipped or store credit issued)
**Required Input:** Customer first name, Product name/type, Resolution type, Tracking/confirmation
**Task:** Resolution email in **International English** — confirm resolution, provide tracking if applicable, state expected arrival, remind customer replacement carries 3-month warranty, offer further support.

**Approved Language:**
> "Your replacement [product] has been shipped. Your tracking number is [tracking]. It should arrive within [timeframe]."
> "Your replacement comes with a 3-month limited warranty from today's shipment date."

**Forbidden:**
- ❌ "Your replacement has the same warranty as the original" — it is 3 months, not 12

---

## Key Difference from US Skill
- **Language:** International English
- **Order number format:** #67702 style
- **Support email:** info@catalystlifestyle.com

## Policy Reference
See: CANONICAL_policy_warranty.md
