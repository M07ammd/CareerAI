"""
Tests for the FastAPI endpoints.

Phase 4 compliance:
- Imports from app.*, patches real objects the app uses.
- No real LLM or search API calls.
- test_successful_analysis asserts exactly 200 and a real response body.
"""

import io
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Set dummy env so config does not fail
os.environ.setdefault("OPENAI_API_KEY", "test-key-123")

from app.main import app
from app.schemas.models import AnalysisResponse, FinalReport, ResumeAnalysis, JobAnalysis, SkillMatch


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def minimal_pdf_bytes():
    """
    Return a minimal valid PDF byte string that PyMuPDF can parse.
    This PDF contains a single page with the text "Hello World".
    """
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\n"
        b"BT /F1 12 Tf 100 700 Td (Hello World) Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000266 00000 n \n"
        b"0000000360 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n441\n%%EOF"
    )


@pytest.fixture
def fake_analysis_response():
    """A complete AnalysisResponse with all fields populated."""
    return AnalysisResponse(
        status="success",
        resume_analysis=ResumeAnalysis(
            candidate_name="Alice Smith",
            summary="Senior ML Engineer with 5 years of experience.",
            technical_skills=["Python", "PyTorch", "LangChain"],
        ),
        job_analysis=JobAnalysis(
            job_title="Senior ML Engineer",
            required_skills=["Python", "PyTorch"],
            domain="ML Engineering",
            seniority_level="Senior",
        ),
        skill_match=SkillMatch(
            matched_skills=["Python", "PyTorch"],
            missing_skills=["LangGraph"],
            match_score=66,
            explanation="Good match.",
            strengths="| Finding | Evidence |",
        ),
        final_report=FinalReport(
            candidate_name="Alice Smith",
            job_title="Senior ML Engineer",
            executive_summary="Alice is a strong match for this role.",
            match_score=66,
            score_interpretation="Good fit with some gaps.",
            hiring_probability="Medium",
            top_recommendations="| Finding | Evidence |",
            full_report_markdown="# Report\n\nGood match.",
        ),
        processing_steps=["resume_agent", "job_agent", "skill_agent", "report_agent"],
    )


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "llm_provider" in data

    def test_health_ready_returns_200_or_503(self, client):
        """Health ready endpoint should exist and return 200 or 503."""
        response = client.get("/api/health/ready")
        assert response.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Analyze endpoint — input validation
# ---------------------------------------------------------------------------


