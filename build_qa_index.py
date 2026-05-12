"""
build_qa_index.py
Generates catalyst_kb_qa_index.json from CANONICAL KB files.
Following June's Q&A ontology: The Case | The Device | The Feature
Sources: CANONICAL_product_* + CANONICAL_policy_* + CANONICAL_skill_*
"""

import re
import json
import hashlib
from pathlib import Path

KB_DIR = Path(r"C:\Users\pc\Documents\Catalyst-Projects\Claude_KB")
SKILLS_DIR = KB_DIR / "Skills"
OUTPUT_FILE = Path(r"C:\Users\pc\Documents\Catalyst-Projects\catalyst_kb_qa_index.json")

# ─────────────────────────────────────────────────────────
# METADATA MAPS
# ─────────────────────────────────────────────────────────

PRODUCT_META = {
    "CANONICAL_product_influence-case-iphone16-series.md": {
        "product_family": "Influence Case",
        "sub_category": "Phone Case",
        "compatible_devices": ["iPhone 16", "iPhone 16 Plus", "iPhone 16 Pro", "iPhone 16 Pro Max"],
        "is_waterproof": False,
        "has_magnets": True,
        "drop_rating": "MIL-STD-810G",
        "material": "Dual-layer PC + TPU",
        "store": "US",
        "product_page": "https://catalystcase.com/pages/support-influence-camera-control",
    },
    "CANONICAL_product_waterproof-iphone16-15-14.md": {
        "product_family": "Waterproof Total Protection Case",
        "sub_category": "Phone Case",
        "compatible_devices": [
            "iPhone 16", "iPhone 16 Pro", "iPhone 16 Pro Max",
            "iPhone 15", "iPhone 15 Plus", "iPhone 15 Pro", "iPhone 15 Pro Max",
            "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
        ],
        "is_waterproof": True,
        "waterproof_rating": "IP68 — 10m / 30min",
        "has_magnets": True,
        "drop_rating": "MIL-STD-810G",
        "material": "Polycarbonate with silicone O-ring seal",
        "store": "US",
        "product_page": "https://catalystcase.com/pages/support-waterproof-case-iphone-16-15",
    },
    "CANONICAL_product_influence-case-iphone17-pro.md": {
        "product_family": "Influence Case with Thermo-Flow",
        "sub_category": "Phone Case",
        "compatible_devices": ["iPhone 17 Pro", "iPhone 17 Pro Max"],
        "is_waterproof": False,
        "waterproof_planned": False,
        "has_magnets": True,
        "drop_rating": "MIL-STD-810G",
        "material": "Dual-layer PC + TPU",
        "store": "US",
        "product_page": "https://catalystcase.com/pages/support-influence-thermo-flow",
    },
    "CANONICAL_product_crux-case-iphone14-16e.md": {
        "product_family": "Crux Case",
        "sub_category": "Phone Case",
        "compatible_devices": [
            "iPhone 17e", "iPhone 16e",
            "iPhone 14", "iPhone 14 Plus", "iPhone 14 Pro", "iPhone 14 Pro Max",
            "iPhone 13", "iPhone 13 mini", "iPhone 13 Pro", "iPhone 13 Pro Max",
        ],
        "is_waterproof": False,
        "has_magnets": False,
        "drop_rating": "5× MIL-STD-810G",
        "material": "Single-piece monolithic TPU",
        "store": "US",
    },
    "CANONICAL_product_influence-case-iphone17.md": {
        "product_family": "Influence Case with Thermo-Flow",
        "sub_category": "Phone Case",
        "compatible_devices": ["iPhone 17", "iPhone 17 Plus"],
        "is_waterproof": False,
        "has_magnets": True,
        "drop_rating": "MIL-STD-810G",
        "material": "Dual-layer PC + TPU",
        "store": "US",
        "product_page": "https://catalystcase.com/pages/support-influence-thermo-flow",
    },
    "CANONICAL_product_airpods-total-protection-pro2-gen3.md": {
        "product_family": "AirPods Total Protection Case",
        "sub_category": "AirPods Case",
        "compatible_devices": ["AirPods Pro 2nd Gen", "AirPods 3rd Gen"],
        "is_waterproof": True,
        "has_magnets": False,
        "material": "Polycarbonate",
        "store": "US",
    },
    "CANONICAL_product_airpods-total-protection-pro3-gen4.md": {
        "product_family": "AirPods Total Protection Case",
        "sub_category": "AirPods Case",
        "compatible_devices": ["AirPods Pro 3rd Gen", "AirPods 4th Gen"],
        "is_waterproof": True,
        "has_magnets": False,
        "material": "Polycarbonate",
        "store": "US",
    },
    "CANONICAL_product_tempered-glass-screen-protector.md": {
        "product_family": "Tempered Glass Screen Protector",
        "sub_category": "Screen Protector",
        "compatible_devices": ["Various iPhone models"],
        "is_waterproof": False,
        "has_magnets": False,
        "material": "Tempered glass",
        "store": "US",
    },
    "CANONICAL_product_crux-attachment-accessories.md": {
        "product_family": "Crux System Accessories",
        "sub_category": "Accessory",
        "compatible_devices": ["All Crux System compatible cases"],
        "is_waterproof": False,
        "has_magnets": False,
        "material": "Various",
        "store": "US",
    },
    "CANONICAL_product_ipad-waterproof-cases.md": {
        "product_family": "iPad Waterproof Case",
        "sub_category": "iPad Case",
        "compatible_devices": ["iPad"],
        "is_waterproof": True,
        "has_magnets": False,
        "material": "Polycarbonate with silicone O-ring seal",
        "store": "US",
    },
    "CANONICAL_product_crossbody-shoulder-strap.md": {
        "product_family": "Crossbody Shoulder Strap",
        "sub_category": "Accessory",
        "compatible_devices": ["All Crux System compatible cases"],
        "is_waterproof": False,
        "has_magnets": False,
        "material": "Various",
        "store": "US",
    },
}

