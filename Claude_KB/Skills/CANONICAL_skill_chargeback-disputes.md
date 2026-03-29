# CANONICAL: CS Skill — Chargeback Dispute Response

## Metadata
- **Last Updated**: 2026-03-25
- **Updated By**: Theresa
- **Version**: 1.1
- **Review Schedule**: Quarterly
- **Store**: CatalystCase.com (US)
- **Language Style**: Professional, legal-adjacent, assertive but respectful

## Change Log
| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-03-24 | 1.0 | Initial version | Merged from 5 Chargeback files in /Chargeback files/ subfolder |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Business Context

- **Company:** Catalyst Case US — catalystcase.com
- **Platform:** Shopify Plus
- **Store Timezone:** America/Los_Angeles (PST/PDT, UTC-8/-7)
- **Currency:** USD
- **Primary Challenge:** Customers filing fraudulent chargebacks after receiving products, claiming non-receipt or defects while retaining merchandise ("friendly fraud")

---

## Key Rules (Locked)

- **Never draft a response without completing all required data points first** — incomplete evidence loses disputes
- All timestamps must include **timezone** (e.g., "2:14 PM PST") — this is critical for timeline arguments
- **Never offer a refund, replacement, or concession** within the dispute response itself — doing so weakens the dispute and may constitute an admission
- **Never speculate** — only assert what is documented with evidence
- A chargeback response is a legal document — tone must be factual and unemotional throughout
- Response must lead with the strongest pillar (usually Pillar 1 — timeline)
- The agent does not make settlement decisions — escalate any customer outreach that accompanies the chargeback to human review

---

## Legal Strategy

The dispute response is crafted with the **authorial voice of a lawyer with 12 years of experience** working in a customer support capacity.

**Core strategy:** Prove friendly fraud through irrefutable timeline evidence and documentation of procedural violations.

**Success criteria:** Demonstrate the impossibility of the customer's claims OR show clear bad faith actions on the part of the customer.

**Tone:** Professional, factual, evidence-based, assertive but respectful.

---

## The Four Pillars (Core Dispute Arguments)

### Pillar 1: Timeline Inconsistencies
Focus on discrepancies between the order/delivery timeline and the chargeback filing date:
- Chargebacks filed **before** product delivery
- Chargebacks filed **after** delivery confirmation emails were sent
- Significant time gaps between product delivery and dispute filing

### Pillar 2: Procedural Violations
Highlight the customer's failure to follow established company procedures:
- Customer bypassed the established return policy
- No attempt was made to contact the merchant before filing
- Failure to provide required evidence (e.g., photos for defect claims)

### Pillar 3: Evidence of Fraud
Present direct evidence suggesting fraudulent intent:
- Retention of merchandise while simultaneously disputing the charge
- False claims directly contradicted by tracking data
- Pattern of bad faith behavior

### Pillar 4: Lack of Good Faith
Focus on the customer's lack of effort to resolve the issue with the merchant:
- No merchant communication attempts made
- No supporting documentation provided with the chargeback
- Immediate escalation to chargeback without any prior resolution attempt

---

## Required Data Points

Collect ALL of the following before drafting a response:

| Data Point | Description |
|---|---|
| Order number | Format: Ms###### |
| Order date and time | Exact date and time order was placed |
| Order total | Total amount in USD |
| Customer full name and email | Full contact information |
| Complete shipping address | Full address where order shipped |
| All product names with SKUs | Every item purchased with SKU |
| Shipping carrier | e.g., USPS |
| Tracking number | Unique tracking identifier |
| In-transit timestamp | When package was first marked in-transit |
| Estimated delivery date | Carrier's initial estimated delivery |
| Actual delivery date and time | Precise delivery date/time **including timezone** |
| Chargeback filing date and time | Date/time chargeback was filed **including timezone** |
| Chargeback reason | Reason stated by customer |
| Delivery confirmation email timestamp | Timestamp of delivery confirmation email (if applicable) |

---

## Three-Phase Workflow

### Phase 1: Data Collection
1. Navigate to order in Shopify Admin: `/orders/[ORDER_ID]`
2. Execute GraphQL query to retrieve complete order data
3. Verify USPS (or other carrier) tracking and final delivery status
4. Document chargeback filing date and stated reason
5. Calculate timeline gaps and identify inconsistencies
6. Check for delivery confirmation email timestamps
7. Verify there were no customer contact attempts in support records

### Phase 2: Analysis
1. **Identify inconsistency type:**
   - **Impossible Timeline:** Chargeback filed before delivery
   - **False Claim:** Delivery confirmed by tracking but customer claims non-receipt
   - **Retention Fraud:** Customer has product but is disputing charge
   - **No Evidence:** Defect claim filed without required documentation

2. **Calculate time gaps:**
   - Hours/days between delivery notification and chargeback filing
   - Days between actual delivery and chargeback filing
   - Identify timeline impossibilities

3. **Document procedural violations:**
   - No merchant contact made
   - No return request initiated
   - No evidence provided for the claim
   - Established return policy ignored

### Phase 3: Response Drafting

Apply the 10-section response template structure. Lead with the strongest pillar.

**Approved Language — Timeline Argument:**
> "The chargeback was filed on [date + timezone], [X hours/days] after the carrier confirmed delivery at [delivery date + timezone]. This timeline is inconsistent with a genuine non-receipt claim."

**Approved Language — Procedural Violation:**
> "Prior to filing the dispute, [customer name] made no attempt to contact Catalyst Case via our published support channel (cs@catalystcase.com) or to initiate a return through our established return portal at https://catalystcase.com/pages/returns."

**Approved Language — Tracking Evidence:**
> "Carrier tracking records confirm that the package was delivered to [address] on [date] at [time + timezone], and marked as [delivery scan status]. This data directly contradicts the claim of non-receipt."

---

## Response Tone Guidelines

**Use:**
- Precise dates and times (always include timezone)
- Specific tracking events with scan locations
- Direct references to policy the customer bypassed
- Factual, unemotional language

**Avoid:**
- Emotional or accusatory language
- Speculation ("the customer probably...")
- Any admission of fault or ambiguity
- Offering refunds or concessions in the dispute response

---

## Forbidden

- ❌ Never draft a response without completing all required data points first
- ❌ Never speculate — only state what is documented
- ❌ Never offer a refund, replacement, or concession within the dispute response itself
- ❌ Never use informal or emotional language
- ❌ Never omit timezone from delivery and chargeback timestamps — this is critical for timeline arguments
- ❌ Never assert "the customer is lying" — demonstrate the inconsistency with evidence instead
- ❌ Never respond to a chargeback that also includes a concurrent customer email without escalating the customer email to human review first
