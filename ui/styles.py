"""Streamlit custom CSS for PacketProof."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    font-family: Inter, system-ui, -apple-system, sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #f4f6f9;
}

/* Keep Material icon ligatures intact */
span[class^="material"],
[data-testid="stIconMaterial"],
.material-icons,
.material-symbols-outlined,
.material-symbols-rounded {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
}

.main .block-container {
    padding-top: 1.4rem;
    padding-bottom: 3rem;
    max-width: 1120px;
}

[data-testid="stHeader"] {
    background: transparent;
}
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="collapsedControl"],
#MainMenu {
    visibility: hidden;
    height: 0;
}

[data-testid="stFileUploaderDropzone"] [data-testid="stIconMaterial"],
[data-testid="stFileUploader"] [data-testid="stIconMaterial"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    background: #0f172a;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: #cbd5e1;
}
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] [data-baseweb="input"] {
    background: #1e293b !important;
    color: #f8fafc !important;
    border-color: #334155 !important;
}
[data-testid="stSidebar"] .stButton button {
    background: #1e293b;
    border: 1px solid #334155;
    color: #f8fafc;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stButton button:hover {
    border-color: #14b8a6;
    color: #ccfbf1;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: 0.7rem 1.2rem;
    letter-spacing: 0.01em;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%);
}

[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 1.5px dashed #cbd5e1;
    border-radius: 14px;
    padding: 0.35rem 0.5rem 0.7rem;
}
[data-testid="stFileUploader"]:hover {
    border-color: #14b8a6;
    background: #f0fdfa;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem;
    background: #eef2f7;
    padding: 0.3rem;
    border-radius: 12px;
    border: none !important;
}
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] {
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    color: #475569 !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 0.45rem 0.9rem !important;
}
.stTabs [data-baseweb="tab"]:focus,
.stTabs [data-baseweb="tab"]:focus-visible {
    outline: none !important;
    box-shadow: none !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #0f172a !important;
    border: none !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08) !important;
}
.stTabs button::after,
.stTabs [data-baseweb="tab"]::after {
    display: none !important;
    content: none !important;
    border: none !important;
}

.pp-header {
    background: linear-gradient(135deg, #0b1224 0%, #163054 55%, #115e59 140%);
    color: #f8fafc;
    padding: 1.75rem 2rem;
    border-radius: 18px;
    margin-bottom: 1.25rem;
    border: 1px solid #1e3a5f;
    display: flex;
    gap: 1.25rem;
    align-items: center;
}
.pp-mark {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: rgba(20, 184, 166, 0.18);
    border: 1px solid rgba(94, 234, 212, 0.35);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1.15rem;
    color: #99f6e4;
    flex-shrink: 0;
}
.pp-header h1 {
    margin: 0;
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.03em;
}
.pp-tagline {
    color: #94a3b8;
    margin-top: 0.35rem;
    font-size: 1rem;
}
.pp-pills {
    margin-top: 0.7rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
}
.pp-pill {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    color: #e2e8f0;
    border-radius: 999px;
    padding: 0.18rem 0.7rem;
    font-size: 0.75rem;
    font-weight: 500;
}

.pp-stepper {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.5rem;
    margin: 0 0 1.4rem 0;
}
.pp-step {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.7rem 0.85rem;
    min-height: 72px;
}
.pp-step.active {
    border-color: #14b8a6;
    box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.12);
}
.pp-step .n {
    font-size: 0.7rem;
    font-weight: 700;
    color: #0d9488;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pp-step .t {
    display: block;
    margin-top: 0.2rem;
    color: #0f172a;
    font-weight: 600;
    font-size: 0.88rem;
}

.pp-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.15rem 1.3rem;
    margin-bottom: 0.85rem;
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
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.pp-badge-verified { background: #ccfbf1; color: #0f766e; }
.pp-badge-missing { background: #fee2e2; color: #b91c1c; }
.pp-badge-review { background: #ffedd5; color: #c2410c; }
.pp-badge-na { background: #f1f5f9; color: #475569; }
.pp-badge-ok { background: #dcfce7; color: #166534; }
.pp-badge-warn { background: #fef3c7; color: #92400e; }

.pp-step-label {
    color: #0f172a;
    font-weight: 650;
    font-size: 1.08rem;
    margin-bottom: 0.35rem;
}
.pp-help {
    color: #64748b;
    font-size: 0.88rem;
    margin-bottom: 0.75rem;
}
.pp-examples {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin: 0 0 1.35rem 0;
}
.pp-ex {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 0.95rem 1.05rem;
}
.pp-ex h3 {
    margin: 0 0 0.45rem 0;
    font-size: 0.92rem;
    color: #0f172a;
}
.pp-ex ul {
    margin: 0;
    padding-left: 1.1rem;
    color: #475569;
    font-size: 0.84rem;
    line-height: 1.45;
}
@media (max-width: 900px) {
    .pp-examples { grid-template-columns: 1fr; }
}
.pp-muted { color: #64748b; font-size: 0.88rem; }

.pp-doc-card {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 0.9rem 1rem;
    background: #ffffff;
    margin-bottom: 0.55rem;
}
.pp-doc-name { color: #0f172a; font-weight: 600; }
.pp-empty {
    border: 1px dashed #cbd5e1;
    background: #f8fafc;
    border-radius: 14px;
    padding: 1.1rem 1.2rem;
    color: #64748b;
    font-size: 0.92rem;
    margin-bottom: 0.8rem;
}
.pp-quote {
    background: #f8fafc;
    border-left: 3px solid #14b8a6;
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 0.9rem;
    color: #334155;
    font-size: 0.9rem;
    margin: 0.4rem 0 0.8rem;
}

.pp-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 0.82rem;
    margin-top: 2.5rem;
    padding-top: 1rem;
    border-top: 1px solid #e2e8f0;
}

.pp-sidebar-brand {
    font-weight: 700;
    letter-spacing: -0.03em;
    font-size: 1.05rem;
    color: #f8fafc !important;
    margin-bottom: 0.15rem;
}
</style>
"""
