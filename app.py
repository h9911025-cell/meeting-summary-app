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
# PDF 분석 보고서 생성 함수
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
# 매뉴얼 PDF 생성 함수
# =========================

def create_manual_pdf():
    buffer = BytesIO()
    try:
        pdfmetrics.registerFont(TTFont("Malgun", "malgun.ttf"))
        font_name = "Malgun"
    except:
        font_name = "Helvetica"

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    styles["Title"].fontName = font_name
    styles["Heading2"].fontName = font_name
    styles["BodyText"].fontName = font_name
    styles["BodyText"].leading = 16

    story = []

    # 제목
    story.append(Paragraph("<b>AI 회의록 요약 시스템 사용자 매뉴얼</b>", styles["Title"]))
    story.append(Spacer(1, 15))
    story.append(Paragraph(f"작성일: {datetime.now().strftime('%Y-%m-%d')} | 시스템 버전: v1.0", styles["BodyText"]))
    story.append(Spacer(1, 25))

    # 섹션 1
    story.append(Paragraph("<b>1. 시스템 개요</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("본 시스템은 인공지능(AI)을 활용하여 복잡하고 긴 회의록 내용을 단 몇 초 만에 핵심 위주로 요약 및 분석해 주는 업무 효율화 플랫폼입니다. 보안성이 뛰어난 다크 모드 인터페이스와 유연한 파일 연동 기능을 제공합니다.", styles["BodyText"]))
    story.append(Spacer(1, 18))

    # 섹션 2
    story.append(Paragraph("<b>2. 주요 기능 및 조작 방법</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("• <b>회의록 파일 업로드</b>: 메인 화면 좌측의 업로드 영역에 텍스트 파일(.txt)을 드래그 앤 드롭하면 내용이 자동으로 입력창에 매핑됩니다.", styles["BodyText"]))
    story.append(Paragraph("• <b>직접 텍스트 입력</b>: 파일이 없더라도 편집창에 직접 회의 내용을 타이핑하거나 복사하여 붙여넣을 수 있습니다.", styles["BodyText"]))
    story.append(Paragraph("• <b>AI 분석 실행</b>: 우측의 'AI 분석 시작' 버튼을 누르면 실시간 프로그래스 바와 함께 핵심 요약, 결정 사항, 액션 아이템, 리스크 분석, 상사 보고 브리핑 등 5대 영역으로 정밀 분석이 수행됩니다.", styles["BodyText"]))
    story.append(Paragraph("• <b>분석 히스토리 관리</b>: 좌측 사이드바를 통해 과거에 분석했던 기록이 시간별로 저장되며, 검색창을 통해 이전 회의록을 쉽게 찾아 다시 불러올 수 있습니다.", styles["BodyText"]))
    story.append(Spacer(1, 18))

    # 섹션 3 (업무 꿀팁)
    story.append(Paragraph("<b>3. [필독] 실무 활용 및 1초 복사 꿀팁</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("최신 웹 브라우저의 강력한 클립보드 보안 규제 및 격리 환경(iframe)으로 인해, 일반적인 마우스 클릭형 자동 복사 버튼은 작동이 차단되거나 레이아웃을 무너뜨릴 수 있습니다. 따라서 아래의 <b>가장 확실하고 빠른 대안</b>을 권장합니다.", styles["BodyText"]))
    story.append(Paragraph("<b>방법 ① [강력 추천]:</b> 하단의 <b>'TXT 다운로드'</b> 버튼을 클릭하여 파일로 저장합니다. 파일을 열어 전체 선택(Ctrl+A) 후 복사(Ctrl+C)하면 메일이나 사내 메신저(슬랙, 카카오톡, 잔디 등)에 <b>줄바꿈과 서식이 100% 완벽하게 보존된 상태</b>로 바로 전달할 수 있습니다.", styles["BodyText"]))
    story.append(Paragraph("<b>방법 ②:</b> 웹 화면에 출력된 '분석 결과' 본문 영역을 마우스로 드래그하거나 트리플 클릭(세 번 연속 클릭)하여 직접 복사합니다.", styles["BodyText"]))
    story.append(Spacer(1, 18))

    # 섹션 4
    story.append(Paragraph("<b>4. 문제 해결 (FAQ)</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("• <b>텍스트 파일 업로드 시 글자가 깨지는 경우</b>: 메모장 등에서 파일 저장 시 인코딩 형식이 'UTF-8'로 되어 있는지 확인해 주세요.", styles["BodyText"]))
    story.append(Paragraph("• <b>분석 결과가 나오지 않거나 오류가 뜨는 경우</b>: 입력 내용이 너무 비어있지 않은지 확인하고, 사내 방화벽이나 네트워크 연결 상태를 점검 후 '입력 초기화'를 누르고 다시 실행해 주세요.", styles["BodyText"]))

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
   파일 업로더 디자인
========================= */

[data-testid="stFileUploader"] {
    background: rgba(15, 23, 42, 0.45) !important;
    backdrop-filter: blur(8px);
    border: 1px dashed rgba(148, 163, 184, 0.25) !important;
    border-radius: 20px !important;
    padding: 10px !important;
    margin-bottom: 15px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: rgba(96, 165, 250, 0.7) !important;
    background: rgba(15, 23, 42, 0.65) !important;
    box-shadow: 0 0 15px rgba(96, 165, 250, 0.15) !important;
}

[data-testid="stFileUploader"] section {
    padding: 15px !important;
}

[data-testid="stFileUploader"] group {
    color: #cbd5e1 !important;
}

[data-testid="stFileUploader"] svg {
    fill: #60a5fa !important;
}

[data-testid="stFileUploaderDropzone"] div div {
    color: #94a3b8 !important;
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

/* 사이가이드 내부 */

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

    uploaded_file = st.file_uploader(
        "회의록 파일 업로드 (.txt)",
        type=["txt"],
        disabled=st.session_state.processing,
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        try:
            stringio = BytesIO(uploaded_file.getvalue())
            file_text = stringio.read().decode("utf-8")
            st.session_state["meeting_input"] = file_text
        except Exception as file_err:
            st.error(f"파일을 읽는 중 오류가 발생했습니다: {file_err}")

    meeting_text = st.text_area(
        "입력",
        height=380,
        label_visibility="collapsed",
        placeholder="회의 내용을 입력하거나 위에 파일을 업로드하세요...",
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

    # [위치 조정 완료] 이제 분석 전에도 언제든지 매뉴얼을 다운로드할 수 있도록 우측 가이드 컴포넌트 하단에 상시 배치
    manual_pdf_data = create_manual_pdf()
    st.write("")
    st.download_button(
        label="📘 시스템 사용자 매뉴얼 다운로드 (PDF)",
        data=manual_pdf_data,
        file_name="AI_회의록_요약시스템_사용자매뉴얼.pdf",
        mime="application/pdf",
        use_container_width=True
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

            result_content = result_content.replace("```markdown", "").replace("```", "")

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

    clean_result = st.session_state.result.replace("```markdown", "").replace("```", "")

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