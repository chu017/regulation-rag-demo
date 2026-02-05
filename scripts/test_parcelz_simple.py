"""
Simple test - just call the function directly.
"""
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from scripts.parcelz_property_api import get_property_info_from_address

# Test with a real address
address = "123 Main St, San Francisco, CA 94102"
print(f"Testing address: {address}\n")

result = get_property_info_from_address(address)
print("\nResult:")
print(json.dumps(result, indent=2))
