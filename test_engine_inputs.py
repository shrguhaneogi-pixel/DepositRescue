import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from api.core.schemas import AuditRequest
from api.index import audit_landlord_statement
from record_full_demo import main as record_demo_main

inputs = [
    "Landlord says: $400 for painting, $150 for routine carpet cleaning, and $200 for a broken window.",
    "The landlord was just being mean",
    "Deducting $50 for leaving dust on the ceiling fan, $500 for a hole I punched in the wall, and $200 for normal wear on the hardwood floors."
]

for idx, inp in enumerate(inputs, 1):
    print(f"\n--- Input {idx} ---")
    print(inp)
    req = AuditRequest(text=inp)
    res = audit_landlord_statement(req)
    print("Raw total:", res.raw_total)
    print("Illegal total:", res.illegal_total)
    print("Allowed total:", res.allowed_total)
    print("Statutory recovery:", res.statutory_recovery)
    print("Items count:", len(res.items))
    for item in res.items:
        print(f"  - {item.item_name}: ${item.original_cost} (Illegal: {item.is_illegal}) -> {item.explanation}")

print("\n--- Starting Full Screen Recording & Audio Synthesis ---", flush=True)
asyncio.run(record_demo_main())
