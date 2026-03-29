# CANONICAL: CS Skill — Out-of-Stock Order Notification (CatalystLifestyle.com — International)

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
| 2026-03-25 | 1.0 | Created as International counterpart to oos-notification-us.md | KB governance alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`
- Order contains one or more items currently out of stock

---

## Key Rules (Locked)

- Always present options in this order: **Wait → Ship Available Now → Alternative → Refund**
- Refund timeline: **3–5 business days** to original payment method
- Do not promise a specific restock date unless confirmed with inventory team
- If no customer response after 7 days: send follow-up reminder
- Never cancel the order unilaterally — always give the customer the choice first

---

## Skill Functions

### Function 1: Partial Out-of-Stock Notification
**Trigger:** Order contains a mix of in-stock and out-of-stock items
**Required Input:** Order number (######), Customer name, In-stock items list, Out-of-stock items list with restock dates (if known)
**Task:** Write a clear, solution-focused email in International English that:
- Identifies which items are ready and which are out of stock
- Presents all four options in order (Wait / Ship Available / Alternative / Refund)
- Provides restock estimate if known; if not, states that clearly
- Asks the customer to reply with their preferred option
- Uses clear, simple language accessible to non-native English speakers

**Approved Language:**
> "Your order #[ORDER_NUMBER] contains items that are currently out of stock. Here is what we have available:"
> "We would like to offer you the following options: [list]"
> "If you choose a refund for the out-of-stock items, it will be processed within 3–5 business days to your original payment method."
> "Please reply and let us know which option you prefer."

**Forbidden:**
- ❌ Promising a restock date without inventory confirmation
- ❌ "We apologize for the inconvenience" (banned phrase)
- ❌ Cancelling the order without customer input
- ❌ Burying options in paragraphs — use a numbered or bulleted list

---

### Function 2: Full Out-of-Stock Notification
**Trigger:** All items in the order are out of stock
**Required Input:** Order number (######), Customer name, All item names, Restock dates if known, Available alternatives
**Task:** Write a clear, professional email in International English that:
- States all ordered items are currently out of stock
- Presents options: Wait / Choose alternative / Full refund
- Provides restock estimate if available
- States refund timeline clearly

**Approved Language:**
> "All items in your order #[ORDER_NUMBER] are currently out of stock."
> "We can hold your order until stock is available, switch you to an available alternative, or process a full refund."
> "A full refund would be processed within 3–5 business days to your original payment method."

**Forbidden:**
- ❌ Any unconfirmed restock date
- ❌ Automatically cancelling without offering options first
- ❌ Informal or colloquial phrasing

---

### Function 3: Restock Date Unknown
**Trigger:** Customer asks about restock timing and no confirmed date is available
**Required Input:** Order number (######), Customer name, Item name
**Task:** Write a brief, honest email in International English that:
- States clearly that a confirmed restock date is not available
- Offers to notify the customer when it returns
- Presents the refund option if they prefer not to wait

**Approved Language:**
> "We do not have a confirmed restock date for [item] at this time."
> "We will notify you as soon as it becomes available. If you would prefer not to wait, we can process a refund within 3–5 business days."

**Forbidden:**
- ❌ "It should be back soon" without confirmation
- ❌ Giving a date without inventory team confirmation

---

### Function 4: No-Response Follow-Up
**Trigger:** 7 days have passed since OOS notification with no customer response
**Required Input:** Order number (######), Customer name, Original notification date
**Task:** Write a brief follow-up email in International English that:
- References the original notification
- Restates options concisely
- States that a response is needed to proceed
- Sets a final response window

**Approved Language:**
> "We contacted you on [date] regarding your order #[ORDER_NUMBER] but have not yet received a response."
> "Please let us know how you would like to proceed: [brief option list]. If we do not hear from you within [X] days, we will [state default action]."

**Forbidden:**
- ❌ Cancelling without this follow-up being sent first
- ❌ Making the customer feel at fault for not responding

---

### Function 5: Resolution Confirmation
**Trigger:** Customer has chosen their preferred option
**Required Input:** Order number (######), Customer name, Chosen option, Next steps
**Task:** Write a brief confirmation email in International English that:
- Confirms the chosen option
- States what will happen next and by when
- For refunds: confirms 3–5 business day timeline

**Approved Language:**
> "Thank you for your response. We will [action based on chosen option]."
> "Your refund will be processed within 3–5 business days to your original payment method."

**Forbidden:**
- ❌ Any refund timeline other than 3–5 business days
- ❌ Promising shipment timing without fulfillment confirmation

---

## Key Difference from US Skill
- **Language:** International English (neutral, no US idioms, clear for ESL readers)
- **Order number format:** #67702 style
- **Support email:** info@catalystlifestyle.com
