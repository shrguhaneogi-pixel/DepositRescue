import sys
from pathlib import Path
import unittest

# Add root directory to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.schemas import AuditRequest, AuditResponse
from api.index import audit_landlord_statement

class TestDepositRescueVercelAudit(unittest.TestCase):
    def test_mock_deduction_audit(self):
        sample_text = (
            "Move-Out Inspection Deductions:\n"
            "1. Wall repainting: $300.00\n"
            "2. Routine carpet cleaning: $150.00\n"
            "3. Broken kitchen drawer fix: $200.00"
        )
        
        request = AuditRequest(text=sample_text)
        response: AuditResponse = audit_landlord_statement(request)
        
        print("\n--- Vercel API Test Audit Response ---")
        print(f"Raw Total: ${response.raw_total}")
        print(f"Illegal Total: ${response.illegal_total}")
        print(f"Allowed Total: ${response.allowed_total}")
        print(f"Statutory Recovery: ${response.statutory_recovery}")
        print(f"Summary: {response.summary}")
        
        # Verify Pydantic schema contract & math logic
        self.assertEqual(response.raw_total, 650.0)
        self.assertEqual(response.illegal_total, 450.0)
        self.assertEqual(response.allowed_total, 200.0)
        self.assertEqual(response.statutory_recovery, 900.0)
        self.assertTrue(len(response.items) >= 3)

if __name__ == "__main__":
    unittest.main()
