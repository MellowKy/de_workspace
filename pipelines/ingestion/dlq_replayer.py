import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pyarrow as pa
from deltalake import write_deltalake
from pydantic import ValidationError
from governance.contracts.order_event import OrderContract

DLQ_PATH = PROJECT_ROOT / "data/dlq/orders_dlq.jsonl"
BRONZE_DELTA_PATH = PROJECT_ROOT / "data/bronze/orders_delta"

def replay_dlq_records(remediation_map: dict):
    if not DLQ_PATH.exists() or DLQ_PATH.stat().st_size == 0:
        print("DLQ is empty. No records to replay.")
        return

    with open(DLQ_PATH, "r") as f:
        dlq_entries = [json.loads(line) for line in f if line.strip()]

    remaining_dlq = []
    remediated_dicts = []

    for entry in dlq_entries:
        raw_payload = entry.get("raw_payload", {})
        evt_id = raw_payload.get("event_id")

        if evt_id in remediation_map:
            patched_payload = raw_payload | remediation_map[evt_id]
            try:
                validated_event = OrderContract(**patched_payload)
                record_dict = validated_event.model_dump()
                record_dict["timestamp"] = record_dict["timestamp"].isoformat()
                remediated_dicts.append(record_dict)
                print(f"Successfully remediated event: {evt_id}")
            except (ValidationError, TypeError, ValueError) as err:
                print(f"Remediation failed for event {evt_id}: {err}")
                entry["error"] = f"Remediation Failure: {err!s}"
                remaining_dlq.append(entry)
        else:
            remaining_dlq.append(entry)

    if remediated_dicts:
        arrow_table = pa.Table.from_pylist(remediated_dicts)
        write_deltalake(
            str(BRONZE_DELTA_PATH),
            arrow_table,
            mode="append"
        )

    with open(DLQ_PATH, "w") as f:
        for entry in remaining_dlq:
            f.write(json.dumps(entry) + "\n")

    print(f"\nSummary: {len(remediated_dicts)} event(s) replayed to Bronze Delta Lake. {len(remaining_dlq)} event(s) remain in DLQ.")

if __name__ == "__main__":
    remediation_patches = {
        "evt-ERR": {
            "timestamp": "2026-10-17T01:30:00Z",
            "amount": 20.00,
            "currency": "USD"
        }
    }
    replay_dlq_records(remediation_patches)
