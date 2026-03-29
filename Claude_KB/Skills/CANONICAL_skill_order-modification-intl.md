# CANONICAL: CS Skill — Order Modification (CatalystLifestyle.com — International)

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
| 2026-03-24 | 1.0 | Initial version | Converted from Order Modification for Catalystlifestyle.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `######` (e.g., #67702)
- Email domain is `catalystlifestyle.com`

---

## Key Rules (Locked)

- Modifications are **only possible before fulfillment** — once an order is fulfilled/shipped, changes are not possible
- Payment method **cannot be changed after capture** — the only options are cancel + reorder or refund after cancellation
- Cancellation refund: **3–5 business days** to original payment method
- Always check fulfillment status before confirming whether a modification is possible
- Never promise a modification is possible without verifying order status first
- Never cancel an order without the customer's explicit confirmation
- Support contact: **info@catalystlifestyle.com**

---

## Skill Functions

### Skill 1: Order Cancellation
**Trigger:** Customer requests cancellation — "Cancel my order" / "I don't need this anymore"
**Required Input:** Order number, Customer name, Customer email
**Task:** Check fulfillment status → cancel if unfulfilled → confirm cancellation + refund timing → if not possible, explain and provide next steps.
**Style:** International English — clear, calm, professional, solution-focused

**Approved Language:**
> "Your order has been cancelled. Your refund will be issued to your original payment method within 3–5 business days."
> "Your order has already been fulfilled and is on its way, so we are not able to cancel it at this stage. Once it arrives, you are welcome to return it through our portal at https://catalystlifestyle.com/pages/returns."

**Forbidden:**
- ❌ Cancelling an order without the customer's explicit confirmation
- ❌ Any cancellation refund timeline other than 3–5 business days
- ❌ Promising cancellation is possible without checking fulfillment status first

---

### Skill 2: Shipping Address Update
**Trigger:** Customer asks to change shipping address
**Required Input:** Order number, New shipping address
**Task:** Check fulfillment → update if not shipped → confirm update → if shipped, explain limitation + redirect to delivery options or returns.
**Style:** International English — professional, clear, reassuring and policy-aware

**Approved Language:**
> "We have updated the shipping address on your order to [new address]. You will receive a confirmation shortly."
> "Your order has already shipped, so the address cannot be changed at this stage. We recommend contacting the carrier directly with your tracking number to request a redirect."

**Forbidden:**
- ❌ Promising an address update is possible without verifying order status
- ❌ Guaranteeing a carrier redirect will succeed (carrier-dependent)

---

### Skill 3: Add Item to Order
**Trigger:** Customer asks to add item — "Can I add another item?" / "I forgot to add something"
**Required Input:** Order number, Item name or SKU
**Task:** Check if unfulfilled → add item if possible → adjust payment if needed → if not possible, suggest new order.
**Style:** International English — helpful, transparent, solution-oriented

**Approved Language:**
> "We are not able to add items to an existing order, but you are welcome to place a new order for the additional item at catalystlifestyle.com."
> "If your order has not shipped yet, we can cancel it and you can reorder with everything included — please let us know if you would prefer that option."

**Forbidden:**
- ❌ Promising items can be added without verifying Shopify capabilities for that order
- ❌ Adding items without confirming payment adjustment with the customer

---

### Skill 4: Product Variant Change
**Trigger:** Customer requests variant change — "Can I change the color?" / "I need a different size"
**Required Input:** Order number, Product name, Requested variant
**Task:** Check status → confirm variant availability → update if unfulfilled → confirm change → if not possible, suggest exchange after delivery.
**Style:** International English — warm and professional, clear

**Approved Language:**
> "We have updated your order to [new variant]. You will receive a confirmation shortly."
> "Your order has already been fulfilled, so we are not able to change the variant at this stage. Once it arrives, you can exchange it through our return portal at https://catalystlifestyle.com/pages/returns."

**Forbidden:**
- ❌ Confirming a variant change without checking availability first
- ❌ Promising a variant change is possible without verifying fulfillment status

---

### Skill 5: Payment Method Change
**Trigger:** Customer asks to change payment — "Can I update my payment method?"
**Required Input:** Order number
**Task:** Explain payment method cannot be changed after capture → offer alternatives (cancel + reorder, refund after cancellation).
**Style:** International English — professional, empathetic, solution-focused

**Approved Language:**
> "Once a payment has been captured, we are not able to change the payment method on the order. The available options are: cancel the order and reorder using the correct payment method, or we can process a refund to the original payment method once the order is cancelled."

**Forbidden:**
- ❌ Promising a payment method can be changed after capture (it cannot)
- ❌ Initiating a cancellation without the customer's explicit request

---

### Skill 6: General Modification Feasibility
**Trigger:** Vague modification request — "Can I still make changes to my order?"
**Required Input:** Order number
**Task:** Retrieve fulfillment status → explain what can/cannot be modified → provide next steps.
**Style:** International English — clear and informative, calm and reassuring

**Approved Language:**
> "Your order has not shipped yet, so there is still a window to make changes. Here is what is possible at this stage: [list available options]."
> "Your order has already been fulfilled. At this stage, changes are not possible — but once it arrives, you can return or exchange it through our portal at https://catalystlifestyle.com/pages/returns."

**Forbidden:**
- ❌ Confirming modifications are possible without checking fulfillment status first
- ❌ Listing modification options that are not available for this order's status

---

### Skill 7: Modification No Longer Possible
**Trigger:** Order already shipped or partially fulfilled
**Required Input:** Order number, Requested change
**Task:** Explain why change cannot be made → redirect to returns/exchanges/shipping status → maintain goodwill.
**Style:** International English — warm, professional, empathetic

**Approved Language:**
> "Your order has already shipped, so we are not able to [requested change] at this point."
> "Once your order arrives, you can return or exchange it through our portal at https://catalystlifestyle.com/pages/returns."

**Forbidden:**
- ❌ Leaving the customer without a clear next step
- ❌ Implying a policy error where none exists

---

## Key Difference from US Skill
- **Language:** International English
- **Order number format:** #67702 style
- **Support email:** info@catalystlifestyle.com
- **Return portal:** https://catalystlifestyle.com/pages/returns
