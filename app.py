import streamlit as st
from openai import OpenAI
import time
from datetime import datetime
from io import BytesIO
import re

# PDF
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# 한글 폰트
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =========================
# OpenRouter 설정
# =========================

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

# =========================
# 페이지 설정
# =========================

st.set_page_config(
    page_title="AI 회의록 요약 시스템",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# 세션 상태
# =========================

if "result" not in st.session_state:
    st.session_state.result = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "processing" not in st.session_state:
    st.session_state.processing = False

# =========================
# 초기화
# =========================

def reset_content():

    if not st.session_state.processing:
        st.session_state["meeting_input"] = ""
        st.session_state.result = ""

# =========================
# PDF 생성 함수
# =========================

def create_pdf(text):

    buffer = BytesIO()

    try:
        pdfmetrics.registerFont(
            TTFont("Malgun", "malgun.ttf")
        )
        font_name = "Malgun"

    except:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    styles["Title"].fontName = font_name
    styles["BodyText"].fontName = font_name

    story = []

    title = Paragraph(
        "<b>AI 회의 분석 보고서</b>",
        styles["Title"]
    )

    story.append(title)
    story.append(Spacer(1, 20))

    clean_text = re.sub(r'[#*`>-]', '', text)

    content = clean_text.replace("\n", "<br/>")

    paragraph = Paragraph(
        content,
        styles["BodyText"]
    )

    story.append(paragraph)

    doc.build(story)

    buffer.seek(0)

    return buffer

# =========================
# CSS
# =========================

st.markdown("""
<style>

/* =========================
   기본 배경
========================= */

.stApp {
    background:
        radial-gradient(circle at top left, #1e293b 0%, #0f172a 45%),
        radial-gradient(circle at bottom right, #111827 0%, #020617 50%);
    color: #f8fafc;
}

/* 상단 흰색 제거 */

header[data-testid="stHeader"] {
    background: transparent;
    height: 0px;
}

[data-testid="stToolbar"] {
    right: 1rem;
}

.block-container {
    max-width: 1500px;
    padding-top: 1rem;
}

/* =========================
   헤더 스타일
========================= */

.main-title {
    font-size: 58px;
    font-weight: 900;
    background: linear-gradient(
        90deg,
        #ffffff,
        #60a5fa,
        #a78bfa
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.sub-text {
    color: #94a3b8;
    font-size: 18px;
    margin-bottom: 35px;
    opacity: 0.9;
}

.ai-badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background:
        linear-gradient(
            135deg,
            rgba(37,99,235,0.25),
            rgba(124,58,237,0.25)
        );
    border: 1px solid rgba(148,163,184,0.15);
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 18px;
}

/* =========================
   카드 스타일
========================= */

.glass-card {
    background: rgba(15, 23, 42, 0.72);
    backdrop-filter: blur(16px);
    border-radius: 24px;
    padding: 28px;
    border: 1px solid rgba(148,163,184,0.1);
    box-shadow:
        0 0 40px rgba(37,99,235,0.08);
}

.result-container {
    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,0.92),
            rgba(2,6,23,0.92)
        );

    border-radius: 28px;
    padding: 35px;
    border: 1px solid rgba(148,163,184,0.15);

    border-top: 3px solid rgba(96,165,250,0.7);

    line-height: 1.9;
    margin-top: 15px;

    box-shadow:
        0 0 40px rgba(37,99,235,0.08);

    animation: fadeUp 0.4s ease;
}

/* =========================
   결과 텍스트 스타일
========================= */

.result-container h1,
.result-container h2,
.result-container h3 {
    color: white !important;
    margin-top: 25px;
    margin-bottom: 15px;
    font-weight: 700;
}

.result-container p,
.result-container li {
    color: #e2e8f0 !important;
    font-size: 16px;
}

/* =========================
   입력창
========================= */

.stTextArea textarea {
    background: rgba(15,23,42,0.78) !important;
    color: white !important;

    border-radius: 20px !important;
    padding: 20px !important;

    border: 1px solid rgba(148,163,184,0.1) !important;

    font-size: 16px !important;
    line-height: 1.7 !important;
}

/* placeholder 개선 */

.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
    font-size: 16px !important;
}

/* 포커스 효과 */

.stTextArea textarea:focus {
    border: 1px solid rgba(96,165,250,0.7) !important;

    box-shadow:
        0 0 20px rgba(96,165,250,0.2) !important;
}

/* =========================
   버튼
========================= */

.stButton button {
    height: 52px;
    border-radius: 14px;

    border: none !important;

    font-weight: bold !important;
    letter-spacing: 0.5px;

    color: white !important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        ) !important;

    transition: all 0.25s ease !important;
}

.stButton button:hover {

    transform:
        translateY(-3px)
        scale(1.01);

    box-shadow:
        0 0 25px rgba(124,58,237,0.45);
}

.stDownloadButton button {
    height: 52px;

    border-radius: 14px;

    border: none !important;

    font-weight: bold !important;

    color: white !important;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        ) !important;

    transition: all 0.25s ease !important;
}

.stDownloadButton button:hover {

    transform:
        translateY(-3px)
        scale(1.01);

    box-shadow:
        0 0 25px rgba(37,99,235,0.45);
}

/* =========================
   사이드바
========================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(15,23,42,0.98),
            rgba(2,6,23,0.98)
        ) !important;

    border-right:
        1px solid rgba(148,163,184,0.12);

    box-shadow:
        8px 0 30px rgba(0,0,0,0.35);
}

/* 사이드바 내부 */

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

/* 분석 히스토리 제목 */

.sidebar-title {
    font-size: 24px;
    font-weight: 800;
    color: white;
    margin-bottom: 18px;

    border-bottom:
        1px solid rgba(148,163,184,0.15);

    padding-bottom: 12px;

    letter-spacing: -0.3px;
}

/* 검색창 */

[data-testid="stSidebar"] .stTextInput input {

    background: rgba(30,41,59,0.9) !important;

    color: white !important;

    border-radius: 12px !important;

    border:
        1px solid rgba(148,163,184,0.15) !important;
}

/* 히스토리 버튼 */

section[data-testid="stSidebar"] .stButton button {

    white-space: normal !important;

    height: auto !important;

    min-height: 80px !important;

    text-align: left !important;

    padding: 14px !important;

    line-height: 1.5 !important;

    overflow: hidden !important;

    background:
        rgba(30,41,59,0.72) !important;

    border:
        1px solid rgba(148,163,184,0.08) !important;
}

/* 히스토리 버튼 hover */

section[data-testid="stSidebar"] .stButton button:hover {

    background:
        rgba(51,65,85,0.9) !important;

    transform: translateY(-2px);
}

/* =========================
   사이드바 토글 버튼
========================= */

button[kind="header"] {

    background-color:
        rgba(15,23,42,0.9) !important;

    color: white !important;

    border-radius: 12px !important;

    border:
        1px solid rgba(255,255,255,0.1) !important;

    width: 48px !important;

    height: 48px !important;
}

button[kind="header"]:hover {

    background-color:
        rgba(37,99,235,0.9) !important;

    color: white !important;
}

button[kind="header"] svg {

    color: white !important;

    fill: white !important;
}

/* 접힌 상태 텍스트 */

button[kind="headerCollapsedControl"]::after {

    content: "  >> 히스토리";

    color: white;

    font-size: 14px;

    font-weight: 700;

    margin-left: 8px;

    white-space: nowrap;
}

button[kind="headerCollapsedControl"] svg {

    fill: white !important;

    color: white !important;
}

/* =========================
   애니메이션
========================= */

@keyframes fadeUp {

    from {
        opacity: 0;
        transform: translateY(15px);
    }

    to {
        opacity: 1;
        transform: translateY(0px);
    }
}

</style>
""", unsafe_allow_html=True)

# =========================
# 사이드바
# =========================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">📂 분석 히스토리</div>',
        unsafe_allow_html=True
    )

    search_text = st.text_input(
        "검색",
        placeholder="회의 내용 검색...",
        disabled=st.session_state.processing
    )

    if not st.session_state.history:

        st.info("저장된 기록이 없습니다.")

    else:

        for i, item in enumerate(reversed(st.session_state.history)):

            if search_text.strip():

                if search_text.lower() not in item["title"].lower():
                    continue

            short_title = (
                item["title"][:28] + "..."
                if len(item["title"]) > 28
                else item["title"]
            )

            if st.button(
                f"⏰ {item['time']}\n\n{short_title}",
                key=f"hist_{i}",
                disabled=st.session_state.processing,
                use_container_width=True
            ):

                st.session_state["meeting_input"] = item["content"]
                st.session_state.result = item["result"]

                st.rerun()

