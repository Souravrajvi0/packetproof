import pytest

from core.pdf_processor import create_text_pdf
from core.pipeline import run_analysis


def test_empty_application_raises():
    req = create_text_pdf("r.pdf", ["Requirements here"])
    with pytest.raises(ValueError):
        run_analysis(("r.pdf", req), [], skip_contradictions=True)
