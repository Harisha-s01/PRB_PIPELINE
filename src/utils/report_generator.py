import os
from datetime import datetime
import pandas as pd
from jinja2 import Template

class ReportGenerator:
    def __init__(self, processed_documents=None):
        self.processed_documents = processed_documents or []
        self.template = """
# Product Baseline Report — {{ baseline_id }}
**Product**: {{ product_name }}
**Baseline ID**: {{ baseline_id }}
**Date**: {{ date }}

## Executive Summary
{{ executive_summary }}

## Product Configuration
{% for row in configuration %}
- {{ row.key }}: {{ row.value }}
{% endfor %}

## BOM (Top items)
| Part No | Description | Qty | Source |
|---------|-------------|-----|--------|
{% for item in bom %}
| {{ item.part_no }} | {{ item.desc }} | {{ item.qty }} | {{ item.source }} |
{% endfor %}

## Test / Build Summary
{{ test_summary }}

## Recommendations
{{ recommendations }}

## Citations
{% for c in citations %}
- {{ c }}
{% endfor %}
"""

    def generate_report(self):
        """Generate PBR from processed documents"""
        if not self.processed_documents:
            # Fallback to sample data if no documents processed
            return self._generate_sample_report()

        # Extract information from processed documents
        sources = [doc["source"] for doc in self.processed_documents]
        unique_sources = list(set(sources))

        report_data = {
            "baseline_id": f"PBR-{datetime.now().strftime('%Y%m%d')}",
            "product_name": "Product from Documents",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "executive_summary": f"This report is based on {len(unique_sources)} processed documents containing {len(self.processed_documents)} text segments.",
            "configuration": [
                {"key": "Version", "value": "Extracted from documents"},
                {"key": "Branch", "value": "main"},
                {"key": "Documents Processed", "value": str(len(unique_sources))}
            ],
            "bom": [
                {"part_no": "TBD", "desc": "To be determined from document analysis", "qty": 0, "source": "N/A"}
            ],
            "test_summary": "Document analysis completed. Further processing needed for detailed test results.",
            "recommendations": "Review all processed documents for complete baseline information.",
            "citations": unique_sources
        }

        template = Template(self.template)
        return template.render(**report_data)

    def _generate_sample_report(self):
        """Generate sample report when no documents are processed"""
        report_data = {
            "baseline_id": f"PBR-{datetime.now().strftime('%Y%m%d')}",
            "product_name": "Sample Product",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "executive_summary": "This is a sample executive summary. No documents have been processed yet.",
            "configuration": [
                {"key": "Version", "value": "1.0.0"},
                {"key": "Branch", "value": "main"},
                {"key": "Commit", "value": "abc123"}
            ],
            "bom": [
                {"part_no": "001", "desc": "Sample Part", "qty": 10, "source": "bom.xlsx"}
            ],
            "test_summary": "All tests passed successfully.",
            "recommendations": "No critical issues found.",
            "citations": [
                "document1.pdf:page1",
                "bom.xlsx:sheet1"
            ]
        }

        template = Template(self.template)
        return template.render(**report_data)
