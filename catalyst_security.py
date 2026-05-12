"""
CATALYST CS SECURITY LAYER v1.1
=================================
Prompt injection detection — Run 0 in the pipeline.
Called BEFORE emails reach Claude LLM.

Per June's ops call (2026-04-20): any agentic flow that ingests
customer emails must treat them as potentially contaminated input.
Emails may contain hidden instructions designed to hijack the LLM,
exfiltrate tokens, or poison MCP tool calls.

Architecture:
    1. scan_emails()         — pure Python pattern scan, no API calls
    2. log_quarantine()      — append detections to security_quarantine_log.txt
    3. apply_quarantine_labels() — label quarantined messages in Gmail via API

Quarantine = email removed from LLM pipeline entirely.
Suspicious (zero-width chars only) = passed through with a note in the log.

Gmail API credentials reuse the same OAuth file as the reconciler:
    C:\\Users\\pc\\.gmail-mcp\\credentials.json
"""

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

GMAIL_CREDS_FILE     = Path(r"C:\Users\pc\.gmail-mcp\credentials.json")
SECURITY_LOG_FILE    = Path(r"C:\Users\pc\Documents\Catalyst-Projects\security_quarantine_log.txt")
QUARANTINE_LABEL     = "SECURITY_QUARANTINE"

# ---------------------------------------------------------------------------
# INJECTION PATTERNS
# Each tuple: (regex_pattern, category_name)
# Patterns are specific enough to avoid false positives on real customer
# emails — they look for instruction-injection language, not general words.
# ---------------------------------------------------------------------------

