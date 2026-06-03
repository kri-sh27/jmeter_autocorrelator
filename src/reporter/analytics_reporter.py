"""
Enterprise Reporting and Analytics Engine.
Compiles pipeline run summaries into clean Markdown files and interactive HTML dashboards.
"""

import os
import json
import logging
from typing import List, Dict, Any
from src.models.correlation import ParameterDependencyMatrix

logger = logging.getLogger("JMeterAutoCorrelator")

class AnalyticsReportEngine:
    """
    Transforms raw auto-correlation transaction telemetry logs into comprehensive
    executive performance summaries and interactive documentation.
    """

    def __init__(self, pipeline_results: Dict[str, Any], dependencies: List[ParameterDependencyMatrix]) -> None:
        self.results = pipeline_results
        self.dependencies = dependencies
        self.output_dir = os.path.abspath("./workspace/reports")
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_markdown_summary(self) -> str:
        """Assembles a highly readable technical summary file using markdown formatting rules."""
        target_path = os.path.join(self.output_dir, "correlation_report.md")
        
        md_content = [
            "# JMeter Auto-Correlation Performance Report",
            "## Executive Summary KPI Metrics",
            f"| Metric Classification | Consolidated Result State |",
            f"| :--- | :--- |",
            f"| **Pipeline Execution Status** | `{self.results.get('status', 'UNKNOWN')}` |",
            f"| **Total Source JMX Samplers** | {self.results.get('samplers_count', 0)} |",
            f"| **Live Runtime Requests Triggered** | {self.results.get('total_requests', 0)} |",
            f"| **Baseline Loop Error Footprint** | {self.results.get('error_percentage', 0.0)}% |",
            f"| **Dynamic Candidates Identified** | {self.results.get('detected_candidates', 0)} |",
            f"| **Total Injectable Rules Applied** | {self.results.get('applied_correlations', 0)} |",
            "",
            "## Mapped Functional Value Dependencies Trace Matrix",
        ]

        if not self.dependencies:
            md_content.append("*No downstream parameter matches or substitutions were recorded for this execution trace.*")
        else:
            md_content.append("| Parameter Name Handle | Source Origin Step | Target Downstream Sampler | Location | Parameter Key Field |")
            md_content.append("| :--- | :--- | :--- | :--- | :--- |")
            for dep in self.dependencies:
                md_content.append(
                    f"| `{dep.candidate.parameter_name}` | {dep.candidate.source_sampler_name} | "
                    f"{dep.target_sampler_name} | {dep.target_location.value} | `{dep.target_parameter_key or 'Inline'}` |"
                )

        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write("\n".join(md_content))
            logger.info(f"Markdown analytics execution brief successfully written to: {target_path}")
            return target_path
        except Exception as exc:
            logger.error(f"Failed writing markdown report artifact data structures: {str(exc)}")
            return ""

    def generate_html_dashboard(self) -> str:
        """Generates a standalone responsive HTML page with interactive visualization charts."""
        target_path = os.path.join(self.output_dir, "correlation_report.html")
        
        # Serialize dependency matrix collections cleanly for browser-side script consumption
        serialized_deps = []
        for dep in self.dependencies:
            serialized_deps.append({
                "param": dep.candidate.parameter_name,
                "source": dep.candidate.source_sampler_name,
                "target": dep.target_sampler_name,
                "loc": dep.target_location.value,
                "key": dep.target_parameter_key or "Query String/Body"
            })

        html_blueprint = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>JMeter Auto-Correlation Analytics Hub</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; background: #fdfdfd; color: #2c3e50; }}
        .card {{ background: white; padding: 24px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 24px; border: 1px solid #eaeaea; }}
        h1, h2 {{ color: #1a2a3a; border-bottom: 2px solid #eaeaea; padding-bottom: 8px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-tile {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 16px; text-align: center; }}
        .metric-tile div {{ font-size: 28px; font-weight: bold; color: #2b6cb0; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
        th {{ background: #edf2f7; color: #4a5568; }}
        tr:hover {{ background: #f7fafc; }}
        .badge {{ background: #e2e8f0; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>JMeter Auto-Correlation Analytics Hub</h1>
    
    <div class="card">
        <h2>Pipeline Execution Performance Metrics</h2>
        <div class="grid">
            <div class="metric-tile">Status<div>{self.results.get('status', 'SUCCESS')}</div></div>
            <div class="metric-tile">Total Samplers<div>{self.results.get('samplers_count', 0)}</div></div>
            <div class="metric-tile">Requests Executed<div>{self.results.get('total_requests', 0)}</div></div>
            <div class="metric-tile">Error Footprint<div>{self.results.get('error_percentage', 0.0)}%</div></div>
            <div class="metric-tile">Applied Rules<div>{self.results.get('applied_correlations', 0)}</div></div>
        </div>
    </div>

    <div class="card">
        <h2>Interactive Value Trace Data Topology</h2>
        <table>
            <thead>
                <tr>
                    <th>Parameter Variable Name</th>
                    <th>Source Origin Sampler Step</th>
                    <th>Target Destination Sampler Field</th>
                    <th>HTTP Segment Location</th>
                    <th>Target Field Key</th>
                </tr>
            </thead>
            <tbody id="topology-rows">
                </tbody>
        </table>
    </div>

    <script>
        const dataset = {json.dumps(serialized_deps)};
        const tbody = document.getElementById('topology-rows');
        
        if(dataset.length === 0) {{
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#718096;">No forward dependencies mapped for this trace loop run.</td></tr>';
        }} else {{
            dataset.forEach(row => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="badge" style="background:#ebf8ff; color:#2b6cb0;">${{row.param}}</span></td>
                    <td>${{row.source}}</td>
                    <td>${{row.target}}</td>
                    <td><span class="badge">${{row.loc}}</span></td>
                    <td><code>${{row.key}}</code></td>
                `;
                tbody.appendChild(tr);
            }});
        }}
    </script>
</body>
</html>
"""
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(html_blueprint)
            logger.info(f"Interactive HTML dashboard visualization exported directly to: {target_path}")
            return target_path
        except Exception as exc:
            logger.error(f"Failed creating serialized interactive HTML dashboard component layouts: {str(exc)}")
            return ""