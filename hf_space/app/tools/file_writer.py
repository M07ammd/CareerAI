"""
CareerPilot AI - File Writer Tool

Saves generated reports and analysis results to disk.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


def _ensure_output_dir() -> Path:
    settings = get_settings()
    output_dir = Path(settings.report_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_report_markdown(
    markdown_content: str, candidate_name: str = "candidate"
) -> str:
    """
    Save a Markdown report to the output directory.
    If settings.save_reports is False, this is a no-op.
    """
    settings = get_settings()
    if not settings.save_reports:
        return ""

    import uuid

    output_dir = _ensure_output_dir()
    file_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}_{file_id}.md"
    file_path = output_dir / filename
    file_path.write_text(markdown_content, encoding="utf-8")
    logger.info("Report saved to: %s", file_path)
    return str(file_path.resolve())


def save_analysis_json(data: dict[str, Any], candidate_name: str = "candidate") -> str:
    """
    Save the full analysis result as a JSON file.
    If settings.save_reports is False, this is a no-op.
    """
    settings = get_settings()
    if not settings.save_reports:
        return ""

    import uuid

    output_dir = _ensure_output_dir()
    file_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"analysis_{timestamp}_{file_id}.json"
    file_path = output_dir / filename
    file_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    logger.info("Analysis JSON saved to: %s", file_path)
    return str(file_path.resolve())
