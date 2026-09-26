import sys
from pathlib import Path
import unittest

# Add root directory to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.schemas import AuditRequest, AuditResponse
from api.core.groq_client import fallback_regex_extractor
from api.index import audit_landlord_statement
from fastapi import HTTPException

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
        
        # Verify Pydantic schema contract & math logic
        self.assertEqual(response.raw_total, 650.0)
        self.assertEqual(response.illegal_total, 450.0)
        self.assertEqual(response.allowed_total, 200.0)
        self.assertEqual(response.statutory_recovery, 900.0)
        self.assertTrue(len(response.items) >= 3)

    def test_comma_formatted_amounts(self):
        sample_text = (
            "1. Interior repainting: $1,200.00\n"
            "2. Replacement window pane: $450.00"
        )
        request = AuditRequest(text=sample_text)
        response: AuditResponse = audit_landlord_statement(request)
        
        self.assertEqual(response.raw_total, 1650.0)
        self.assertEqual(response.illegal_total, 1200.0)
        self.assertEqual(response.allowed_total, 450.0)
        self.assertEqual(response.statutory_recovery, 2400.0)

    def test_empty_or_whitespace_text_validation(self):
        with self.assertRaises(HTTPException) as cm:
            audit_landlord_statement(AuditRequest(text="     "))
        self.assertEqual(cm.exception.status_code, 400)

    def test_fallback_regex_extractor_directly(self):
        sample_text = "Touch up paint - $75.50\nScuff marks - $50.00"
        extracted = fallback_regex_extractor(sample_text)
        self.assertEqual(len(extracted.deductions), 2)
        self.assertEqual(extracted.deductions[0].cost, 75.50)

    def test_all_valid_tenant_damage_charges(self):
        sample_text = (
            "1. Destroyed bathroom mirror: $180.00\n"
            "2. Broken front door lock: $120.00"
        )
        request = AuditRequest(text=sample_text)
        response: AuditResponse = audit_landlord_statement(request)
        self.assertEqual(response.raw_total, 300.0)
        self.assertEqual(response.illegal_total, 0.0)
        self.assertEqual(response.allowed_total, 300.0)
        self.assertEqual(response.statutory_recovery, 0.0)

    def test_exact_decimal_rounding_sum(self):
        sample_text = (
            "1. Deep cleaning: $100.33\n"
            "2. Wall scuff repair: $50.33\n"
            "3. Plumbing damage: $49.34"
        )
        request = AuditRequest(text=sample_text)
        response: AuditResponse = audit_landlord_statement(request)
        item_sum = round(sum(item.original_cost for item in response.items), 2)
        self.assertEqual(response.raw_total, item_sum)
        self.assertEqual(response.raw_total, 200.00)

    def test_alternative_formatting_and_usd_prefix(self):
        sample_text = "Interior paint USD 250.00\nBroken window: $150.00"
        extracted = fallback_regex_extractor(sample_text)
        self.assertEqual(len(extracted.deductions), 2)
        self.assertEqual(extracted.deductions[0].item_name, "Interior paint")
        self.assertEqual(extracted.deductions[0].cost, 250.0)

if __name__ == "__main__":
    unittest.main()
