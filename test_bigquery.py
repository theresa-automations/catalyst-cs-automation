from google.cloud import bigquery
from google.api_core.exceptions import Conflict
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json'

PROJECT_ID = 'cs-mcp-gateway'
DATASET_ID = 'catalyst_cs_accuracy'

client = bigquery.Client(project=PROJECT_ID)

# --------------------------------------------------
# STEP 1 — Create dataset (skip if already exists)
# --------------------------------------------------
dataset_ref = bigquery.Dataset(f'{PROJECT_ID}.{DATASET_ID}')
dataset_ref.location = 'US'
try:
    client.create_dataset(dataset_ref)
    print(f'Dataset {DATASET_ID}: created')
except Conflict:
    print(f'Dataset {DATASET_ID}: already exists')

# --------------------------------------------------
# STEP 2 — Create draft_log table
# --------------------------------------------------
draft_log_schema = [
    bigquery.SchemaField('draft_id',        'STRING',    mode='REQUIRED'),
    bigquery.SchemaField('created_at',      'TIMESTAMP', mode='REQUIRED'),
    bigquery.SchemaField('email_category',  'STRING'),
    bigquery.SchemaField('sender_email',    'STRING'),
    bigquery.SchemaField('subject',         'STRING'),
    bigquery.SchemaField('claude_draft',    'STRING'),
    bigquery.SchemaField('shopify_order_id','STRING'),
    bigquery.SchemaField('store',           'STRING'),
]
draft_table_ref = f'{PROJECT_ID}.{DATASET_ID}.draft_log'
try:
    client.create_table(bigquery.Table(draft_table_ref, schema=draft_log_schema))
    print('Table draft_log: created')
except Conflict:
    print('Table draft_log: already exists')

# --------------------------------------------------
# STEP 3 — Create accuracy_log table
# --------------------------------------------------
accuracy_log_schema = [
    bigquery.SchemaField('draft_id',       'STRING',    mode='REQUIRED'),
    bigquery.SchemaField('reconciled_at',  'TIMESTAMP', mode='REQUIRED'),
    bigquery.SchemaField('final_sent',     'STRING'),
    bigquery.SchemaField('edit_distance',  'INTEGER'),
    bigquery.SchemaField('total_chars',    'INTEGER'),
    bigquery.SchemaField('edit_pct',       'FLOAT'),
    bigquery.SchemaField('accuracy_score', 'FLOAT'),
    bigquery.SchemaField('result',         'STRING'),
    bigquery.SchemaField('semantic_match', 'BOOLEAN'),
    bigquery.SchemaField('agent_id',       'STRING'),
]
accuracy_table_ref = f'{PROJECT_ID}.{DATASET_ID}.accuracy_log'
try:
    client.create_table(bigquery.Table(accuracy_table_ref, schema=accuracy_log_schema))
    print('Table accuracy_log: created')
except Conflict:
    print('Table accuracy_log: already exists')

# --------------------------------------------------
# STEP 4 — Insert test row into draft_log
# --------------------------------------------------
sql_draft = f"""
INSERT INTO `{PROJECT_ID}.{DATASET_ID}.draft_log`
(draft_id, created_at, email_category, sender_email, subject, claude_draft, shopify_order_id, store)
VALUES
('test-001', TIMESTAMP('2026-03-25T10:00:00Z'), 'CATALYST_US_WISMO', 'test@example.com',
 'Where is my order?', 'Your order is on its way.', '1234', 'catalystcase')
"""
job = client.query(sql_draft)
job.result()
print('draft_log insert: OK')

# --------------------------------------------------
# STEP 5 — Insert test row into accuracy_log
# --------------------------------------------------
sql_accuracy = f"""
INSERT INTO `{PROJECT_ID}.{DATASET_ID}.accuracy_log`
(draft_id, reconciled_at, final_sent, edit_distance, total_chars, edit_pct, accuracy_score, result, semantic_match, agent_id)
VALUES
('test-001', TIMESTAMP('2026-03-25T10:30:00Z'), 'Your order is on its way.',
 0, 26, 0.0, 100.0, 'PERFECT', TRUE, 'cs@catalystcase.com')
"""
job2 = client.query(sql_accuracy)
job2.result()
print('accuracy_log insert: OK')

# --------------------------------------------------
# STEP 6 — Query both tables back
# --------------------------------------------------
print('\n--- draft_log ---')
for row in client.query(f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.draft_log`').result():
    print(dict(row))

print('\n--- accuracy_log ---')
for row in client.query(f'SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.accuracy_log`').result():
    print(dict(row))

print('\nDone.')