class TestAnalyzeEndpoint:
    def test_missing_file_returns_422(self, client):
        response = client.post(
            "/api/analyze",
            data={"job_description": "A valid job description with at least 50 characters here"},
        )
        assert response.status_code == 422

    def test_missing_job_description_returns_422(self, client, minimal_pdf_bytes):
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", minimal_pdf_bytes, "application/pdf")},
        )
        assert response.status_code == 422

    def test_non_pdf_file_returns_400(self, client):
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.txt", b"plain text content", "text/plain")},
            data={"job_description": "A valid job description with at least 50 characters here."},
        )
        assert response.status_code == 400

    def test_empty_file_returns_400(self, client):
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", b"", "application/pdf")},
            data={"job_description": "A valid job description with at least 50 characters here."},
        )
        assert response.status_code == 400

    def test_short_job_description_returns_422(self, client, minimal_pdf_bytes):
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", minimal_pdf_bytes, "application/pdf")},
            data={"job_description": "Too short"},
        )
        assert response.status_code == 422

    def test_fake_pdf_header_rejected(self, client):
        """A file named .pdf but with non-PDF content should fail gracefully."""
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", b"not a real pdf just fake content here", "application/pdf")},
            data={"job_description": "A valid job description with at least 50 characters here."},
        )
        # Should get 422 (parse error) not 500
        assert response.status_code in (400, 422)

    @patch("app.api.routes.run_analysis")
    @patch("app.api.routes.extract_text_from_pdf")
    def test_successful_analysis(self, mock_extract, mock_run, client, minimal_pdf_bytes, fake_analysis_response):
        """
        A valid request with a real PDF and a long JD must return EXACTLY 200
        and a response body that matches AnalysisResponse schema.
        """
        mock_extract.return_value = (
            "Alice Smith\nSenior ML Engineer\n"
            "Python, PyTorch, LangChain, 5 years experience building ML systems."
        )
        mock_run.return_value = fake_analysis_response

        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", minimal_pdf_bytes, "application/pdf")},
            data={
                "job_description": (
                    "We are looking for a Senior ML Engineer with Python, PyTorch, "
                    "LangChain, LangGraph, 5+ years experience, FastAPI expertise."
                )
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Validate response shape
        assert data["status"] == "success"
        assert data["resume_analysis"]["candidate_name"] == "Alice Smith"
        assert data["skill_match"]["match_score"] == 66
        assert data["final_report"]["match_score"] == 66
        assert len(data["processing_steps"]) > 0
        # Verify no exception text leaks into the response
        body_str = str(data)
        assert "Traceback" not in body_str
        assert "Exception" not in body_str

    @patch("app.api.routes.run_analysis")
    @patch("app.api.routes.extract_text_from_pdf")
    def test_error_response_never_contains_exception_text(self, mock_extract, mock_run, client, minimal_pdf_bytes):
        """Error responses must not leak raw exception messages."""
        mock_extract.return_value = "Some CV text that is long enough for analysis."
        mock_run.side_effect = RuntimeError("Secret internal error with credentials xyz123")

        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", minimal_pdf_bytes, "application/pdf")},
            data={
                "job_description": (
                    "We are looking for a Senior ML Engineer with Python and PyTorch. "
                    "5+ years experience required, FastAPI, Docker, Kubernetes."
                )
            },
        )

        assert response.status_code == 500
        body = response.text
        # Must NOT leak the raw exception text
        assert "Secret internal error" not in body
        assert "xyz123" not in body
        # Must contain a request ID for correlation
        data = response.json()
        detail = data.get("detail", {})
        assert "request_id" in detail

    def test_request_id_header_always_present(self, client):
        """Every response must have an X-Request-ID header."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert "x-request-id" in response.headers


# ---------------------------------------------------------------------------
# Input validation (Pydantic schemas)
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_job_description_minimum_length(self):
        """Validate that short JDs are caught early at the schema level."""
        from app.schemas.models import AnalysisRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            AnalysisRequest(job_description="Short")

    def test_job_description_valid(self):
        from app.schemas.models import AnalysisRequest

        req = AnalysisRequest(
            job_description=(
                "We need a Python developer with at least 3 years of experience "
                "in backend development, REST APIs, and cloud platforms."
            )
        )
        assert len(req.job_description) >= 50


# ---------------------------------------------------------------------------
# Upload limits
# ---------------------------------------------------------------------------


class TestUploadLimits:
    def test_non_pdf_extension_rejected(self, client):
        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.docx", b"fake content", "application/octet-stream")},
            data={"job_description": "A valid job description with at least 50 characters here."},
        )
        assert response.status_code == 400

    def test_oversized_pdf_by_content_length_header(self, client):
        """Files claiming oversized Content-Length should be rejected early."""
        from app.config import get_settings
        s = get_settings()
        max_bytes = s.max_pdf_size_mb * 1024 * 1024
        big_fake_pdf = b"%PDF-1.4" + b"0" * 100

        response = client.post(
            "/api/analyze",
            files={"cv_file": ("resume.pdf", big_fake_pdf, "application/pdf")},
            data={"job_description": "A valid job description with at least 50 characters here."},
            headers={"Content-Length": str(max_bytes + 1024 * 1024 + 4096)},
        )
        # Should be rejected (413) or fall through to parse error (400/422)
        assert response.status_code in (400, 413, 422)


# ---------------------------------------------------------------------------
# SSE streaming endpoint
# ---------------------------------------------------------------------------


class TestStreamEndpoint:
    def test_stream_endpoint_exists(self, client, minimal_pdf_bytes):
        """The /analyze/stream endpoint must exist and return 200 with event-stream."""
        with patch("app.api.routes.extract_text_from_pdf") as mock_extract:
            with patch("app.api.routes.run_analysis_stream") as mock_stream:
                mock_extract.return_value = "Some CV text long enough for analysis processing."

                async def fake_stream(*args, **kwargs):
                    yield 'data: {"node": "resume_agent", "status": "completed"}\n\n'
                    yield 'data: {"node": "workflow", "status": "done"}\n\n'

                mock_stream.return_value = fake_stream()

                response = client.post(
                    "/api/analyze/stream",
                    files={"cv_file": ("resume.pdf", minimal_pdf_bytes, "application/pdf")},
                    data={
                        "job_description": (
                            "Senior Python Developer with ML experience required. "
                            "5+ years, FastAPI, Docker, PyTorch, LangChain."
                        )
                    },
                )
                assert response.status_code == 200