# =========================
# 메인
# =========================

st.markdown(
    """
    <div class="ai-badge">
        ✨ AI POWERED MEETING ANALYSIS
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-title">🧠 AI 회의록 요약 시스템</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-text">업무 효율화를 위한 AI 기반 회의 분석 플랫폼</div>',
    unsafe_allow_html=True
)

left, right = st.columns([1.2, 1])

# =========================
# 입력 영역
# =========================

with left:

    st.markdown("### 🖋️ 회의록 입력")

    meeting_text = st.text_area(
        "입력",
        height=380,
        label_visibility="collapsed",
        placeholder="회의 내용을 입력하세요...",
        key="meeting_input",
        disabled=st.session_state.processing
    )

# =========================
# 우측 영역
# =========================

with right:

    st.markdown("### 📌 시스템 안내")

    st.info("""
    ✅ 회의 핵심 요약  
    ✅ 주요 결정 사항  
    ✅ 액션 아이템  
    ✅ 리스크 분석  
    ✅ 상사 보고 브리핑
    """)

    analyze = st.button(
        "🚀 AI 분석 시작",
        use_container_width=True,
        disabled=st.session_state.processing
    )

    st.button(
        "🔄 입력 초기화",
        on_click=reset_content,
        use_container_width=True,
        disabled=st.session_state.processing
    )

# =========================
# 분석 실행
# =========================

if analyze:

    if not meeting_text.strip():

        st.warning("회의 내용을 입력해주세요.")

    else:

        st.session_state.processing = True

        progress_bar = st.progress(0)

        status_text = st.empty()

        try:

            fake_progress = 0.0

            while fake_progress < 95.0:

                fake_progress += 0.7

                progress_bar.progress(int(fake_progress))

                status_text.markdown(
                    f"### 🤖 AI 분석 진행 중... {fake_progress:.1f}%"
                )

                time.sleep(0.03)

            response = client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": """
회의록을 전문적으로 분석해줘.

1. 📌 핵심 요약
2. 💎 주요 결정 사항
3. 🚀 액션 아이템
4. ⚠️ 리스크 및 고려사항
5. 👔 상사 보고 브리핑
"""
                    },
                    {
                        "role": "user",
                        "content": meeting_text
                    }
                ]
            )

            result_content = response.choices[0].message.content

            result_content = result_content.replace("```markdown", "")
            result_content = result_content.replace("```", "")

            progress_bar.progress(100)

            status_text.markdown(
                "### ✅ AI 분석 완료! 100.0%"
            )

            st.session_state.result = result_content

            history_data = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "title": meeting_text[:40],
                "content": meeting_text,
                "result": result_content
            }

            st.session_state.history.append(history_data)

            time.sleep(0.5)

            st.session_state.processing = False

            st.rerun()

        except Exception as e:

            st.session_state.processing = False

            st.error(f"오류 발생: {e}")

# =========================
# 결과 출력
# =========================

if st.session_state.result:

    st.divider()

    st.markdown("## 📊 분석 결과")

    clean_result = st.session_state.result.replace("```markdown", "")
    clean_result = clean_result.replace("```", "")

    with st.container():

        st.markdown(clean_result)

    st.markdown("## 💾 다운로드")

    pdf_data = create_pdf(clean_result)

    col1, col2 = st.columns(2)

    file_name = f"회의록_분석_{datetime.now().strftime('%Y%m%d_%H%M')}"

    with col1:

        st.download_button(
            label="📄 TXT 다운로드",
            data=clean_result,
            file_name=f"{file_name}.txt",
            mime="text/plain",
            use_container_width=True
        )

    with col2:

        st.download_button(
            label="📑 PDF 다운로드",
            data=pdf_data,
            file_name=f"{file_name}.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.balloons()