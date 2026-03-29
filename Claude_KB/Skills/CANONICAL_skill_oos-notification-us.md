# CANONICAL: CS Skill — Out-of-Stock Order Notification (CatalystCase.com — US)

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
| 2026-03-25 | 1.0 | Converted from Out-of-Stock Order Notification Guide.md + moved to Skills/ | KB governance alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`
- Order contains one or more items currently out of stock

---

## Key Rules (Locked)

- Always present options in this order: **Wait → Ship Available Now → Alternative → Refund**
- Refund timeline: **3–5 business days** to original payment method
- Do not promise a specific restock date unless confirmed with inventory team
- If no customer response after 7 days: send follow-up reminder
- Never cancel the order unilaterally — always give the customer the choice first
- Partial shipments are only possible if Shopify supports it for this order

---

## Skill Functions

### Function 1: Partial Out-of-Stock Notification
**Trigger:** Order contains a mix of in-stock and out-of-stock items
**Examples:** "Some items in your order aren't available yet" / order has multiple SKUs with mixed availability
**Required Input:** Order number (Ms######), Customer name, List of in-stock items, List of out-of-stock items with estimated restock dates (if known)
**Task:** Write a clear, solution-focused email in American English that:
- Identifies which items are ready and which are out of stock
- Presents all four options in order (Wait / Ship Available / Alternative / Refund)
- Provides restock estimate if known — if unknown, state that
- Asks the customer to reply with their preferred option
- Sets a 7-day follow-up expectation

**Approved Language:**
> "Your order #[ORDER_NUMBER] contains items that are currently out of stock. Here's what we have:"
> "We want to give you the best options, so here's what we can do: [list options]"
> "If you'd like a refund for the out-of-stock items, it will be processed within 3–5 business days to your original payment method."
> "Please reply and let us know which option works best for you."

**Forbidden:**
- ❌ Promising a restock date without warehouse confirmation
- ❌ "We apologize for the inconvenience" (banned phrase — instead: "We want to make sure you're taken care of")
- ❌ Cancelling the order without customer input
- ❌ Burying options in paragraph form — use a numbered or bulleted list

---

### Function 2: Full Out-of-Stock Notification
**Trigger:** All items in the order are out of stock
**Required Input:** Order number (Ms######), Customer name, All item names, Restock dates if known, Available alternatives
**Task:** Write a clear, empathetic email in American English that:
- States that all ordered items are currently out of stock
- Presents options: Wait for restock / Choose alternatives / Full refund
- Provides restock estimate if known
- States refund timeline if that option is chosen
- Asks for customer response

**Approved Language:**
> "All items in your order #[ORDER_NUMBER] are currently out of stock."
> "We can hold your order until stock is available, switch you to an available alternative, or process a full refund."
> "A full refund would be processed within 3–5 business days to your original payment method."

**Forbidden:**
- ❌ Any promise about when stock will return without confirmation
- ❌ Automatically cancelling and refunding without offering the hold/alternative option first
- ❌ "Unfortunately" as a sentence opener (weak framing — state facts directly)

---

### Function 3: Restock Date Unknown
**Trigger:** Customer asks about restock timing and the date is not confirmed
**Required Input:** Order number (Ms######), Customer name, Item name
**Task:** Write a brief, honest email in American English that:
- Acknowledges the item is out of stock
- States clearly that a confirmed restock date is not available
- Offers to notify the customer when it returns
- Presents the refund option if they cannot wait

**Approved Language:**
> "We don't have a confirmed restock date for [item] at this time."
> "We'll notify you as soon as it's back in stock. If you'd prefer not to wait, we can process a refund within 3–5 business days."

**Forbidden:**
- ❌ "It should be back soon" without confirmation (creates false expectations)
- ❌ Giving a date without inventory team confirmation
- ❌ "We have no idea when it will be back" (unprofessional — say "a confirmed date is not available")

---

### Function 4: No-Response Follow-Up
**Trigger:** 7 days have passed since the OOS notification with no customer response
**Required Input:** Order number (Ms######), Customer name, Original notification date
**Task:** Write a brief follow-up email in American English that:
- References the original notification
- Restates the options concisely
- States that a decision is needed to proceed
- Sets a final response window (3–5 business days)

**Approved Language:**
> "We reached out on [date] about your order #[ORDER_NUMBER] but haven't heard back yet."
> "Please let us know how you'd like to proceed: [brief option list]. If we don't hear from you within [X] days, we'll [state default action — hold or refund, per internal policy]."

**Forbidden:**
- ❌ Cancelling without sending this follow-up first
- ❌ Making the customer feel blamed for not responding

---

### Function 5: Resolution Confirmation
**Trigger:** Customer has chosen their preferred option (wait, ship available, alternative, or refund)
**Required Input:** Order number (Ms######), Customer name, Chosen option, Next steps for that option
**Task:** Write a brief confirmation email in American English that:
- Confirms the option chosen
- States what will happen next and by when
- For refunds: confirms 3–5 business day timeline
- For ship available: confirms shipment timing
- For wait: confirms when you'll follow up

**Approved Language:**
> "Got it — we'll [action based on chosen option]."
> "Your refund will be processed within 3–5 business days to your original payment method."
> "We'll send your shipping confirmation as soon as the in-stock items leave our warehouse."

**Forbidden:**
- ❌ Any refund timeline other than 3–5 business days
- ❌ Promising same-day or next-day shipment without confirming with fulfillment

---

## Policy Reference
- Refund timeline: 3–5 business days to original payment method
- Options order: Wait → Ship Available → Alternative → Refund
- Follow-up if no response: 7 days
- Restock dates: only state if confirmed with inventory team
- Support contact: cs@catalystcase.com
