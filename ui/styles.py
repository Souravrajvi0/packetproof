"""Streamlit custom CSS for PacketProof."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.main .block-container {
    padding-top: 2rem;
    max-width: 1100px;
}

.pp-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    color: #f8fafc;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    border: 1px solid #334155;
}

.pp-header h1 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
}

.pp-tagline {
    color: #94a3b8;
    margin-top: 0.5rem;
    font-size: 1.05rem;
}

.pp-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.pp-metric-verified { border-left: 4px solid #0d9488; }
.pp-metric-missing { border-left: 4px solid #dc2626; }
.pp-metric-review { border-left: 4px solid #d97706; }
.pp-metric-neutral { border-left: 4px solid #64748b; }

.pp-badge {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

.pp-badge-verified { background: #ccfbf1; color: #0f766e; }
.pp-badge-missing { background: #fee2e2; color: #b91c1c; }
.pp-badge-review { background: #ffedd5; color: #c2410c; }
.pp-badge-na { background: #f1f5f9; color: #475569; }

.pp-step-label {
    color: #0f172a;
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
}

.pp-muted {
    color: #64748b;
    font-size: 0.9rem;
}

.pp-doc-card {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem;
    background: #f8fafc;
}

.pp-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.85rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
}
</style>
"""
