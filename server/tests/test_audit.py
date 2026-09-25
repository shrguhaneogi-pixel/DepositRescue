import sys
from pathlib import Path
import unittest

# Add server directory to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.schemas import AuditRequest, AuditResponse
from app.groq_client import extract_deductions_from_text
from app.audit_engine import audit_deductions
from app.main import audit_landlord_statement

class TestDepositRescueAudit(unittest.TestCase):
    def test_mock_deduction_audit(self):
        sample_text = (
            "Move-Out Inspection Deductions:\n"
            "1. Wall repainting: $300.00\n"
            "2. Routine carpet cleaning: $150.00\n"
            "3. Broken kitchen drawer fix: $200.00"
        )
        
        request = AuditRequest(text=sample_text)
        response: AuditResponse = audit_landlord_statement(request)
        
        print("\n--- Test Audit Response ---")
        print(f"Raw Total: ${response.raw_total}")
        print(f"Illegal Total: ${response.illegal_total}")
        print(f"Allowed Total: ${response.allowed_total}")
        print(f"Statutory Recovery: ${response.statutory_recovery}")
        print(f"Summary: {response.summary}")
        
        # Verify Pydantic schema contract & math logic
        self.assertEqual(response.raw_total, 650.0)
        self.assertEqual(response.illegal_total, 450.0) # $300 painting + $150 cleaning
        self.assertEqual(response.allowed_total, 200.0) # $200 drawer fix
        self.assertEqual(response.statutory_recovery, 900.0) # 2x of $450
        self.assertTrue(len(response.items) >= 3)
        self.assertTrue(response.items[0].is_illegal)
        self.assertTrue(response.items[1].is_illegal)
        self.assertFalse(response.items[2].is_illegal)

if __name__ == "__main__":
    unittest.main()
