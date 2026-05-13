"""
Test: parse actual batchexecute response format and extract conversations.
"""
import json, re, sys
from pathlib import Path

SCRIPT_DIR = Path("E:/MyCodeProjects/02-审计工具")

def strip_batcherror(body: str) -> str:
    return re.sub(r"^\)\]}'\n?", "", body)

# Load the capture file
capture = json.load(open(SCRIPT_DIR / "gemini_rpc_capture.json", "r", encoding="utf-8"))

# Get MaZiqc sample
maziqc_samples = capture["rpc_samples"].get("MaZiqc", [])
print(f"MaZiqc samples: {len(maziqc_samples)}")

for i, sample in enumerate(maziqc_samples):
    print(f"\n{'='*60}")
    print(f"Sample {i+1}: raw prefix: {repr(sample[:50])}")
    cleaned = strip_batcherror(sample)
    print(f"After strip: {repr(cleaned[:80])}")

    try:
        data = json.loads(cleaned)
        print(f"JSON parse OK: type={type(data).__name__}, len={len(data) if isinstance(data, list) else 'N/A'}")
        print(f"Top-level structure:")
        if isinstance(data, list):
            for j, item in enumerate(data):
                if isinstance(item, list):
                    print(f"  [{j}]: list of {len(item)}")
                    if len(item) >= 3:
                        print(f"    [0]: {item[0]}")
                        print(f"    [1]: {item[1]}")
                        third = item[2]
                        if isinstance(third, str):
                            print(f"    [2]: string, len={len(third)}, starts with: {third[:80]}...")
                            # Try parsing third as JSON
                            try:
                                inner = json.loads(third)
                                print(f"    Inner JSON: type={type(inner).__name__}")
                                if isinstance(inner, list):
                                    print(f"    Inner list len={len(inner)}")
                                    for k, val in enumerate(inner):
                                        print(f"      [{k}]: {type(val).__name__} = {str(val)[:80]}")
                            except json.JSONDecodeError as e:
                                print(f"    Inner JSON parse FAILED: {e}")
                        else:
                            print(f"    [2]: {type(third).__name__} = {str(third)[:80]}")
                elif isinstance(item, dict):
                    print(f"  [{j}]: dict with keys {list(item.keys())[:5]}")
                else:
                    print(f"  [{j}]: {type(item).__name__} = {str(item)[:80]}")
        print(f"\nFull response structure:")
        print(json.dumps(data, ensure_ascii=False)[:2000])
    except json.JSONDecodeError as e:
        print(f"JSON parse FAILED: {e}")
        print(f"Trying to clean further...")
        # Try finding first [ after a known pattern
        m = re.search(r'\n\d+\n(\[.*)', cleaned, re.DOTALL)
        if m:
            cleaned2 = m.group(1)
            print(f"After size prefix strip: {repr(cleaned2[:80])}")
            try:
                data2 = json.loads(cleaned2)
                print(f"JSON parse OK! type={type(data2).__name__}")
                print(json.dumps(data2, ensure_ascii=False)[:2000])
            except json.JSONDecodeError as e2:
                print(f"Still failed: {e2}")