POLICY_META = {
    "CANONICAL_policy_warranty.md": {"topic": "warranty", "node": "The Case"},
    "CANONICAL_policy_returns.md": {"topic": "returns", "node": "The Case"},
}

# GDrive file IDs — sourced from catalyst_draft.md Step 4.5 table.
# Format: https://drive.google.com/file/d/{ID}/view
# Product/policy IDs are null until confirmed after GDrive upload.
GDRIVE_IDS = {
    # Skills (IDs confirmed in catalyst_draft.md)
    "CANONICAL_skill_warranty-claim-us.md":                   "1dHIlpP82Z7ktm6rqdlPOZl6aYuL3aXZf",
    "CANONICAL_skill_warranty-claim-intl.md":                 "1roo3rtpij7zOwvQo48iHUro6I_tBZzuH",
    "CANONICAL_skill_order-shipping-us.md":                   "1FKreoe2yCSiq6NvAowCyVySOITeHF9CZ",
    "CANONICAL_skill_order-shipping-intl.md":                 "1DSyCLqYDdMY4-MYZdSaBz64u6O5aovSY",
    "CANONICAL_skill_order-modification-us.md":               "1BJhLFRFBWhoaYVuJBzmx2IPJrKc9AliG",
    "CANONICAL_skill_order-modification-intl.md":             "1zZjG-XoPX9DE6mxXrOwEv5s5Xyke1X1t",
    "CANONICAL_skill_return-processing-us.md":                "13vNBxb6drC4-9TFnUeG5PfvitYLTLt43",
    "CANONICAL_skill_return-processing-intl.md":              "1aMvNXMUIfQfmaWDke1wgRRK1gx2TuT2B",
    "CANONICAL_skill_return-tracking-us.md":                  "1CiUOnXlvactzAocW7VIXjAX8mdG-WwHT",
    "CANONICAL_skill_return-tracking-intl.md":                "1zbsQzcf8HO0WFjF5giIkv_PyociFSyO5",
    "CANONICAL_skill_address-verification-us.md":             "1mKQXdXoYakWP8gHPACGF6bq4_BYgOrzg",
    "CANONICAL_skill_address-verification-intl.md":           "1i_Y6hx_L_zCwXVk8nxjRANRTxP1iImWz",
    "CANONICAL_skill_oos-notification-us.md":                 "1K3QFfGkmyoVgNzMTrdSMdwyp7fgMs0Y4",
    "CANONICAL_skill_oos-notification-intl.md":               "1ot1PqkStQskJjjgcYHoov1Qc1e32muJZ",
    "CANONICAL_skill_chargeback-disputes.md":                 "1FQiUulyEWeu17VKdJorFTX15UR4H3bxv",
    "CANONICAL_skill_product-support-waterproof-iphone.md":   "12nwAztnuBZ6UrENMylr_ST_yhXfFvN7J",
    "CANONICAL_skill_product-support-influence-iphone12-15.md": "18DGHOZq_PREGR4furQ6DeA9NRUfHxRSa",
    "CANONICAL_skill_product-support-influence-iphone16.md":  "19ZOEyBE7ycxolwEOVCkh0mIvRFozz6dq",
    "CANONICAL_skill_product-support-influence-iphone17.md":  "1mAk5AIuzWb4YsXGJrn5VXB0wFyFhqRj9",
    # Product files — confirmed by user 2026-05-04
    "CANONICAL_product_influence-case-iphone16-series.md":    "1XmxsldGvSu_uCkb6Wm6Ixc70RRIfgHy2",
    "CANONICAL_product_waterproof-iphone16-15-14.md":         "16bw2gdT7tnp25zcKq6cwbWT8C64-QlVA",
    "CANONICAL_product_influence-case-iphone17-pro.md":       "1bFExtfLBFfhSYKymldUeSpG14nT0okDy",
    "CANONICAL_product_crux-case-iphone14-16e.md":            "1za9FacCmR4Pcnb-COR90YHaFHpLkKNmH",
    "CANONICAL_product_influence-case-iphone17.md":           "1ike6RTn2BL7bglPSm2C2nkozZUzSlMjE",
    "CANONICAL_product_airpods-total-protection-pro2-gen3.md": "1VluShsPaZ8Le9q2xOHBL0-DtqixBD7wP",
    "CANONICAL_product_airpods-total-protection-pro3-gen4.md": "1Ko9fJ3v3x_KdWACZ-012UbBY8x_hAmuQ",
    "CANONICAL_product_tempered-glass-screen-protector.md":   "11UlDXdwQgcZURGFxa9lsJUCuZj5-Tp-o",
    "CANONICAL_product_crux-attachment-accessories.md":       "1Rx1aXv5gEbZ9qu9COAc9h41qYFV7VSsX",
    "CANONICAL_product_ipad-waterproof-cases.md":             "1rfnUNOLLMW4nINZ8vvs5qo9ct13WyVu6",
    "CANONICAL_product_crossbody-shoulder-strap.md":          "1TvLba6NZEEX2Ie5rmuUclJbsupSi0lyM",
    # Policy files — confirmed by user 2026-05-04
    "CANONICAL_policy_warranty.md":                           "1QAVKRIYn4qmALYUZ285Lr_bRh2v4CSqU",
    "CANONICAL_policy_returns.md":                            "1b2Edb6YTcCTjmnHj8g5ec5VnRAQ7qFB4",
    # Brand + reference files — on GDrive, not currently indexed
    "CANONICAL_brand_design-philosophy.md":                   "12gd3ij6w3ZUKavLjDy-aFulzhcXJc97j",
    "CANONICAL_reference_iphone-model-identification.md":     "1xsENDpu2PljVRBP96Jdq_GLEymushf1X",
}


