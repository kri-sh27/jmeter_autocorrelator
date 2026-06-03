"""
Log Parsing Engine Verification Suite.
Validates extraction pipelines across both XML and CSV log structures.
"""

import os
import unittest
from src.collector.jtl_collector import JtlResponseCollectorEngine
from src.config.exceptions import ExecutionException

class TestJtlResponseCollectorEngine(unittest.TestCase):

    def setUp(self) -> None:
        self.xml_jtl_path = "mock_output_trace.jtl"
        self.csv_jtl_path = "mock_output_table.jtl"
        
        # 1. Setup mock XML execution logs
        self.xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<testResults version="1.2">
  <httpSample t="245" rc="200" rm="OK" tn="Thread Group 1-1" dt="text" s="true" by="1024" lb="Fetch Secure Landing">
    <requestHeader class="java.lang.String">Host: api.enterprise.io\nCookie: session_id_marker=XYZ987654321\n</requestHeader>
    <responseHeader class="java.lang.String">Content-Type: text/html\nSet-Cookie: app_state=active_session_token\n</responseHeader>
    <queryString class="java.lang.String">action=load_view</queryString>
    <responseData class="java.lang.String"><![CDATA[<html>Welcome User!</html>]]></responseData>
  </httpSample>
</testResults>
"""
        # 2. Setup mock CSV execution logs
        self.csv_content = (
            "elapsed,responseCode,responseMessage,threadName,dataType,success,bytes,label,requestHeaders,responseHeaders,queryString,responseData\n"
            "412,201,Created,Thread Group 1-1,text,true,512,Post Transaction,Host: api.enterprise.io,Content-Type: application/json,user_id=99,{'status':'success'}\n"
        )

        with open(self.xml_jtl_path, "w", encoding="utf-8") as f:
            f.write(self.xml_content)
        with open(self.csv_jtl_path, "w", encoding="utf-8") as f:
            f.write(self.csv_content)

    def tearDown(self) -> None:
        for path in [self.xml_jtl_path, self.csv_jtl_path]:
            if os.path.exists(path):
                os.remove(path)

    def test_missing_file_throws_execution_exception(self) -> None:
        with self.assertRaises(ExecutionException):
            engine = JtlResponseCollectorEngine("missing_trace_file.jtl")
            list(engine.stream_records())

    def test_xml_format_streaming_extraction(self) -> None:
        engine = JtlResponseCollectorEngine(self.xml_jtl_path)
        records = list(engine.stream_records())
        
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.sample_label, "Fetch Secure Landing")
        self.assertEqual(record.elapsed_ms, 245)
        self.assertTrue(record.success)
        self.assertEqual(record.request_headers["Host"], "api.enterprise.io")
        self.assertEqual(record.cookies["session_id_marker"], "XYZ987654321")
        self.assertEqual(record.cookies["app_state"], "active_session_token")
        self.assertIn("Welcome User!", record.response_body)

    def test_csv_format_streaming_extraction(self) -> None:
        engine = JtlResponseCollectorEngine(self.csv_jtl_path)
        records = list(engine.stream_records())
        
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.sample_label, "Post Transaction")
        self.assertEqual(record.response_code, "201")
        self.assertEqual(record.elapsed_ms, 412)
        self.assertEqual(record.request_body, "user_id=99")
        self.assertEqual(record.response_body, "{'status':'success'}")