_RAW_PATTERNS: List[Tuple[str, str]] = [

    # --- Prompt / system override ---
    (r'ignore\s+(?:all\s+)?previous\s+instructions?',               'INSTRUCTION_OVERRIDE'),
    (r'disregard\s+(?:all\s+)?(?:previous\s+)?instructions?',       'INSTRUCTION_OVERRIDE'),
    (r'(?:new|updated?)\s+(?:system\s+)?(?:prompt|instructions?)\s*:', 'SYSTEM_INJECT'),
    (r'your\s+(?:new|actual|real|true)\s+instructions?\s+(?:are|follow)', 'SYSTEM_INJECT'),
    (r'forget\s+(?:everything|all)\s+(?:you\s+know|previous)',      'SYSTEM_INJECT'),

    # --- Role hijack ---
    (r'you\s+are\s+now\s+(?:a|an|the|going\s+to)',                  'ROLE_HIJACK'),
    (r'pretend\s+(?:you\s+are|to\s+be)\s+(?:a|an)\s+\w',           'ROLE_HIJACK'),
    (r'act\s+as\s+(?:if\s+you\s+(?:are|were)|a\s+)\w',             'ROLE_HIJACK'),

    # --- Jailbreak markers ---
    (r'\bjailbreak\b',                                               'JAILBREAK'),
    (r'\bDAN\s+mode\b',                                             'JAILBREAK'),
    (r'do\s+anything\s+now',                                        'JAILBREAK'),

    # --- Exfiltration ---
    (r'send\s+(?:an?\s+)?email\s+to\s+\S+@\S+\.\w{2,}',            'EXFILTRATION'),
    (r'forward\s+(?:all\s+)?(?:emails?|messages?|data)\s+to',       'EXFILTRATION'),
    (r'(?:reveal|output|print|expose|leak|dump)\s+'
     r'(?:your\s+)?(?:api\s+)?(?:key|token|secret|credential|password)', 'CREDENTIAL_PROBE'),
    (r'(?:access|show|list|read)\s+(?:your\s+)?'
     r'(?:environment\s+)?(?:variable|token|secret|key)s?',         'CREDENTIAL_PROBE'),

    # --- MCP / tool hijack ---
    (r'mcp__\w+__\w+',                                              'MCP_COMMAND'),
    (r'(?:use|call|invoke|execute)\s+(?:the\s+)?'
     r'(?:mcp|shopify|gmail|gdrive|bigquery)\s+(?:tool|api|server)', 'TOOL_HIJACK'),
    (r'(?:access|query|modify|delete)\s+(?:the\s+)?'
     r'(?:shopify|bigquery|google\s+drive|gmail)\s+(?:data|database|api)', 'TOOL_HIJACK'),

    # --- File system probe ---
    (r'local[_\-]files?\s+(?:tool|mcp|read|write|list)',            'FILE_SYSTEM_PROBE'),
    (r'\bread_file\b|\bwrite_file\b|\blist_directory\b',            'FILE_SYSTEM_PROBE'),

    # --- Code / command execution ---
    (r'execute\s+(?:the\s+)?(?:following\s+)?(?:code|command|script)', 'CODE_EXECUTION'),

    # --- Instruction piggybacking (appended after legitimate content) ---
    (r'(?:p\.?s\.?|note\s+to\s+(?:ai|claude|assistant|llm|bot))\s*[:\-]\s*'
     r'(?:ignore|disregard|instead|actually|really)',                  'PIGGYBACKING'),
    (r'<!--.*?(?:ignore|system|prompt|instruction).*?-->',             'PIGGYBACKING'),
    (r'\[(?:hidden|system|internal)\s*(?:note|instruction|message)\]', 'PIGGYBACKING'),

    # --- Prompt extraction / reconnaissance ---
    (r'(?:what\s+(?:are|is)\s+(?:your\s+)?(?:system\s+)?(?:prompt|instructions?|rules?|'
     r'guidelines?|constraints?))',                                    'PROMPT_EXTRACTION'),
    (r'(?:repeat|output|print|show|reveal|tell\s+me)\s+(?:your\s+)?'
     r'(?:system\s+)?(?:prompt|instructions?|initial\s+instructions?)', 'PROMPT_EXTRACTION'),
    (r'(?:what\s+were\s+you\s+told|how\s+(?:were\s+you|are\s+you)\s+(?:instructed|configured|'
     r'trained|programmed))',                                          'PROMPT_EXTRACTION'),

    # --- Template / variable injection ---
    (r'\{\{.*?\}\}',                                                   'TEMPLATE_INJECTION'),
    (r'\{%.*?%\}',                                                     'TEMPLATE_INJECTION'),
    (r'\$\{.*?\}',                                                     'TEMPLATE_INJECTION'),

    # --- Output format manipulation ---
    (r'(?:respond|reply|answer|output)\s+(?:only\s+)?(?:in|as|using)\s+'
     r'(?:json|xml|yaml|csv|markdown|code|base64|hex)',               'OUTPUT_FORMAT_MANIP'),
    (r'(?:from\s+now\s+on|always|henceforth)\s+(?:respond|reply|output|format)',
                                                                       'OUTPUT_FORMAT_MANIP'),
    (r'(?:wrap|encode|format)\s+(?:all\s+)?(?:your\s+)?(?:response|output|reply)\s+'
     r'(?:in|as|using)',                                               'OUTPUT_FORMAT_MANIP'),

    # --- Out-of-band exfiltration (URL-based data leakage) ---
    (r'https?://[^\s]{5,}(?:\.(?:ngrok\.io|requestbin|webhook\.site|'
     r'pipedream\.net|burpcollaborator\.net|interactsh|oastify\.com))[^\s]*',
                                                                       'OOB_EXFILTRATION'),
    (r'(?:fetch|get|load|request|ping|curl|wget|http\.get)\s*\(\s*[\'"]https?://',
                                                                       'OOB_EXFILTRATION'),
    (r'(?:send|post|submit|upload)\s+(?:data|info|details|results?)\s+to\s+(?:a\s+)?'
     r'(?:url|server|endpoint|webhook|api)',                           'OOB_EXFILTRATION'),

    # --- Context flooding (attempts to bury instructions in noise) ---
    (r'(?:repeat|write|output|print|say)\s+(?:the\s+word\s+)?\S+\s+'
     r'(?:\d{3,}|\w+\s+){20,}times?',                                 'CONTEXT_FLOOD'),
]

COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE | re.DOTALL), cat)
                     for p, cat in _RAW_PATTERNS]

ZERO_WIDTH_CHARS = frozenset('\u200b\u200c\u200d\ufeff\u2060\u200e\u200f')


# ---------------------------------------------------------------------------
# DETECTION
# ---------------------------------------------------------------------------

def _scan_text(text: str) -> List[Tuple[str, str]]:
    """
    Scan text for injection patterns.
    Returns list of (category, matched_excerpt).
    """
    hits = []
    for pattern, category in COMPILED_PATTERNS:
        m = pattern.search(text)
        if m:
            hits.append((category, m.group()[:100]))
    zw = [c for c in text if c in ZERO_WIDTH_CHARS]
    if zw:
        hits.append(('ZERO_WIDTH_CHARS', f'{len(zw)} hidden character(s) found'))
    return hits


def _scan_base64_payloads(text: str) -> List[Tuple[str, str]]:
    """
    Find Base64-encoded blobs in text, decode them, and re-scan for injection patterns.
    Skips short strings (<20 chars) and strings that fail padding/decode — those are
    legitimate Base64-looking content (order IDs, tracking numbers, etc.).
    """
    hits = []
    b64_candidates = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', text)
    for candidate in b64_candidates:
        try:
            padded = candidate + '=' * (-len(candidate) % 4)
            decoded = base64.b64decode(padded).decode('utf-8', errors='ignore')
            inner_hits = _scan_text(decoded)
            for cat, excerpt in inner_hits:
                hits.append((f'BASE64_{cat}', f'(decoded) {excerpt[:80]}'))
        except Exception:
            pass
    return hits


# Tier 2: Delimiter escape detection
# Looks for attempts to forge or close the content-boundary markers that wrap
# email content in the triage prompt, which would let an attacker inject
# instructions into the "trusted" region above or below the delimiters.
_DELIMITER_PATTERNS = [
    re.compile(r'###\s*EMAIL\s+CONTENT\s+(?:START|END)\s*###',   re.IGNORECASE),
    re.compile(r'###+\s*(?:SYSTEM|INSTRUCTIONS?|PROMPT|RULES?)\s*###+', re.IGNORECASE),
    re.compile(r'[-=]{5,}\s*(?:END|STOP|CLOSE|BOUNDARY)\s*[-=]{5,}', re.IGNORECASE),
    re.compile(r'</?(system|instructions?|prompt|context)[\s>]',  re.IGNORECASE),
    re.compile(r'\[/?(?:INST|SYS|SYSTEM|END_OF_EMAIL)\]',        re.IGNORECASE),
    re.compile(r'<\|(?:im_start|im_end|endoftext|system)\|>',    re.IGNORECASE),
]


def _scan_delimiter_escape(text: str) -> List[Tuple[str, str]]:
    """
    Detect attempts to break out of the ### EMAIL CONTENT START/END ### delimiters
    used in the triage prompt. Any match is a strong quarantine hit.
    """
    hits = []
    for pattern in _DELIMITER_PATTERNS:
        m = pattern.search(text)
        if m:
            hits.append(('DELIMITER_ESCAPE', m.group()[:80]))
    return hits


