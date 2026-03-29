"""One-time schema migration: add thread_id, message_id, status to draft_log."""
from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'C:\Users\pc\gdrive-mcp-server\credentials\bigquery-service-account.json'

client = bigquery.Client(project='cs-mcp-gateway')
table_ref = client.dataset('catalyst_cs_accuracy').table('draft_log')
table = client.get_table(table_ref)

print("Current schema:")
for field in table.schema:
    print(f"  {field.name} ({field.field_type})")

existing = {f.name for f in table.schema}
new_fields = []

if 'thread_id' not in existing:
    new_fields.append(bigquery.SchemaField('thread_id', 'STRING', mode='NULLABLE',
        description='Gmail thread ID — stable across draft to send lifecycle'))
if 'message_id' not in existing:
    new_fields.append(bigquery.SchemaField('message_id', 'STRING', mode='NULLABLE',
        description='Gmail message ID of the draft — PRIMARY reconciler match key'))
if 'status' not in existing:
    new_fields.append(bigquery.SchemaField('status', 'STRING', mode='NULLABLE',
        description='PENDING / RECONCILED / ABANDONED'))

if not new_fields:
    print("\nAll fields already exist. No changes needed.")
else:
    table.schema = table.schema + new_fields
    client.update_table(table, ['schema'])
    print(f"\nAdded {len(new_fields)} field(s): {[f.name for f in new_fields]}")

    table = client.get_table(table_ref)
    print("\nUpdated schema:")
    for field in table.schema:
        print(f"  {field.name} ({field.field_type})")

print("\nDone.")
