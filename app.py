import streamlit as st
import json
import streamlit.components.v1 as components

st.set_page_config(page_title="텍스트 매핑 웹앱", layout="wide")

st.title("품평회 내용 정리")

if "files" not in st.session_state:
    st.session_state.files = {
        "원문데이터": {},
        "ixi-Gen": {},
        "ixi-BART": {},
        "Gemini-1.5Flash": {},
        "Gemini-2.0Flash-lite": {},
        "Gemini-2.0Flash": {}
    }

st.sidebar.header("파일 업로드")
categories = ["원문데이터", "ixi-Gen", "ixi-BART", "Gemini-1.5Flash", "Gemini-2.0Flash-lite", "Gemini-2.0Flash"]

for category in categories:
    uploaded = st.sidebar.file_uploader(f"{category} 업로드", type="txt", accept_multiple_files=True, key=category)
    if uploaded:
        for file in uploaded:
            content = file.read().decode("utf-8")
            st.session_state.files[category][file.name] = content
    st.sidebar.write(f"업로드된 파일 수: {len(st.session_state.files[category])}")

def copy_button(label, text, key, height=100):
    st.text_area(label, text, height=height, key=key)
    components.html(f"""
    <div style='margin-top:-10px;'>
        <textarea id="{key}" style="position: absolute; left: -9999px;">{text.replace('"', '&quot;')}</textarea>
        <button onclick="
            var copyText = document.getElementById('{key}');
            copyText.select();
            document.execCommand('copy');
            var notice = document.getElementById('{key}_notice');
            notice.style.display = 'inline';
            setTimeout(function() {{ notice.style.display = 'none'; }}, 1500);
        " style="margin-top:2px; padding:2px 6px; font-size:10px; cursor:pointer;">📎 복사</button>
        <span id="{key}_notice" style="display:none; color:green; font-size:10px;">✔ 복사됨!</span>
    </div>
    """, height=35)

def parse_and_display(category, content, unique_prefix):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        st.warning(f"{category}의 데이터가 유효한 JSON 형식이 아닙니다.")
        copy_button(f"{category} 원본 내용", content, f"{unique_prefix}_raw", height=200)
        return

    if not isinstance(data, dict):
        st.warning(f"{category}의 데이터가 JSON이지만 dict 형식이 아닙니다 (type: {type(data).__name__}).")
        copy_button(f"{category} 원본 내용", json.dumps(data, ensure_ascii=False, indent=2), f"{unique_prefix}_raw", height=200)
        return

    with st.container():
        st.markdown(f"<h5 style='font-size:14px;'>{category}</h5>", unsafe_allow_html=True)

        summary_1line_raw = data.get("summary_1line", "한줄 요약 없음")
        if isinstance(summary_1line_raw, list):
            summary_1line = "\n".join(summary_1line_raw)
        else:
            summary_1line = str(summary_1line_raw)
        copy_button("한줄 요약", summary_1line, f"{unique_prefix}_summary", height=100)

        summary_detail_raw = data.get("summary_detail", [])
        if isinstance(summary_detail_raw, list):
            detail_text = "\n".join(f"- {item}" for item in summary_detail_raw) if summary_detail_raw else "상세 내용 없음"
        else:
            detail_text = str(summary_detail_raw) or "상세 내용 없음"
        copy_button("상세요약", detail_text, f"{unique_prefix}_detail", height=300)

        keywords_raw = data.get("keywords", [])
        if isinstance(keywords_raw, list):
            keyword_text = ", ".join(keywords_raw) if keywords_raw else "키워드 없음"
        else:
            keyword_text = str(keywords_raw) or "키워드 없음"
        copy_button("키워드", keyword_text, f"{unique_prefix}_keywords", height=100)

        if category != "ixi-BART":
            task_recommend = data.get("task_recommend", [])
            if task_recommend:
                st.markdown("**태스크 추천**")
                simple_tasks = ["schedule", "map", "phone_call"]
                other_tasks = []

                for idx, task in enumerate(task_recommend, 1):
                    if not isinstance(task, dict):
                        continue
                    task_type = task.get("task", "")
                    task_info = "\n".join([f"{k}: {v}" for k, v in task.items() if v])
                    if task_type in simple_tasks:
                        copy_button(f"태스크 {idx} ({task_type})", task_info, f"{unique_prefix}_task_{idx}", height=150)
                    else:
                        other_tasks.append((idx, task_type, task_info))

                if other_tasks:
                    with st.expander("기타 태스크들", expanded=False):
                        for idx, task_type, task_info in other_tasks:
                            copy_button(f"태스크 {idx} ({task_type})", task_info, f"{unique_prefix}_other_task_{idx}", height=150)
            else:
                st.info("태스크 추천 없음")

st.subheader("원문데이터 내용 보기")
original_files = list(st.session_state.files["원문데이터"].keys())

if original_files:
    selected_file = st.selectbox("원문데이터 파일 선택", original_files)
    copy_button("원문 내용", st.session_state.files["원문데이터"][selected_file], "original_content", height=300)

    if selected_file.endswith("_scripts_t.txt"):
        model_file_key = selected_file.replace("_scripts_t.txt", "_output.txt")
    else:
        model_file_key = selected_file.replace(".txt", "_output.txt")

    st.markdown("---")
    st.subheader("매핑된 결과 보기")

    cols = st.columns(len(categories[1:]))
    for i, category in enumerate(categories[1:]):
        with cols[i]:
            mapped_text = st.session_state.files[category].get(model_file_key, None)
            if mapped_text:
                unique_prefix = f"{category}_{selected_file}"
                parse_and_display(category, mapped_text, unique_prefix)
            else:
                st.info(f"{model_file_key} (해당 파일 없음)")
else:
    st.info("왼쪽 사이드바에서 원문데이터를 먼저 업로드해 주세요.")