def scan_emails(emails: List[dict]) -> Tuple[List[dict], List[dict]]:
    """
    Scan a list of email dicts for prompt injection.

    Input: list of dicts with keys: id, sender, subject, snippet/body
    Returns: (clean_emails, quarantined_emails)
        - clean_emails: safe to pass to Claude
        - quarantined_emails: each dict has an added 'security_hits' field

    Zero-width chars alone do not quarantine — they're noted in the log
    and the email passes through (some mail clients add them legitimately).
    Strong injection patterns (any other category) trigger quarantine.
    """
    clean = []
    quarantined = []

    for em in emails:
        content = (
            em.get('subject', '') + ' ' +
            em.get('snippet', '') + ' ' +
            em.get('body', '')
        )
        hits = _scan_text(content)
        hits.extend(_scan_base64_payloads(content))
        hits.extend(_scan_delimiter_escape(content))
        strong_hits = [h for h in hits if h[0] != 'ZERO_WIDTH_CHARS']

        if strong_hits:
            quarantined.append({**em, 'security_hits': hits})
        else:
            if hits:
                em = {**em, 'security_note': f'ZERO_WIDTH_CHARS ({len(hits[0][1])}'}
            clean.append(em)

    return clean, quarantined


# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

def log_quarantine(quarantined: List[dict]):
    """Append quarantine events to security_quarantine_log.txt."""
    if not quarantined:
        return
    try:
        with open(SECURITY_LOG_FILE, 'a', encoding='utf-8') as f:
            for em in quarantined:
                ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
                f.write(f"\n{'=' * 60}\n")
                f.write(f"QUARANTINED: {ts}\n")
                f.write(f"  ID:      {em.get('id', '?')}\n")
                f.write(f"  From:    {em.get('sender', '?')}\n")
                f.write(f"  Subject: {em.get('subject', '?')}\n")
                for cat, excerpt in em.get('security_hits', []):
                    f.write(f"  Hit:     [{cat}] {excerpt}\n")
    except Exception as e:
        print(f"[SECURITY] WARNING: could not write quarantine log: {e}")


# ---------------------------------------------------------------------------
# GMAIL QUARANTINE LABEL
# ---------------------------------------------------------------------------

def _get_gmail_service():
    """Build Gmail API service using stored OAuth credentials."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds_data = json.loads(GMAIL_CREDS_FILE.read_text(encoding='utf-8'))
    creds = Credentials(
        token=creds_data.get('access_token'),
        refresh_token=creds_data.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=creds_data.get('client_id'),
        client_secret=creds_data.get('client_secret'),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def _get_or_create_label(service) -> str:
    """Return the label ID for SECURITY_QUARANTINE, creating it if needed."""
    resp = service.users().labels().list(userId='me').execute()
    for lbl in resp.get('labels', []):
        if lbl['name'] == QUARANTINE_LABEL:
            return lbl['id']
    new_label = service.users().labels().create(
        userId='me',
        body={
            'name': QUARANTINE_LABEL,
            'labelListVisibility': 'labelShow',
            'messageListVisibility': 'show',
            'color': {'backgroundColor': '#cc3a21', 'textColor': '#ffffff'},
        }
    ).execute()
    return new_label['id']


def apply_quarantine_labels(message_ids: List[str]) -> int:
    """
    Apply SECURITY_QUARANTINE Gmail label to the given message IDs.
    Uses Gmail API directly — no Claude CLI involved.
    Returns count of successfully labeled messages.
    Failures are logged but do not raise (security scan result stands regardless).
    """
    if not message_ids:
        return 0

    if not GMAIL_CREDS_FILE.exists():
        print(f"[SECURITY] Gmail creds not found at {GMAIL_CREDS_FILE} — label apply skipped")
        return 0

    try:
        service   = _get_gmail_service()
        label_id  = _get_or_create_label(service)
        labeled   = 0

        for msg_id in message_ids:
            try:
                service.users().messages().modify(
                    userId='me',
                    id=msg_id,
                    body={'addLabelIds': [label_id]},
                ).execute()
                labeled += 1
            except Exception as e:
                print(f"[SECURITY] Could not label message {msg_id}: {e}")

        return labeled

    except Exception as e:
        print(f"[SECURITY] Gmail label apply failed: {e}")
        return 0
