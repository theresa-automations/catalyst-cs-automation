# CANONICAL: CS Skill — Order Modification (CatalystCase.com — US)

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
| 2026-03-24 | 1.0 | Initial version | Converted from Order Modification for CatalystUS.xlsx |
| 2026-03-25 | 1.1 | Added Key Rules (Locked) + Approved Language + Forbidden blocks | Temperature Zero alignment |

---

## Trigger Identification

All functions apply when:
- Email contains order number format `Ms#######`
- Email domain is `catalystcase.com`
- Customer requests a change to an existing order

---

## Key Rules (Locked)

- Modifications are **only possible before fulfillment** — once an order is fulfilled/shipped, changes are not possible
- Payment method **cannot be changed after capture** — the only options are cancel + reorder or refund after cancellation
- Cancellation refund: **3–5 business days** to original payment method
- Always check Shopify fulfillment status before confirming whether a modification is possible
- Never promise a modification is possible without verifying order status first
- Never cancel an order without the customer's explicit confirmation

---

## Skill Functions

### Skill 1: Order Cancellation
**Function:** Cancel an existing order when fulfillment has not started
**Trigger:** Customer requests cancellation
**Examples:** "Cancel my order" / "I don't need this anymore"
**Required Input:** Order number (Ms######), Customer name, Customer email
**Task:**
1. Confirm fulfillment status
2. Cancel the order if unfulfilled
3. Confirm cancellation to the customer
4. Explain refund timing if payment was captured
5. If cancellation is not possible, explain why and provide next steps
**Style:** American English — clear, calm, professional, solution-focused and reassuring

**Approved Language:**
> "Your order has been cancelled. If a payment was captured, your refund will be issued to your original payment method within 3–5 business days."
> "Your order has already been fulfilled and is on its way to you, so we're not able to cancel it at this stage. Once it arrives, you're welcome to return it through our portal at https://catalystcase.com/pages/returns."

**Forbidden:**
- ❌ Cancelling an order without the customer's explicit confirmation
- ❌ Any cancellation refund timeline other than 3–5 business days
- ❌ Promising cancellation is possible without checking Shopify fulfillment status first

---

### Skill 2: Shipping Address Update
**Function:** Update shipping address for existing order when possible
**Trigger:** Customer asks to change shipping address
**Examples:** "I need to change my shipping address" / "Can I update where this is going?"
**Required Input:** Order number (Ms######), New shipping address
**Task:**
1. Check order fulfillment status
2. Update shipping address if order has not shipped
3. Confirm the update to the customer
4. If already fulfilled, explain why change cannot be made
5. Provide guidance on delivery options or return process if needed
**Style:** American English — professional and clear, reassuring and policy-aware

**Approved Language:**
> "We've updated the shipping address on your order to [new address]. You'll receive a new confirmation shortly."
> "Your order has already shipped, so the address can't be changed at this stage. We'd recommend contacting the carrier directly with your tracking number to request a redirect."

**Forbidden:**
- ❌ Promising an address update is possible without verifying order status
- ❌ Guaranteeing a carrier redirect will succeed (carrier-dependent)

---

### Skill 3: Add Item to Order
**Function:** Handle requests to add items to an existing order
**Trigger:** Customer asks to add an item
**Examples:** "Can I add another item to my order?" / "I forgot to add something"
**Required Input:** Order number (Ms######), Item name or SKU
**Task:**
1. Check if order is still unfulfilled
2. Add the item if supported by Shopify
3. Adjust payment if required and explain next steps
4. If not possible, explain limitation and suggest placing a new order
**Style:** American English — helpful and transparent, solution-oriented

**Approved Language:**
> "We're not able to add items to an existing order once it's been placed, but you're welcome to place a new order for the additional item at catalystcase.com."
> "If your order hasn't shipped yet, we can cancel it and you can reorder with everything included — let us know if you'd like to go that route."

**Forbidden:**
- ❌ Promising items can be added without verifying Shopify capabilities for that order
- ❌ Adding items without confirming payment adjustment with the customer

---

### Skill 4: Product Variant Change
**Function:** Change product variant (color, size, model) on existing order
**Trigger:** Customer requests variant change
**Examples:** "Can I change the color?" / "I need a different size"
**Required Input:** Order number (Ms######), Product name, Requested variant
**Task:**
1. Retrieve order status
2. Confirm availability of requested variant
3. Update the order if unfulfilled
4. Confirm the change to the customer
5. If not possible, explain why and suggest exchange after delivery
**Style:** American English — warm and professional, clear and confidence-building

**Approved Language:**
> "We've updated your order to [new variant]. You'll receive a confirmation shortly."
> "Your order has already been fulfilled, so we're not able to change the variant at this stage. Once it arrives, you can exchange it through our return portal at https://catalystcase.com/pages/returns."

**Forbidden:**
- ❌ Confirming a variant change without checking availability first
- ❌ Promising a variant change is possible without verifying fulfillment status

---

### Skill 5: Payment Method Change
**Function:** Explain limitations around updating payment methods
**Trigger:** Customer asks to change payment details
**Examples:** "Can I update my payment method?" / "I used the wrong card"
**Required Input:** Order number (Ms######)
**Task:**
1. Check payment status
2. Explain that payment methods cannot be changed after capture
3. Confirm whether order is still valid
4. Offer alternatives (cancel and reorder, refund after cancellation)
**Style:** American English — professional and policy-clear, empathetic and solution-focused

**Approved Language:**
> "Once a payment has been captured, we're not able to change the payment method on the order. The options available are: cancel the order and reorder using the correct payment method, or we can process a refund to the original card once the order is cancelled."
> "If you'd like to cancel and reorder, let us know and we'll get the cancellation started right away."

**Forbidden:**
- ❌ Promising a payment method can be changed after capture (it cannot)
- ❌ Initiating a cancellation without the customer's explicit request

---

### Skill 6: General Modification Feasibility Check
**Function:** Determine whether any modification is still possible
**Trigger:** Vague modification request
**Examples:** "Can I still make changes to my order?" / "Is it too late to update my order?"
**Required Input:** Order number (Ms######)
**Task:**
1. Retrieve fulfillment status
2. Explain whether changes are still possible
3. Outline what can and cannot be modified at this stage
4. Provide next steps based on eligibility
**Style:** American English — clear and informative, calm and reassuring

**Approved Language:**
> "Your order hasn't shipped yet, so there's still a window to make changes. Here's what's possible at this stage: [list available options]."
> "Your order has already been fulfilled and is on its way. At this stage, we're not able to make changes — but once it arrives, you can return or exchange it through our portal at https://catalystcase.com/pages/returns."

**Forbidden:**
- ❌ Confirming modifications are possible without checking Shopify first
- ❌ Listing modification options that aren't actually available for this order's status

---

### Skill 7: Modification No Longer Possible
**Function:** Handle cases where order can no longer be modified
**Trigger:** Requested change blocked due to fulfillment status
**Examples:** Order already shipped / Order partially fulfilled
**Required Input:** Order number (Ms######), Requested change
**Task:**
1. Clearly explain why the change cannot be made
2. Reference fulfillment timing without internal jargon
3. Redirect customer to appropriate workflow (returns, exchanges, shipping status)
4. Maintain goodwill
**Style:** American English — warm, professional, empathetic, policy-forward without sounding restrictive

**Approved Language:**
> "Your order has already shipped, so we're not able to [requested change] at this point."
> "Once your order arrives, you can [return it / exchange it] through our portal at https://catalystcase.com/pages/returns — our team will take care of you from there."

**Forbidden:**
- ❌ Apologizing in a way that implies a policy error ("sorry for the inconvenience")
- ❌ Leaving the customer without a clear next step
