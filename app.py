import streamlit as st
import json

# Streamlit 설정
st.set_page_config(page_title="텍스트 매핑 웹앱", layout="wide")

# 앱 제목
st.title("품평회 내용 정리")

# 파일 저장을 위한 세션 상태 초기화
if "files" not in st.session_state:
    st.session_state.files = {
        "원문데이터": {},
        "ixi-Gen": {},
        "ixi-BART": {},
        "Gemini-1.5Flash": {}
    }

# 사이드바
st.sidebar.header("파일 업로드")
categories = ["원문데이터", "ixi-Gen", "ixi-BART", "Gemini-1.5Flash"]

for category in categories:
    uploaded = st.sidebar.file_uploader(
        f"{category} 업로드", type="txt", accept_multiple_files=True, key=category
    )
    if uploaded:
        for file in uploaded:
            content = file.read().decode("utf-8")
            st.session_state.files[category][file.name] = content
    st.sidebar.write(f"업로드된 파일 수: {len(st.session_state.files[category])}")

def parse_and_display(category, content):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        st.warning(f"{category}의 데이터가 유효한 JSON 형식이 아닙니다.")
        st.text_area(f"{category} 원본 내용", content, height=500)
        return

    st.markdown(f"### {category}")
    st.markdown("---")

    # 한줄 요약
    summary_1line = data.get("summary_1line", "한줄 요약 없음")
    st.text_area("한줄 요약", summary_1line)
    st.markdown("---")

    # 상세 요약 (고정 높이 박스)
    summary_detail = data.get("summary_detail", [])
    detail_text = "\n".join(f"- {item}" for item in summary_detail) if summary_detail else "상세 내용 없음"
    st.text_area("상세요약", detail_text, height=200)
    st.markdown("---")

    # 키워드 (고정 높이 박스)
    keywords = data.get("keywords", [])
    keyword_text = " ".join(keywords) if keywords else "키워드 없음"
    st.text_area("키워드", keyword_text, height=100)
    st.markdown("---")

    # 태스크 추천 (ixi-BART 제외, 구분하여 표시)
    if category != "ixi-BART":
        task_recommend = data.get("task_recommend", [])
        st.subheader("태스크 추천")
        if task_recommend:
            for idx, task in enumerate(task_recommend, 1):
                task_type = task.get("task", "")
                task_info = "\n".join([f"{k}: {v}" for k, v in task.items() if v])
                
                if task_type in ["schedule", "map", "phone_call"]:
                    st.text_area(f"태스크 {idx} ({task_type})", task_info, height=150)
                else:
                    with st.expander(f"태스크 {idx} ({task_type})", expanded=False):
                        st.text_area(f" ", task_info, height=150)
        else:
            st.info("태스크 추천 없음")

# 메인 컨텐츠
st.subheader("원문데이터 내용 보기")
original_files = list(st.session_state.files["원문데이터"].keys())

if original_files:
    selected_file = st.selectbox("원문데이터 파일 선택", original_files)
    st.text_area("원문 내용", st.session_state.files["원문데이터"][selected_file], height=500)

    # 모델 쪽에서 찾을 이름: 원본 이름에서 '.txt'를 '_output.txt'로 변환
    model_file_key = selected_file.replace(".txt", "_output.txt")

    st.markdown("---")
    st.subheader("매핑된 결과 보기")

    cols = st.columns(3)
    for i, category in enumerate(categories[1:]):
        with cols[i]:
            mapped_text = st.session_state.files[category].get(model_file_key, None)
            if mapped_text:
                parse_and_display(category, mapped_text)
            else:
                st.info(f"{model_file_key} (해당 파일 없음)")
else:
    st.info("왼쪽 사이드바에서 원문데이터를 먼저 업로드해 주세요.")