def gdrive_url(filename):
    fid = GDRIVE_IDS.get(filename)
    if fid:
        return f"https://drive.google.com/file/d/{fid}/view"
    return None


SKILL_META = {
    # ── Warranty ──────────────────────────────────────────────────────────
    "CANONICAL_skill_warranty-claim-us.md": {
        "service_area": "Warranty Claims",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "warranty",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_warranty-claim-intl.md": {
        "service_area": "Warranty Claims",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "warranty",
        "compatible_devices": ["All"],
    },
    # ── Returns ────────────────────────────────────────────────────────────
    "CANONICAL_skill_return-processing-us.md": {
        "service_area": "Return Processing",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "returns",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_return-processing-intl.md": {
        "service_area": "Return Processing",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "returns",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_return-tracking-us.md": {
        "service_area": "Return Tracking",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "returns",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_return-tracking-intl.md": {
        "service_area": "Return Tracking",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "returns",
        "compatible_devices": ["All"],
    },
    # ── Shipping ───────────────────────────────────────────────────────────
    "CANONICAL_skill_order-shipping-us.md": {
        "service_area": "Order Shipping & Delivery",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "shipping",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_order-shipping-intl.md": {
        "service_area": "Order Shipping & Delivery",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "shipping",
        "compatible_devices": ["All"],
    },
    # ── Order Modification ─────────────────────────────────────────────────
    "CANONICAL_skill_order-modification-us.md": {
        "service_area": "Order Modification",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "order_management",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_order-modification-intl.md": {
        "service_area": "Order Modification",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "order_management",
        "compatible_devices": ["All"],
    },
    # ── Address Verification ───────────────────────────────────────────────
    "CANONICAL_skill_address-verification-us.md": {
        "service_area": "Address Verification & Order Holds",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "order_management",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_address-verification-intl.md": {
        "service_area": "Address Verification & Order Holds",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "order_management",
        "compatible_devices": ["All"],
    },
    # ── OOS Notification ───────────────────────────────────────────────────
    "CANONICAL_skill_oos-notification-us.md": {
        "service_area": "Out-of-Stock Notification",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "inventory",
        "compatible_devices": ["All"],
    },
    "CANONICAL_skill_oos-notification-intl.md": {
        "service_area": "Out-of-Stock Notification",
        "sub_category": "CS Workflow",
        "store": "INTL",
        "default_topic": "inventory",
        "compatible_devices": ["All"],
    },
    # ── Chargebacks ────────────────────────────────────────────────────────
    "CANONICAL_skill_chargeback-disputes.md": {
        "service_area": "Chargeback Dispute Response",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "chargeback",
        "compatible_devices": ["All"],
    },
    # ── Product Support ────────────────────────────────────────────────────
    "CANONICAL_skill_product-support-influence-iphone12-15.md": {
        "service_area": "Product Support — Influence Case",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "installation",
        "compatible_devices": ["iPhone 12", "iPhone 13", "iPhone 14", "iPhone 15", "iPhone 15 Plus"],
    },
    "CANONICAL_skill_product-support-influence-iphone16.md": {
        "service_area": "Product Support — Influence Case",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "installation",
        "compatible_devices": ["iPhone 16 Pro", "iPhone 16 Pro Max"],
    },
    "CANONICAL_skill_product-support-influence-iphone17.md": {
        "service_area": "Product Support — Influence Case",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "installation",
        "compatible_devices": ["iPhone 17", "iPhone 17 Plus", "iPhone 17 Pro", "iPhone 17 Pro Max"],
    },
    "CANONICAL_skill_product-support-waterproof-iphone.md": {
        "service_area": "Product Support — Waterproof Case",
        "sub_category": "CS Workflow",
        "store": "US",
        "default_topic": "waterproofing",
        "compatible_devices": ["Various iPhone models"],
    },
}


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────

