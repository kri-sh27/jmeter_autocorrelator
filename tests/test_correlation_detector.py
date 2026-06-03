"""
Correlation Detection Verification Suite.
Validates extraction accuracies across various systemic payload patterns.
"""

import unittest
from src.core.constants import CorrelationType, HttpLocation
from src.models.tracking import SampleResultRecord
from src.detector.correlation_detector import CorrelationDetectorEngine

class TestCorrelationDetectorEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.detector = CorrelationDetectorEngine(min_confidence=0.50)

    def test_jsessionid_cookie_detection(self) -> None:
        record = SampleResultRecord(
            elapsed_ms=10,
            response_code="200",
            response_message="OK",
            thread_name="Thread-1",
            sample_label="Login Transaction",
            cookies={"JSESSIONID": "abc123XYZ789MTG"}
        )
        
        candidates = self.detector.analyze_record(record, index=1)
        self.assertTrue(len(candidates) >= 1)
        
        # Verify the candidate properties match expectations
        jsession_cand = [c for c in candidates if c.correlation_type == CorrelationType.JSESSIONID][0]
        self.assertEqual(jsession_cand.extracted_value, "abc123XYZ789MTG")
        self.assertEqual(jsession_cand.location, HttpLocation.COOKIES)

    def test_csrf_token_html_body_detection(self) -> None:
        html_payload = """
        <html>
          <head><title>Secure Page</title></head>
          <body>
            <input type="hidden" name="_csrf" value="security_token_payload_abc" />
          </body>
        </html>
        """
        record = SampleResultRecord(
            elapsed_ms=45,
            response_code="200",
            response_message="OK",
            thread_name="Thread-1",
            sample_label="Get Dashboard",
            response_body=html_payload
        )
        
        candidates = self.detector.analyze_record(record, index=2)
        csrf_cand = [c for c in candidates if c.correlation_type == CorrelationType.CSRF_TOKEN][0]
        
        self.assertEqual(csrf_cand.extracted_value, "security_token_payload_abc")
        self.assertEqual(csrf_cand.location, HttpLocation.BODY)

    def test_jwt_token_auth_detection(self) -> None:
        raw_json_auth = '{"token_type": "Bearer", "access_token": "eyJbX0.eyJ1c2VySWQiOiI5OSJ9.signature_xyz"}'
        record = SampleResultRecord(
            elapsed_ms=100,
            response_code="200",
            response_message="OK",
            thread_name="Thread-1",
            sample_label="Auth Endpoint",
            response_body=raw_json_auth
        )
        
        candidates = self.detector.analyze_record(record, index=3)
        jwt_cand = [c for c in candidates if c.correlation_type == CorrelationType.JWT_TOKEN][0]
        
        self.assertEqual(jwt_cand.extracted_value, "eyJbX0.eyJ1c2VySWQiOiI5OSJ9.signature_xyz")