import unittest
from services.masking_service import mask_digits
from services.quality_gate import run_all_checks


class TestMaskingAndQualityGate(unittest.TestCase):
    def test_mask_digits_4_plus(self):
        text = "My account is 12345678 and phone is 9876"
        masked, occurred = mask_digits(text)
        self.assertTrue(occurred)
        self.assertNotIn("12345678", masked)
        self.assertIn("XXXXXXXX", masked)
        self.assertNotIn("9876", masked)
        self.assertIn("XXXX", masked)

    def test_mask_digits_short_intact(self):
        text = "SIP date is 5 and amount is 500"
        masked, occurred = mask_digits(text)
        self.assertFalse(occurred)
        self.assertEqual(masked, text)

    def test_quality_gate_pass(self):
        response = {
            "confidence": 0.85,
            "fact_ids": ["K1", "K2"],
            "explanation": "You can change your SIP date or amount using the Edit SIP option in Groww.",
            "evidence_quote": "salary 10 tarikh ko aati hai",
        }
        input_text = "salary 10 tarikh ko aati hai par SIP 5 ko kat jaata hai"
        result = run_all_checks(response, input_text)
        self.assertTrue(result["checked"])
        self.assertEqual(len(result["failures"]), 0)

    def test_quality_gate_banned_word(self):
        response = {
            "confidence": 0.9,
            "fact_ids": ["K1"],
            "explanation": "Hurry, act now before it's too late to change your SIP!",
            "evidence_quote": "salary 10 tarikh",
        }
        input_text = "salary 10 tarikh"
        result = run_all_checks(response, input_text)
        self.assertFalse(result["checked"])
        self.assertTrue(any("banned_word" in f for f in result["failures"]))

    def test_quality_gate_fund_name_blocked(self):
        response = {
            "confidence": 0.9,
            "fact_ids": ["K1"],
            "explanation": "Switch your investment to HDFC Smallcap fund instead.",
            "evidence_quote": "salary 10",
        }
        input_text = "salary 10"
        result = run_all_checks(response, input_text)
        self.assertFalse(result["checked"])
        self.assertIn("fund_or_stock_name_detected", result["failures"])

    def test_quality_gate_ungrounded_fact(self):
        response = {
            "confidence": 0.9,
            "fact_ids": ["K99"],
            "explanation": "Custom action",
            "evidence_quote": "salary 10",
        }
        input_text = "salary 10"
        result = run_all_checks(response, input_text)
        self.assertFalse(result["checked"])
        self.assertTrue(any("unknown_fact_ids" in f for f in result["failures"]))

    def test_quality_gate_evidence_quote_mismatch(self):
        response = {
            "confidence": 0.9,
            "fact_ids": ["K1"],
            "explanation": "You can change date",
            "evidence_quote": "non-existent text here",
        }
        input_text = "salary 10 tarikh"
        result = run_all_checks(response, input_text)
        self.assertFalse(result["checked"])
        self.assertIn("evidence_quote_not_in_input", result["failures"])


if __name__ == "__main__":
    unittest.main()