def make_id(source, text):
    h = hashlib.md5(f"{source}::{text}".encode()).hexdigest()[:8]
    return f"qa_{h}"


def classify_topic(question, answer):
    combined = (question + " " + answer).lower()
    if any(w in combined for w in ["waterproof", "ip68", "submerge", "water resistant"]):
        return "waterproofing"
    if any(w in combined for w in ["yellow", "discolor"]):
        return "discoloration"
    if any(w in combined for w in ["install", "remove", "snap", "seat", "insertion"]):
        return "installation"
    if any(w in combined for w in ["clean", "soap", "alcohol", "wipe", "disinfect"]):
        return "cleaning"
    if any(w in combined for w in ["warranty", "defect", "coverage", "claim", "replace"]):
        return "warranty"
    if any(w in combined for w in ["magsafe", "magnet", "wireless", "qi charging"]):
        return "charging_compatibility"
    if any(w in combined for w in ["drop", "mil-std", "impact", "drop protection"]):
        return "drop_protection"
    if any(w in combined for w in ["screen protector", "tempered glass"]):
        return "screen_protector"
    if any(w in combined for w in ["camera control", "camera button"]):
        return "camera_features"
    if any(w in combined for w in ["thermo-flow", "heat", "warm", "vent", "temperature"]):
        return "thermal_management"
    if any(w in combined for w in ["true sound", "acoustic", "audio", "speaker", "sound"]):
        return "audio_features"
    if any(w in combined for w in ["lanyard", "strap", "attach", "crux system", "carabiner"]):
        return "accessories"
    if any(w in combined for w in ["mute switch", "rotating dial"]):
        return "controls"
    if any(w in combined for w in ["return", "refund", "exchange", "send back"]):
        return "returns"
    if any(w in combined for w in ["chargeback", "dispute", "friendly fraud"]):
        return "chargeback"
    if any(w in combined for w in ["track", "tracking", "shipped", "delivery", "usps", "carrier"]):
        return "shipping"
    if any(w in combined for w in ["address", "hold", "undeliverable", "wrong address"]):
        return "order_management"
    if any(w in combined for w in ["modify", "cancel", "change order", "order status"]):
        return "order_management"
    if any(w in combined for w in ["out of stock", "back in stock", "unavailable", "inventory"]):
        return "inventory"
    if any(w in combined for w in ["compatible", "fit", "work with", "model"]):
        return "compatibility"
    return "general"


def classify_node(topic):
    device_topics = {"compatibility", "screen_protector", "charging_compatibility"}
    feature_topics = {"discoloration", "cleaning", "thermal_management", "audio_features",
                      "camera_features", "controls", "accessories", "drop_protection"}
    if topic in device_topics:
        return "The Device"
    if topic in feature_topics:
        return "The Feature"
    return "The Case"


# ─────────────────────────────────────────────────────────
# PARSERS — PRODUCT FILES
# ─────────────────────────────────────────────────────────

