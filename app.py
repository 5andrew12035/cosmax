import streamlit as st
import pandas as pd
from pathlib import Path

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="INCI Finder · COSMAX R&I",
    page_icon="🧪",
    layout="centered",
)

DATA_PATH = Path(__file__).parent / "data" / "inci_data.csv"

COUNTRY_CODES = ["KR", "EU", "CN", "US"]
COUNTRY_LABEL = {
    "KR": "대한민국",
    "EU": "유럽연합",
    "CN": "중국",
    "US": "미국",
}
STATUS_LABEL = {"safe": "안전", "caution": "주의", "restricted": "제한"}
STATUS_COLOR = {
    "safe": {"bg": "#E1F5F3", "border": "rgba(14,165,164,0.25)", "accent": "#0EA5A4"},
    "caution": {"bg": "#FEF0D9", "border": "rgba(245,158,11,0.3)", "accent": "#F59E0B"},
    "restricted": {"bg": "#FBE4DE", "border": "rgba(176,67,47,0.28)", "accent": "#B0432F"},
}


# ----------------------------------------------------------------------------
# 데이터 로드
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df["allergen"] = df["allergen"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def to_title_case(inci: str) -> str:
    return " ".join(w.capitalize() for w in str(inci).split(" "))


def normalize(s: str) -> str:
    return str(s).lower().replace(" ", "")


def find_matches(df: pd.DataFrame, query: str) -> pd.DataFrame:
    q = normalize(query)
    if not q:
        return df.iloc[0:0]
    mask = (
        df["name"].apply(normalize).str.contains(q, na=False)
        | df["inci"].apply(normalize).str.contains(q, na=False)
        | df["aliases"].fillna("").apply(normalize).str.contains(q, na=False)
    )
    return df[mask]


# ----------------------------------------------------------------------------
# 스타일
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .block-container{
        max-width: 820px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .if-eyebrow{
        display:inline-block;
        background:#E1F5F3;
        color:#0EA5A4;
        font-size:13px;
        font-weight:600;
        padding:6px 16px;
        border-radius:20px;
        margin-bottom:14px;
    }
    .if-title{
        font-size:44px;
        font-weight:800;
        letter-spacing:-0.02em;
        margin:0 0 10px 0;
        background:linear-gradient(135deg, #0EA5A4, #2563EB);
        -webkit-background-clip:text;
        background-clip:text;
        color:transparent;
    }
    .if-underline{
        width:52px;
        height:5px;
        margin:0 0 18px 0;
        border-radius:4px;
        background:linear-gradient(135deg, #0EA5A4, #2563EB);
    }
    .if-sub{
        color:#5A6E6B;
        font-size:16px;
        line-height:1.7;
        margin-bottom: 4px;
    }
    .if-header-row{
        display:flex;
        align-items:center;
        justify-content:space-between;
        margin-bottom: 8px;
    }
    .if-brand{
        display:flex;
        align-items:center;
        gap:10px;
        font-weight:700;
        font-size:16px;
        color:#1B2E2C;
    }
    .if-brand-mark{
        width:28px;height:28px;
        border-radius:8px;
        background:linear-gradient(135deg, #0EA5A4, #2563EB);
        display:flex;align-items:center;justify-content:center;
        color:#fff;
        font-weight:700;
        font-size:12px;
    }
    .if-eyebrow-tag{
        font-size:12px;
        font-weight:500;
        letter-spacing:0.08em;
        color:#5A6E6B;
        text-transform:uppercase;
    }

    .result-head h2{
        font-size:26px;
        font-weight:800;
        margin:0 0 2px 0;
        color:#1B2E2C;
    }
    .result-inci{
        font-size:14px;
        color:#5A6E6B;
        margin-bottom:10px;
    }
    .tag{
        display:inline-block;
        font-size:13px;
        font-weight:600;
        padding:5px 12px;
        border-radius:20px;
        margin-right:6px;
        margin-bottom:10px;
    }
    .tag-category{ background:#E4ECFB; color:#2563EB; }
    .tag-allergen{ background:#FEF0D9; color:#F59E0B; }
    .tag-safe{ background:#E1F5F3; color:#0EA5A4; }

    .compare-card{
        border-radius:12px;
        padding:16px 18px;
        margin-bottom:12px;
        border:1px solid transparent;
    }
    .compare-top{
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:10px;
        margin-bottom: 8px;
    }
    .compare-country{
        font-weight:700;
        font-size:15px;
        color:#1B2E2C;
    }
    .compare-code{
        display:block;
        font-size:12px;
        color:#5A6E6B;
        font-weight:400;
        letter-spacing:.04em;
    }
    .compare-badge{
        font-size:11px;
        font-weight:700;
        color:#fff;
        padding:3px 10px;
        border-radius:20px;
        letter-spacing:.02em;
        white-space:nowrap;
    }
    .compare-limit{
        font-size:20px;
        font-weight:800;
        margin-bottom:6px;
    }
    .compare-note{
        font-size:14px;
        color:#5A6E6B;
        line-height:1.6;
    }

    .if-disclaimer{
        margin-top:10px;
        font-size:13px;
        color:#5A6E6B;
        background:#E4ECFB;
        border-radius:10px;
        padding:12px 16px;
        line-height:1.6;
    }

    .if-empty{
        margin-top:40px;
        text-align:center;
        color:#5A6E6B;
    }

    div.stButton > button{
        border-radius:20px;
        border:1.5px solid #0EA5A4;
        background:#E1F5F3;
        color:#0EA5A4;
        font-weight:600;
        font-size:14px;
        padding:2px 14px;
    }
    div.stButton > button:hover{
        background:#0EA5A4;
        color:#fff;
        border-color:#0EA5A4;
    }

    [data-testid="stAppViewContainer"] > .main{
        position:relative;
    }
    [data-testid="stAppViewContainer"] > .main::before{
        content:"";
        position:absolute;
        inset:0;
        z-index:0;
        pointer-events:none;
        background-repeat:no-repeat, no-repeat;
        background-position: right -60px bottom -60px, left -60px bottom -40px;
        background-size: clamp(220px,34vw,420px) auto, clamp(240px,38vw,460px) auto;
        opacity:0.75;
        background-image:
            url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDAgMzgwIiBmaWxsPSJub25lIj4KICA8ZGVmcz4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iY2FyYm9uQSIgY3g9IjMyJSIgY3k9IjI2JSIgcj0iNzIlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzZFNkU2RSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjU1JSIgc3RvcC1jb2xvcj0iIzJCMkIyQiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwQjBCMEIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9Im94eWdlbkEiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNFQThCODQiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI1NSUiIHN0b3AtY29sb3I9IiNDMjNCMkUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNzExRTE1Ii8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJoeWRyb2dlbkEiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI2MCUiIHN0b3AtY29sb3I9IiNFRUYwRjEiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjQzlDREQwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJyb2RBIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0Q4REFEQyIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM2RDcyNzUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJzaGFkb3dBIiB4PSItMzAlIiB5PSItMzAlIiB3aWR0aD0iMTYwJSIgaGVpZ2h0PSIxNjAlIj4KICAgICAgPGZlRHJvcFNoYWRvdyBkeD0iMCIgZHk9IjYiIHN0ZERldmlhdGlvbj0iOCIgZmxvb2QtY29sb3I9IiMxQTFBMUEiIGZsb29kLW9wYWNpdHk9IjAuMzUiLz4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8ZyBmaWx0ZXI9InVybCgjc2hhZG93QSkiPgogICAgPGcgc3Ryb2tlPSJ1cmwoI3JvZEEpIiBzdHJva2Utd2lkdGg9IjYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+CiAgICAgIDxsaW5lIHgxPSI5MCIgeTE9IjEyMCIgeDI9IjE3MCIgeTI9IjcwIi8+CiAgICAgIDxsaW5lIHgxPSIxNzAiIHkxPSI3MCIgeDI9IjI1MCIgeTI9IjEyMCIvPgogICAgICA8bGluZSB4MT0iMjUwIiB5MT0iMTIwIiB4Mj0iMjUwIiB5Mj0iMjEwIi8+CiAgICAgIDxsaW5lIHgxPSIyNTAiIHkxPSIyMTAiIHgyPSIxNzAiIHkyPSIyNjAiLz4KICAgICAgPGxpbmUgeDE9IjE3MCIgeTE9IjI2MCIgeDI9IjkwIiB5Mj0iMjEwIi8+CiAgICAgIDxsaW5lIHgxPSI5MCIgeTE9IjIxMCIgeDI9IjkwIiB5Mj0iMTIwIi8+CiAgICAgIDxsaW5lIHgxPSIyNTAiIHkxPSIxMjAiIHgyPSIzMzAiIHkyPSI4MCIvPgogICAgICA8bGluZSB4MT0iMjUwIiB5MT0iMjEwIiB4Mj0iMzM1IiB5Mj0iMjQ1Ii8+CiAgICAgIDxsaW5lIHgxPSIxNzAiIHkxPSIyNjAiIHgyPSIxODAiIHkyPSIzNDUiLz4KICAgIDwvZz4KICAgIDxjaXJjbGUgY3g9IjkwIiBjeT0iMTIwIiByPSIxNCIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgICA8Y2lyY2xlIGN4PSIxNzAiIGN5PSI3MCIgcj0iMTkiIGZpbGw9InVybCgjb3h5Z2VuQSkiLz4KICAgIDxjaXJjbGUgY3g9IjI1MCIgY3k9IjEyMCIgcj0iMTYiIGZpbGw9InVybCgjY2FyYm9uQSkiLz4KICAgIDxjaXJjbGUgY3g9IjI1MCIgY3k9IjIxMCIgcj0iMTYiIGZpbGw9InVybCgjY2FyYm9uQSkiLz4KICAgIDxjaXJjbGUgY3g9IjE3MCIgY3k9IjI2MCIgcj0iMTkiIGZpbGw9InVybCgjb3h5Z2VuQSkiLz4KICAgIDxjaXJjbGUgY3g9IjkwIiBjeT0iMjEwIiByPSIxNCIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgICA8Y2lyY2xlIGN4PSIzMzAiIGN5PSI4MCIgcj0iMTIiIGZpbGw9InVybCgjaHlkcm9nZW5BKSIgc3Ryb2tlPSIjQjlCRUMyIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogICAgPGNpcmNsZSBjeD0iMzM1IiBjeT0iMjQ1IiByPSIxNCIgZmlsbD0idXJsKCNveHlnZW5BKSIvPgogICAgPGNpcmNsZSBjeD0iMTgwIiBjeT0iMzQ1IiByPSIxMiIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPC9nPgo8L3N2Zz4K"),
            url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzNjAgMzIwIiBmaWxsPSJub25lIj4KICA8ZGVmcz4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iY2FyYm9uQiIgY3g9IjMyJSIgY3k9IjI2JSIgcj0iNzIlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzZFNkU2RSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjU1JSIgc3RvcC1jb2xvcj0iIzJCMkIyQiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwQjBCMEIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9Im94eWdlbkIiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNFQThCODQiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI1NSUiIHN0b3AtY29sb3I9IiNDMjNCMkUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNzExRTE1Ii8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJoeWRyb2dlbkIiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI2MCUiIHN0b3AtY29sb3I9IiNFRUYwRjEiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjQzlDREQwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJyb2RCIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0Q4REFEQyIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM2RDcyNzUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJzaGFkb3dCIiB4PSItMzAlIiB5PSItMzAlIiB3aWR0aD0iMTYwJSIgaGVpZ2h0PSIxNjAlIj4KICAgICAgPGZlRHJvcFNoYWRvdyBkeD0iMCIgZHk9IjYiIHN0ZERldmlhdGlvbj0iOCIgZmxvb2QtY29sb3I9IiMxQTFBMUEiIGZsb29kLW9wYWNpdHk9IjAuMzUiLz4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8ZyBmaWx0ZXI9InVybCgjc2hhZG93QikiPgogICAgPGcgc3Ryb2tlPSJ1cmwoI3JvZEIpIiBzdHJva2Utd2lkdGg9IjYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+CiAgICAgIDxsaW5lIHgxPSI2MCIgeTE9IjkwIiB4Mj0iMTQwIiB5Mj0iNjAiLz4KICAgICAgPGxpbmUgeDE9IjE0MCIgeTE9IjYwIiB4Mj0iMjAwIiB5Mj0iMTIwIi8+CiAgICAgIDxsaW5lIHgxPSIyMDAiIHkxPSIxMjAiIHgyPSIxODAiIHkyPSIyMDAiLz4KICAgICAgPGxpbmUgeDE9IjE4MCIgeTE9IjIwMCIgeDI9IjEwMCIgeTI9IjIyMCIvPgogICAgICA8bGluZSB4MT0iMTAwIiB5MT0iMjIwIiB4Mj0iNjAiIHkyPSI5MCIvPgogICAgICA8bGluZSB4MT0iMjAwIiB5MT0iMTIwIiB4Mj0iMjgwIiB5Mj0iMTAwIi8+CiAgICA8L2c+CiAgICA8Y2lyY2xlIGN4PSI2MCIgY3k9IjkwIiByPSIxMyIgZmlsbD0idXJsKCNoeWRyb2dlbkIpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgICA8Y2lyY2xlIGN4PSIxNDAiIGN5PSI2MCIgcj0iMTgiIGZpbGw9InVybCgjb3h5Z2VuQikiLz4KICAgIDxjaXJjbGUgY3g9IjIwMCIgY3k9IjEyMCIgcj0iMTUiIGZpbGw9InVybCgjY2FyYm9uQikiLz4KICAgIDxjaXJjbGUgY3g9IjE4MCIgY3k9IjIwMCIgcj0iMTMiIGZpbGw9InVybCgjaHlkcm9nZW5CKSIgc3Ryb2tlPSIjQjlCRUMyIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogICAgPGNpcmNsZSBjeD0iMTAwIiBjeT0iMjIwIiByPSIxOCIgZmlsbD0idXJsKCNveHlnZW5CKSIvPgogICAgPGNpcmNsZSBjeD0iMjgwIiBjeT0iMTAwIiByPSIxMyIgZmlsbD0idXJsKCNoeWRyb2dlbkIpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPC9nPgo8L3N2Zz4K");
    }
    [data-testid="stAppViewContainer"] > .main .block-container{
        position:relative;
        z-index:1;
    }
    @media (max-width:700px){
        [data-testid="stAppViewContainer"] > .main::before{
            background-image: url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDAgMzgwIiBmaWxsPSJub25lIj4KICA8ZGVmcz4KICAgIDxyYWRpYWxHcmFkaWVudCBpZD0iY2FyYm9uQSIgY3g9IjMyJSIgY3k9IjI2JSIgcj0iNzIlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iIzZFNkU2RSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjU1JSIgc3RvcC1jb2xvcj0iIzJCMkIyQiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiMwQjBCMEIiLz4KICAgIDwvcmFkaWFsR3JhZGllbnQ+CiAgICA8cmFkaWFsR3JhZGllbnQgaWQ9Im94eWdlbkEiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNFQThCODQiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI1NSUiIHN0b3AtY29sb3I9IiNDMjNCMkUiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjNzExRTE1Ii8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPHJhZGlhbEdyYWRpZW50IGlkPSJoeWRyb2dlbkEiIGN4PSIzMiUiIGN5PSIyNiUiIHI9IjcyJSI+CiAgICAgIDxzdG9wIG9mZnNldD0iMCUiIHN0b3AtY29sb3I9IiNGRkZGRkYiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSI2MCUiIHN0b3AtY29sb3I9IiNFRUYwRjEiLz4KICAgICAgPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdG9wLWNvbG9yPSIjQzlDREQwIi8+CiAgICA8L3JhZGlhbEdyYWRpZW50PgogICAgPGxpbmVhckdyYWRpZW50IGlkPSJyb2RBIiB4MT0iMCUiIHkxPSIwJSIgeDI9IjEwMCUiIHkyPSIxMDAlIj4KICAgICAgPHN0b3Agb2Zmc2V0PSIwJSIgc3RvcC1jb2xvcj0iI0Q4REFEQyIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEwMCUiIHN0b3AtY29sb3I9IiM2RDcyNzUiLz4KICAgIDwvbGluZWFyR3JhZGllbnQ+CiAgICA8ZmlsdGVyIGlkPSJzaGFkb3dBIiB4PSItMzAlIiB5PSItMzAlIiB3aWR0aD0iMTYwJSIgaGVpZ2h0PSIxNjAlIj4KICAgICAgPGZlRHJvcFNoYWRvdyBkeD0iMCIgZHk9IjYiIHN0ZERldmlhdGlvbj0iOCIgZmxvb2QtY29sb3I9IiMxQTFBMUEiIGZsb29kLW9wYWNpdHk9IjAuMzUiLz4KICAgIDwvZmlsdGVyPgogIDwvZGVmcz4KICA8ZyBmaWx0ZXI9InVybCgjc2hhZG93QSkiPgogICAgPGcgc3Ryb2tlPSJ1cmwoI3JvZEEpIiBzdHJva2Utd2lkdGg9IjYiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCI+CiAgICAgIDxsaW5lIHgxPSI5MCIgeTE9IjEyMCIgeDI9IjE3MCIgeTI9IjcwIi8+CiAgICAgIDxsaW5lIHgxPSIxNzAiIHkxPSI3MCIgeDI9IjI1MCIgeTI9IjEyMCIvPgogICAgICA8bGluZSB4MT0iMjUwIiB5MT0iMTIwIiB4Mj0iMjUwIiB5Mj0iMjEwIi8+CiAgICAgIDxsaW5lIHgxPSIyNTAiIHkxPSIyMTAiIHgyPSIxNzAiIHkyPSIyNjAiLz4KICAgICAgPGxpbmUgeDE9IjE3MCIgeTE9IjI2MCIgeDI9IjkwIiB5Mj0iMjEwIi8+CiAgICAgIDxsaW5lIHgxPSI5MCIgeTE9IjIxMCIgeDI9IjkwIiB5Mj0iMTIwIi8+CiAgICAgIDxsaW5lIHgxPSIyNTAiIHkxPSIxMjAiIHgyPSIzMzAiIHkyPSI4MCIvPgogICAgICA8bGluZSB4MT0iMjUwIiB5MT0iMjEwIiB4Mj0iMzM1IiB5Mj0iMjQ1Ii8+CiAgICAgIDxsaW5lIHgxPSIxNzAiIHkxPSIyNjAiIHgyPSIxODAiIHkyPSIzNDUiLz4KICAgIDwvZz4KICAgIDxjaXJjbGUgY3g9IjkwIiBjeT0iMTIwIiByPSIxNCIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgICA8Y2lyY2xlIGN4PSIxNzAiIGN5PSI3MCIgcj0iMTkiIGZpbGw9InVybCgjb3h5Z2VuQSkiLz4KICAgIDxjaXJjbGUgY3g9IjI1MCIgY3k9IjEyMCIgcj0iMTYiIGZpbGw9InVybCgjY2FyYm9uQSkiLz4KICAgIDxjaXJjbGUgY3g9IjI1MCIgY3k9IjIxMCIgcj0iMTYiIGZpbGw9InVybCgjY2FyYm9uQSkiLz4KICAgIDxjaXJjbGUgY3g9IjE3MCIgY3k9IjI2MCIgcj0iMTkiIGZpbGw9InVybCgjb3h5Z2VuQSkiLz4KICAgIDxjaXJjbGUgY3g9IjkwIiBjeT0iMjEwIiByPSIxNCIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgICA8Y2lyY2xlIGN4PSIzMzAiIGN5PSI4MCIgcj0iMTIiIGZpbGw9InVybCgjaHlkcm9nZW5BKSIgc3Ryb2tlPSIjQjlCRUMyIiBzdHJva2Utd2lkdGg9IjEuNSIvPgogICAgPGNpcmNsZSBjeD0iMzM1IiBjeT0iMjQ1IiByPSIxNCIgZmlsbD0idXJsKCNveHlnZW5BKSIvPgogICAgPGNpcmNsZSBjeD0iMTgwIiBjeT0iMzQ1IiByPSIxMiIgZmlsbD0idXJsKCNoeWRyb2dlbkEpIiBzdHJva2U9IiNCOUJFQzIiIHN0cm9rZS13aWR0aD0iMS41Ii8+CiAgPC9nPgo8L3N2Zz4K");
            background-position: right -80px bottom -80px;
            background-size: clamp(220px,44vw,340px) auto;
        }
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"]{
        border-radius:16px;
        border:1.5px solid rgba(14,165,164,0.3);
        box-shadow: 0 1px 2px rgba(27,46,44,0.04), 0 6px 20px rgba(27,46,44,0.05);
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within{
        border-color:#0EA5A4;
        box-shadow:0 0 0 4px #E1F5F3;
    }
    div[data-testid="stTextInput"] input{
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%235A6E6B' stroke-width='2'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
        background-repeat:no-repeat;
        background-position:16px center;
        padding-left:44px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# 세션 상태
# ----------------------------------------------------------------------------
if "recent" not in st.session_state:
    st.session_state.recent = []
if "selected_name" not in st.session_state:
    st.session_state.selected_name = None
if "query" not in st.session_state:
    st.session_state.query = ""


def select_item(name: str):
    st.session_state.selected_name = name
    st.session_state.query = name
    if name in st.session_state.recent:
        st.session_state.recent.remove(name)
    st.session_state.recent.insert(0, name)
    st.session_state.recent = st.session_state.recent[:5]


# ----------------------------------------------------------------------------
# 데이터
# ----------------------------------------------------------------------------
if not DATA_PATH.exists():
    st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    st.stop()

df = load_data(DATA_PATH)

# ----------------------------------------------------------------------------
# 헤더
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="if-header-row">
        <div class="if-brand">
            <div class="if-brand-mark">Ci</div>
            <div>INCI Finder</div>
        </div>
        <div class="if-eyebrow-tag">COSMAX R&amp;I Unit</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center;">
        <span class="if-eyebrow">원료 하나, 국가별 기준 한 번에</span>
        <div class="if-title">INCI Finder</div>
        <div class="if-underline" style="margin-left:auto;margin-right:auto;"></div>
        <p class="if-sub">원료명 또는 INCI명을 검색하면 한국·EU·중국·미국 배합한도와<br>
        알러젠 여부를 표로 비교해서 보여드려요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# 검색창
# ----------------------------------------------------------------------------
search_col, btn_col = st.columns([5, 1])
with search_col:
    query = st.text_input(
        "search",
        value=st.session_state.query,
        placeholder="예: 나이아신아마이드, Salicylic Acid ...",
        label_visibility="collapsed",
    )
with btn_col:
    search_clicked = st.button("검색", use_container_width=True)

if query != st.session_state.query:
    st.session_state.query = query
    st.session_state.selected_name = None

matches = find_matches(df, st.session_state.query)

# 자동완성 제안 (입력 중이고 후보가 여러 개일 때)
if st.session_state.query and st.session_state.selected_name is None and len(matches) > 0:
    st.caption("추천 검색어")
    for _, row in matches.head(5).iterrows():
        label = f"{row['name']} ({to_title_case(row['inci'])})"
        if st.button(label, key=f"suggest_{row['name']}", use_container_width=True):
            select_item(row["name"])
            st.rerun()

if search_clicked and st.session_state.query and len(matches) > 0:
    select_item(matches.iloc[0]["name"])
    st.rerun()

# ----------------------------------------------------------------------------
# 최근 검색어 칩
# ----------------------------------------------------------------------------
if st.session_state.recent:
    st.write("")
    st.caption("최근 검색한 원료")
    chip_cols = st.columns(len(st.session_state.recent))
    for col, name in zip(chip_cols, st.session_state.recent):
        row = df[df["name"] == name]
        if row.empty:
            continue
        row = row.iloc[0]
        with col:
            if st.button(
                f"{row['name']}",
                key=f"chip_{name}",
                use_container_width=True,
            ):
                select_item(name)
                st.rerun()

st.divider()

# ----------------------------------------------------------------------------
# 결과 영역
# ----------------------------------------------------------------------------
selected_row = None
if st.session_state.selected_name:
    sel = df[df["name"] == st.session_state.selected_name]
    if not sel.empty:
        selected_row = sel.iloc[0]

if selected_row is None:
    if st.session_state.query:
        st.markdown(
            f"""
            <div class="if-empty">
                <p>"{st.session_state.query}"에 대한 검색 결과가 없습니다.<br>
                원료명 또는 INCI명을 다시 확인해 주세요.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="if-empty">
                <p>원료명을 입력하면 결과가 여기에 표시됩니다.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    item = selected_row
    allergen_tag = (
        '<span class="tag tag-allergen">알러젠 표기 대상</span>'
        if item["allergen"]
        else '<span class="tag tag-safe">알러젠 표기 비대상</span>'
    )

    st.markdown(
        f"""
        <div class="result-head">
            <h2>{item['name']} ({to_title_case(item['inci'])})</h2>
            <div class="result-inci">INCI · {item['inci']}</div>
            <div>
                <span class="tag tag-category">{item['category']}</span>
                {allergen_tag}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(2)
    for i, code in enumerate(COUNTRY_CODES):
        status = item[f"{code}_status"]
        limit = item[f"{code}_limit"]
        note = item[f"{code}_note"]
        colors = STATUS_COLOR.get(status, STATUS_COLOR["safe"])
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="compare-card" style="background:{colors['bg']};border-color:{colors['border']};">
                    <div class="compare-top">
                        <div class="compare-country">{COUNTRY_LABEL[code]}<span class="compare-code">{code}</span></div>
                        <span class="compare-badge" style="background:{colors['accent']};">{STATUS_LABEL.get(status, status)}</span>
                    </div>
                    <div class="compare-limit" style="color:{colors['accent']};">{limit}</div>
                    <div class="compare-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="if-disclaimer">
            ⚠ 현재 표시되는 배합한도는 실습용 샘플 데이터입니다. 실제 업무 적용 전 최신 규정 자료로 반드시 재확인해 주세요.
        </div>
        """,
        unsafe_allow_html=True,
    )
