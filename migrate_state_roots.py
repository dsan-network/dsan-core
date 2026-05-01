import json
import os
import sys
from copy import deepcopy

from dsan.core.replay import replay_ledger


def migrate_ledger_state_roots(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ledger file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        original_ledger = json.load(f)

    if not isinstance(original_ledger, list):
        raise ValueError("Ledger must be a JSON list")

    migrated_ledger = []
    changed = 0

    for entry in original_ledger:
        entry_copy = deepcopy(entry)
        migrated_ledger.append(entry_copy)

        progressive_root = replay_ledger(migrated_ledger)

        if entry_copy.get("state_root") != progressive_root:
            entry_copy["state_root"] = progressive_root
            changed += 1

    backup_path = path + ".bak"

    if not os.path.exists(backup_path):
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(original_ledger, f, indent=2, ensure_ascii=False)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(migrated_ledger, f, indent=2, ensure_ascii=False)

    print("migration_status: OK")
    print("ledger_file:", path)
    print("backup_file:", backup_path)
    print("entries_total:", len(original_ledger))
    print("entries_updated:", changed)

    for i, entry in enumerate(migrated_ledger, start=1):
        print(f"entry_{i}_state_root:", entry.get("state_root"))

    if migrated_ledger:
        print("final_state_root:", migrated_ledger[-1]["state_root"])


if __name__ == "__main__":
    ledger_file = sys.argv[1] if len(sys.argv) > 1 else "ledger_node1.json"
    migrate_ledger_state_roots(ledger_file)