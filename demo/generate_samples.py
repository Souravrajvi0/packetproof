#!/usr/bin/env python3
"""Generate synthetic demo PDFs for PacketProof."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.pdf_processor import create_text_pdf

SAMPLES_DIR = Path(__file__).resolve().parent / "samples"


def requirements_pdf() -> bytes:
    pages = [
        """Meridian Future Scholars Program — Application Requirements 2026

1. DOCUMENT REQUIREMENTS
Applicants must submit a completed Meridian application form (signed where indicated).
An official academic transcript from your current or most recent institution is required.
A government-issued photo identification copy must be provided.
One recommendation letter from a faculty member is required; the letter must be dated within the last six (6) months of the submission deadline.
A personal statement of no more than two pages is required.

2. ELIGIBILITY
Applicants must maintain a minimum cumulative GPA of 3.0 on a 4.0 scale.
Applicants must be graduating high school or equivalent in 2025 or 2026.

3. FORMATTING
All documents must be submitted as PDF unless otherwise noted.
The applicant declaration on the final page of the application form must be signed and dated.

4. CONDITIONAL REQUIREMENTS
International applicants (non-U.S. citizens without permanent residency) must submit
proof of English proficiency (TOEFL or IELTS). This requirement does not apply to
applicants who are U.S. citizens or permanent residents.

5. DEADLINE
Complete packets are due by March 15, 2026.
""",
    ]
    return create_text_pdf("meridian_requirements_2026.pdf", pages)


def application_form_pdf() -> bytes:
    pages = [
        """Meridian Future Scholars Program — Application Form

Applicant Legal Name: Alex Rivera
Date of Birth: 04/12/2007
Email: alex.rivera@example.edu
Intended Major: Environmental Science

Education:
Northview High School
Expected Graduation Date: June 2025
Cumulative GPA: 2.7

Personal Statement: see separate file personal_statement.pdf

DECLARATION
I certify that the information provided is accurate.
Applicant Signature: _________________________
Date: February 10, 2026
""",
    ]
    return create_text_pdf("application_form.pdf", pages)


def resume_pdf() -> bytes:
    pages = [
        """Alex Rivera — Resume

Education
Northview High School
Graduation: May 2024
GPA: 2.7

Activities: Science Club, Volunteer Trail Restoration
""",
    ]
    return create_text_pdf("resume.pdf", pages)


def recommendation_pdf() -> bytes:
    pages = [
        """Letter of Recommendation

To the Meridian Future Scholars Committee,

I recommend Alex Rivera for your program. Alex has shown dedication in my chemistry class.

Sincerely,
Dr. Priya Nandakumar
Northview High School

Date: November 12, 2024
""",
    ]
    return create_text_pdf("recommendation_letter.pdf", pages)


def id_copy_pdf() -> bytes:
    pages = [
        """COPY — Fictional State ID (DEMO ONLY)

Name: Alex Rivera
DOB: 04/12/2007
ID Number: NF-000-4821
""",
    ]
    return create_text_pdf("photo_id_copy.pdf", pages)


def personal_statement_pdf() -> bytes:
    pages = [
        """Personal Statement — Alex Rivera

Growing up near the coast, I became passionate about protecting wetlands.
I hope to study environmental science and contribute to community-led restoration projects.
This statement is one page for demonstration purposes.
""",
    ]
    return create_text_pdf("personal_statement.pdf", pages)


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "meridian_requirements_2026.pdf": requirements_pdf(),
        "application_form.pdf": application_form_pdf(),
        "resume.pdf": resume_pdf(),
        "recommendation_letter.pdf": recommendation_pdf(),
        "photo_id_copy.pdf": id_copy_pdf(),
        "personal_statement.pdf": personal_statement_pdf(),
    }
    for name, data in files.items():
        path = SAMPLES_DIR / name
        path.write_bytes(data)
        print(f"Wrote {path}")

    key_path = Path(__file__).resolve().parent / "answer_key.json"
    print(f"Answer key: {key_path}")


if __name__ == "__main__":
    main()
