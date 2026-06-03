"""
JTL Log Pipeline Collector Engine.
Implements memory-safe streaming parsers to evaluate high-throughput transactions.
"""

import os
import csv
import xml.etree.ElementTree as ET
import logging
from typing import Generator, Dict, List, Tuple
from src.config.exceptions import ExecutionException
from src.models.tracking import SampleResultRecord

logger = logging.getLogger("JMeterAutoCorrelator")

class JtlResponseCollectorEngine:
    """
    Directs the execution log parsing workflow. Supports high-volume stream tracking 
    across XML and CSV formats seamlessly.
    """

    def __init__(self, jtl_file_path: str) -> None:
        if not os.path.exists(jtl_file_path):
            raise ExecutionException(f"Target runtime tracing file trace sequence target not found: {jtl_file_path}")
        self.jtl_path = jtl_file_path

    def stream_records(self) -> Generator[SampleResultRecord, None, None]:
        """
        Dynamically detects encoding layouts to route processing through memory-safe 
        incremental tokenizers.
        """
        if self._is_xml_jtl():
            yield from self._stream_xml_format()
        else:
            yield from self._stream_csv_format()

    def _is_xml_jtl(self) -> bool:
        """Sniffs initial file header bytes to confirm XML markup wrappers safely."""
        try:
            with open(self.jtl_path, "r", encoding="utf-8", errors="ignore") as file_stream:
                leading_bytes = file_stream.read(200).strip()
                return leading_bytes.startswith("<?xml") or leading_bytes.startswith("<testResults")
        except Exception as exc:
            raise ExecutionException(f"Failed verifying layout markers on target trace file: {str(exc)}")

    def _stream_xml_format(self) -> Generator[SampleResultRecord, None, None]:
        """
        Implements an incremental XML tokenizer using element trees to process 
        unlimited file sizes with low memory overhead.
        """
        try:
            # Leverage incremental target event generation blocks
            context = ET.iterparse(self.jtl_path, events=("end",))
            for event, elem in context:
                # Standard xml format elements: 'httpSample' or 'sample'
                if elem.tag in ("httpSample", "sample"):
                    yield self._transform_xml_node_to_record(elem)
                    # Clear processed node allocations immediately to reclaim memory
                    elem.clear()
        except Exception as parse_failure:
            raise ExecutionException(f"Fatal disruption processing streaming XML element parsing tokens: {str(parse_failure)}")

    def _transform_xml_node_to_record(self, node: ET.Element) -> SampleResultRecord:
        """Extracts attributes and nested text nodes from XML sample representations."""
        # Parse transport headers from underlying response text layers
        req_headers = self._parse_header_block_string(node.findtext("requestHeader", ""))
        res_headers = self._parse_header_block_string(node.findtext("responseHeader", ""))
        
        # Extract cookie states directly from available header configurations
        cookies = {}
        if "Cookie" in req_headers:
            cookies.update(self._parse_cookie_header(req_headers["Cookie"]))
        if "Set-Cookie" in res_headers:
            cookies.update(self._parse_cookie_header(res_headers["Set-Cookie"]))

        return SampleResultRecord(
            elapsed_ms=int(node.attrib.get("t", 0)),
            response_code=node.attrib.get("rc", "200"),
            response_message=node.attrib.get("rm", "OK"),
            thread_name=node.attrib.get("tn", "ThreadWorker"),
            data_type=node.attrib.get("dt", "text"),
            success=node.attrib.get("s", "true").lower() == "true",
            bytes_received=int(node.attrib.get("by", 0)),
            sample_label=node.attrib.get("lb", "UnlabeledSampler"),
            request_headers=req_headers,
            response_headers=res_headers,
            request_body=node.findtext("queryString", "") or node.findtext("requestData", ""),
            response_body=node.findtext("responseData", "") or "",
            cookies=cookies
        )

    def _stream_csv_format(self) -> Generator[SampleResultRecord, None, None]:
        """
        Parses classic flat CSV tables sequentially using iterative generator streams.
        """
        try:
            with open(self.jtl_path, mode="r", encoding="utf-8", errors="ignore") as csv_file:
                # Use standard sniffer patterns to check the dialect structure
                reader = csv.DictReader(csv_file)
                for index, row in enumerate(reader):
                    yield self._transform_csv_row_to_record(row, index)
        except Exception as csv_failure:
            raise ExecutionException(f"Fatal disruption reading sequence entries on target line records: {str(csv_failure)}")

    def _transform_csv_row_to_record(self, row: Dict[str, str], fallback_idx: int) -> SampleResultRecord:
        """Maps standard JMeter CSV output variables into a structured tracking record."""
        # Handle field differences dynamically based on custom user logging parameters
        success_flag = row.get("success", "true").lower() == "true"
        
        # Extract payload metrics from columns if present in the configuration settings
        req_headers = self._parse_header_block_string(row.get("requestHeaders", ""))
        res_headers = self._parse_header_block_string(row.get("responseHeaders", ""))
        
        cookies = {}
        if "Cookie" in req_headers:
            cookies.update(self._parse_cookie_header(req_headers["Cookie"]))

        return SampleResultRecord(
            elapsed_ms=int(row.get("elapsed", 0) or 0),
            response_code=row.get("responseCode", "200"),
            response_message=row.get("responseMessage", "OK"),
            thread_name=row.get("threadName", f"Worker-{fallback_idx}"),
            data_type=row.get("dataType", "text"),
            success=success_flag,
            bytes_received=int(row.get("bytes", 0) or 0),
            sample_label=row.get("label", f"Sampler-{fallback_idx}"),
            request_headers=req_headers,
            response_headers=res_headers,
            request_body=row.get("queryString", "") or row.get("requestData", ""),
            response_body=row.get("responseData", ""),
            cookies=cookies
        )

    def _parse_header_block_string(self, headers_block: str) -> Dict[str, str]:
        """Splits raw header text patterns into standard key-value maps cleanly."""
        mapped_headers: Dict[str, str] = {}
        if not headers_block:
            return mapped_headers
        for line in headers_block.strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                mapped_headers[key.strip()] = val.strip()
        return mapped_headers

    def _parse_cookie_header(self, cookie_string: str) -> Dict[str, str]:
        """Extracts cookie key-value data maps from standard network transmission headers."""
        cookie_map: Dict[str, str] = {}
        if not cookie_string:
            return cookie_map
        # Split options apart across standard punctuation markers
        for cookie_token in cookie_string.split(";"):
            clean_token = cookie_token.strip()
            if "=" in clean_token:
                key, val = clean_token.split("=", 1)
                # Filter out transport directives like path or secure flags
                if key.strip().lower() not in ("path", "domain", "expires", "secure", "httponly"):
                    cookie_map[key.strip()] = val.strip()
        return cookie_map