def parse_faq_section(content):
    entries = []
    faq_match = re.search(
        r'#{2,3}\s+FAQ[^\n]*\n(.*?)(?=\n#{2,3}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not faq_match:
        return entries
    faq_text = faq_match.group(1)
    pattern = re.compile(
        r'\*\*Q:\s*(.+?)\*\*\s*\n+\s*>\s*(.+?)(?=\n\s*\n\*\*Q:|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(faq_text):
        question = m.group(1).strip().rstrip('*').strip()
        answer = re.sub(r'\n\s*>\s*', ' ', m.group(2)).strip()
        if question and answer:
            entries.append((question, answer))
    return entries


def parse_key_specs(content):
    specs = {}
    table_match = re.search(
        r'\|\s*Feature\s*\|\s*Detail\s*\|(.*?)(?=\n#{2,}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not table_match:
        return specs
    header_seen = False
    for row in table_match.group(1).strip().split('\n'):
        if re.match(r'\s*\|[-\s|]+\|\s*', row):
            header_seen = True
            continue
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 2 and header_seen:
            specs[parts[0]] = parts[1]
    return specs


def parse_forbidden_block(content, section_header=r'What NOT to Say'):
    rules = []
    match = re.search(
        r'#{2,3}\s+' + section_header + r'[^\n]*\n(.*?)(?=\n#{2,}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return rules
    for line in match.group(1).split('\n'):
        line = line.strip()
        if '❌' in line:
            rule = re.sub(r'^-?\s*❌\s*', '', line).strip()
            if rule:
                rules.append(rule)
    return rules


def parse_skill_forbidden(block_text):
    rules = []
    for line in block_text.split('\n'):
        line = line.strip()
        if '❌' in line:
            rule = re.sub(r'^-?\s*❌\s*', '', line).strip()
            if rule:
                rules.append(rule)
    return rules


def build_spec_qa(product_name, specs, meta):
    entries = []
    wpt = specs.get('Waterproof', specs.get('Waterproof Rating', ''))
    if wpt:
        if meta.get('is_waterproof'):
            a = f"Yes. It is IP68 rated — {meta.get('waterproof_rating', wpt)}. Always perform the water test before first use and after any impacts."
        else:
            planned = ' There are currently no plans to release a waterproof version.' if meta.get('waterproof_planned') is False else ''
            a = f"No. The {product_name} is drop-proof only — it is not waterproof.{planned}"
        entries.append((f"Is the {product_name} waterproof?", a.strip()))

    drop = specs.get('Drop Protection', meta.get('drop_rating', ''))
    if drop:
        entries.append((
            f"What drop protection does the {product_name} provide?",
            f"The {product_name} meets {drop}, covering over 99% of real-world drop accidents."
        ))

    if specs.get('MagSafe', '') and meta.get('has_magnets'):
        entries.append((
            f"Is the {product_name} compatible with MagSafe?",
            f"Yes — the {product_name} is fully compatible with MagSafe and Qi wireless charging."
        ))

    warranty = specs.get('Warranty', '')
    if warranty:
        entries.append((
            f"What is the warranty on the {product_name}?",
            f"{warranty}. Covers manufacturing defects under normal use. Normal wear, cosmetic changes, and misuse are not covered."
        ))
    return entries


def process_product_file(filepath, filename):
    meta = PRODUCT_META.get(filename, {})
    if not meta:
        print(f"  [SKIP] No metadata for {filename}")
        return []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    product_name = meta["product_family"]
    compatible = meta.get("compatible_devices", [])
    store = meta.get("store", "US")
    sub_cat = meta.get("sub_category", "Phone Case")
    entries = []

    for question, answer in parse_faq_section(content):
        topic = classify_topic(question, answer)
        entry = {
            "entry_id": make_id(filename, question),
            "source": filename,
            "product_family": product_name,
            "sub_category": sub_cat,
            "store": store,
            "compatible_devices": compatible,
            "node": classify_node(topic),
            "topic": topic,
            "question": question,
            "answer": answer,
            "confidence": "locked",
            "generation": "faq_extracted",
        }
        if meta.get("product_page"):
            entry["product_page"] = meta["product_page"]
        url = gdrive_url(filename)
        if url:
            entry["source_gdrive_url"] = url
        entries.append(entry)

    seen_questions = {e["question"] for e in entries}
    for question, answer in build_spec_qa(product_name, parse_key_specs(content), meta):
        if question in seen_questions:
            continue
        topic = classify_topic(question, answer)
        entry = {
            "entry_id": make_id(filename + "_spec", question),
            "source": filename,
            "product_family": product_name,
            "sub_category": sub_cat,
            "store": store,
            "compatible_devices": compatible,
            "node": classify_node(topic),
            "topic": topic,
            "question": question,
            "answer": answer,
            "confidence": "locked",
            "generation": "rule_based",
        }
        if meta.get("product_page"):
            entry["product_page"] = meta["product_page"]
        if url:
            entry["source_gdrive_url"] = url
        entries.append(entry)

    for rule in parse_forbidden_block(content):
        e = {
            "entry_id": make_id(filename + "_forbidden", rule),
            "source": filename,
            "product_family": product_name,
            "sub_category": sub_cat,
            "store": store,
            "compatible_devices": compatible,
            "node": "The Case",
            "topic": classify_topic(rule, ""),
            "question": None,
            "answer": None,
            "forbidden_response": rule,
            "confidence": "locked",
            "generation": "forbidden_rule",
        }
        if url:
            e["source_gdrive_url"] = url
        entries.append(e)

    return entries


# ─────────────────────────────────────────────────────────
# PARSERS — POLICY FILES
# ─────────────────────────────────────────────────────────

def parse_exact_language(content):
    pairs = []
    match = re.search(
        r'#{2,3}\s+Exact Language to Use[^\n]*\n(.*?)(?=\n#{2,}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return pairs
    pattern = re.compile(
        r'\*\*For\s+(.+?):\*\*\s*\n+\s*>\s*"?(.+?)"?\s*(?=\n\n\*\*For|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(match.group(1)):
        scenario = m.group(1).strip()
        answer = re.sub(r'\n\s*>\s*', ' ', m.group(2)).strip().strip('"')
        pairs.append((f"What should I say for: {scenario}?", answer, scenario))
    return pairs


def parse_key_facts_table(content):
    pairs = []
    match = re.search(
        r'#{2,3}\s+Key Facts[^\n]*\n(.*?)(?=\n#{2,}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return pairs
    header_seen = False
    skip_labels = {"policy point", "feature", "detail", "spec"}
    for row in match.group(1).strip().split('\n'):
        if re.match(r'\s*\|[-\s|]+\|\s*', row):
            header_seen = True
            continue
        parts = [p.strip() for p in row.split('|') if p.strip()]
        if len(parts) >= 2 and header_seen:
            fact, detail = parts[0], parts[1]
            if fact.lower() in skip_labels or detail.lower() in ("detail", "value", ""):
                continue
            pairs.append((f"What is the {fact.lower()}?", detail))
    return pairs


def process_policy_file(filepath, filename):
    meta = POLICY_META.get(filename, {})
    topic_default = meta.get("topic", "general")

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    entries = []
    url = gdrive_url(filename)
    base = {"source": filename, "product_family": "All Products",
            "sub_category": "Policy", "store": "US+INTL",
            "compatible_devices": ["All"], "node": "The Case",
            "confidence": "locked"}
    if url:
        base["source_gdrive_url"] = url

    for question, answer in parse_faq_section(content):
        topic = classify_topic(question, answer)
        e = {**base, "entry_id": make_id(filename, question), "topic": topic,
             "question": question, "answer": answer, "generation": "policy_faq_extracted"}
        entries.append(e)

    for question, answer, scenario in parse_exact_language(content):
        topic = classify_topic(scenario + " " + answer, answer)
        if topic == "general":
            topic = topic_default
        e = {**base, "entry_id": make_id(filename, question), "topic": topic,
             "question": question, "answer": answer, "generation": "policy_approved_language"}
        entries.append(e)

    for question, answer in parse_key_facts_table(content):
        topic = classify_topic(question, answer)
        if topic == "general":
            topic = topic_default
        e = {**base, "entry_id": make_id(filename, question), "topic": topic,
             "question": question, "answer": answer, "generation": "policy_key_facts"}
        entries.append(e)

    for rule in parse_forbidden_block(content):
        e = {**base, "entry_id": make_id(filename + "_forbidden", rule),
             "topic": topic_default, "question": None, "answer": None,
             "forbidden_response": rule, "generation": "forbidden_rule"}
        entries.append(e)

    return entries


# ─────────────────────────────────────────────────────────
# PARSERS — SKILL FILES
# ─────────────────────────────────────────────────────────

def parse_skill_functions(content):
    """
    Parse all Skill / Function / Pillar blocks from a skills file.
    Returns list of dicts: {name, trigger, examples, approved_language, forbidden}
    """
    functions = []

    # Split content into function blocks on ### headers
    blocks = re.split(r'\n(?=###\s)', content)

    for block in blocks:
        # Must be a numbered function/skill/pillar header
        header_match = re.match(
            r'###\s+(?:Skill|Function|Pillar)\s+\d+[:\s]+(.+)',
            block.strip(), re.IGNORECASE
        )
        if not header_match:
            continue

        func_name = header_match.group(1).strip()

        # Trigger
        trigger_match = re.search(r'\*\*Trigger[:\*]+\*?\*?\s*(.+?)(?=\n\*\*|\Z)', block)
        trigger = trigger_match.group(1).strip() if trigger_match else ""

        # Examples (split on " / ")
        examples_match = re.search(r'\*\*Examples[:\*]+\*?\*?\s*(.+?)(?=\n\*\*|\Z)', block)
        if examples_match:
            raw = examples_match.group(1).strip()
            # Remove surrounding quotes from each part
            examples = [e.strip().strip('"').strip('"').strip('"').strip()
                        for e in re.split(r'\s*/\s*', raw) if e.strip()]
        else:
            examples = []

        # Approved Language — collect all blockquote lines in the Approved Language section
        approved_match = re.search(
            r'\*\*Approved Language[:\*]+\*?\*?\s*\n+((?:\s*>.*\n?)+)',
            block
        )
        approved_lines = []
        if approved_match:
            for line in approved_match.group(1).split('\n'):
                line = line.strip().lstrip('>').strip().strip('"').strip('"').strip('"')
                if line:
                    approved_lines.append(line)
        approved_language = ' '.join(approved_lines)

        # Forbidden block (lines after **Forbidden:** up to next **)
        forbidden_match = re.search(
            r'\*\*Forbidden[:\*]+\*?\*?\s*\n+((?:.*\n?)*)',
            block
        )
        forbidden = []
        if forbidden_match:
            forbidden = parse_skill_forbidden(forbidden_match.group(1))

        functions.append({
            "name": func_name,
            "trigger": trigger,
            "examples": examples,
            "approved_language": approved_language,
            "forbidden": forbidden,
        })

    return functions


def parse_key_rules(content):
    """Extract Key Rules (Locked) section as bullet list."""
    rules = []
    match = re.search(
        r'#{2,3}\s+Key Rules[^\n]*\n(.*?)(?=\n#{2,}|\Z)',
        content, re.DOTALL | re.IGNORECASE
    )
    if not match:
        return rules
    for line in match.group(1).split('\n'):
        line = line.strip()
        if line.startswith('- ') and '**' in line:
            rule = re.sub(r'\*\*', '', line[2:]).strip()
            if rule:
                rules.append(rule)
    return rules


def process_skill_file(filepath, filename):
    meta = SKILL_META.get(filename, {})
    if not meta:
        print(f"  [SKIP] No metadata for {filename}")
        return []

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    service_area = meta["service_area"]
    store = meta.get("store", "US")
    sub_cat = meta.get("sub_category", "CS Workflow")
    compatible = meta.get("compatible_devices", ["All"])
    default_topic = meta.get("default_topic", "general")
    url = gdrive_url(filename)
    entries = []

    functions = parse_skill_functions(content)
    for func in functions:
        if not func["approved_language"]:
            for rule in func["forbidden"]:
                fe = {
                    "entry_id": make_id(filename + func["name"] + "_forbidden", rule),
                    "source": filename,
                    "service_area": service_area,
                    "sub_category": sub_cat,
                    "store": store,
                    "compatible_devices": compatible,
                    "node": "The Case",
                    "topic": classify_topic(rule, ""),
                    "question": None,
                    "answer": None,
                    "forbidden_response": rule,
                    "confidence": "locked",
                    "generation": "skill_forbidden",
                }
                if url:
                    fe["source_gdrive_url"] = url
                entries.append(fe)
            continue

        answer = func["approved_language"]
        # Primary question: first example if available, else trigger reformatted
        if func["examples"]:
            primary_question = func["examples"][0]
            variants = func["examples"][1:]
        elif func["trigger"]:
            # Make trigger into a question if it's not already
            t = func["trigger"].rstrip('.')
            primary_question = t if '?' in t else t + "?"
            variants = []
        else:
            primary_question = func["name"] + "?"
            variants = []

        topic = classify_topic(primary_question + " " + func["trigger"], answer)
        if topic == "general":
            topic = default_topic

        entry = {
            "entry_id": make_id(filename, primary_question),
            "source": filename,
            "service_area": service_area,
            "sub_category": sub_cat,
            "store": store,
            "compatible_devices": compatible,
            "node": classify_node(topic),
            "topic": topic,
            "function_name": func["name"],
            "trigger": func["trigger"],
            "question": primary_question,
            "question_variants": variants,
            "answer": answer,
            "confidence": "locked",
            "generation": "skill_function",
        }
        if url:
            entry["source_gdrive_url"] = url
        entries.append(entry)

        for variant in variants:
            variant_entry = {
                "entry_id": make_id(filename + "_variant", variant),
                "source": filename,
                "service_area": service_area,
                "sub_category": sub_cat,
                "store": store,
                "compatible_devices": compatible,
                "node": classify_node(topic),
                "topic": topic,
                "function_name": func["name"],
                "trigger": func["trigger"],
                "question": variant,
                "answer": answer,
                "confidence": "locked",
                "generation": "skill_variant",
            }
            if url:
                variant_entry["source_gdrive_url"] = url
            entries.append(variant_entry)

        for rule in func["forbidden"]:
            fe = {
                "entry_id": make_id(filename + func["name"] + "_forbidden", rule),
                "source": filename,
                "service_area": service_area,
                "sub_category": sub_cat,
                "store": store,
                "compatible_devices": compatible,
                "node": "The Case",
                "topic": classify_topic(rule, ""),
                "question": None,
                "answer": None,
                "forbidden_response": rule,
                "confidence": "locked",
                "generation": "skill_forbidden",
            }
            if url:
                fe["source_gdrive_url"] = url
            entries.append(fe)

    for rule in parse_forbidden_block(content):
        fe = {
            "entry_id": make_id(filename + "_file_forbidden", rule),
            "source": filename,
            "service_area": service_area,
            "sub_category": sub_cat,
            "store": store,
            "compatible_devices": compatible,
            "node": "The Case",
            "topic": default_topic,
            "question": None,
            "answer": None,
            "forbidden_response": rule,
            "confidence": "locked",
            "generation": "skill_forbidden",
        }
        if url:
            fe["source_gdrive_url"] = url
        entries.append(fe)

    return entries


# ─────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────

def main():
    all_entries = []
    print("Building Q&A index from CANONICAL KB files...\n")

    # 1. Product files
    print("-- Product Files ------------------------------------------")
    for filename, meta in PRODUCT_META.items():
        filepath = KB_DIR / filename
        if not filepath.exists():
            print(f"  [MISSING] {filename}")
            continue
        entries = process_product_file(filepath, filename)
        all_entries.extend(entries)
        faq = sum(1 for e in entries if e.get("generation") == "faq_extracted")
        rule = sum(1 for e in entries if e.get("generation") == "rule_based")
        forb = sum(1 for e in entries if e.get("generation") == "forbidden_rule")
        print(f"  [OK] {filename}")
        print(f"       FAQ:{faq} | Rule:{rule} | Forbidden:{forb}")

    # 2. Policy files
    print("\n-- Policy Files -------------------------------------------")
    for filename in POLICY_META:
        filepath = KB_DIR / filename
        if not filepath.exists():
            print(f"  [MISSING] {filename}")
            continue
        entries = process_policy_file(filepath, filename)
        all_entries.extend(entries)
        qa = sum(1 for e in entries if e.get("question"))
        forb = sum(1 for e in entries if e.get("forbidden_response"))
        print(f"  [OK] {filename} — Q&A:{qa} | Forbidden:{forb}")

    # 3. Skill files
    print("\n-- Skill Files --------------------------------------------")
    for filename in SKILL_META:
        filepath = SKILLS_DIR / filename
        if not filepath.exists():
            print(f"  [MISSING] {filename}")
            continue
        entries = process_skill_file(filepath, filename)
        all_entries.extend(entries)
        primary = sum(1 for e in entries if e.get("generation") == "skill_function")
        variants = sum(1 for e in entries if e.get("generation") == "skill_variant")
        forb = sum(1 for e in entries if e.get("generation") in ("skill_forbidden",))
        print(f"  [OK] {filename}")
        print(f"       Functions:{primary} | Variants:{variants} | Forbidden:{forb}")

    # Output
    qa_count = sum(1 for e in all_entries if e.get("question"))
    forbidden_count = sum(1 for e in all_entries if e.get("forbidden_response"))

    output = {
        "schema_version": "1.1",
        "generated_by": "build_qa_index.py",
        "generated_date": "2026-05-04",
        "ontology": "June Architecture — The Case | The Device | The Feature",
        "sources": {
            "product_files": len(PRODUCT_META),
            "policy_files": len(POLICY_META),
            "skill_files": len(SKILL_META),
        },
        "total_entries": len(all_entries),
        "qa_entries": qa_count,
        "forbidden_entries": forbidden_count,
        "entries": all_entries,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"OUTPUT: {OUTPUT_FILE}")
    print(f"Total entries:    {output['total_entries']}")
    print(f"Q&A entries:      {output['qa_entries']}")
    print(f"Forbidden rules:  {output['forbidden_entries']}")
    print(f"File size:        {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
