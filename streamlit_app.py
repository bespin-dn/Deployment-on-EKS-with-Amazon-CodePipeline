import streamlit as st 
import requests

# FastAPI 서버 주소
FASTAPI_URL = "http://127.0.0.1:8000"  # FastAPI가 실행 중인 URL


# KMS 키 목록 가져오기 함수
def fetch_kms_keys():
    try:
        response = requests.get(f"{FASTAPI_URL}/kms/keys")
        if response.status_code == 200:
            return response.json().get("keys", [])  # 키 리스트 반환
        else:
            return ["Error fetching keys"]  # 오류 발생 시 기본값 반환
    except requests.exceptions.RequestException:
        return ["Connection error"]  # FastAPI 연결 오류 처리
# KMS 키 목록 동적 설정
KMS_KEYS = fetch_kms_keys()
KMS_KEYS = [f"{key['Alias'].replace('alias/','')} ({key['KeyId']})" for key in KMS_KEYS]  # 출력 형식 변경



st.set_page_config(page_title="Bespinglobal", layout="wide")

# 탭 생성
tab1, tab2 = st.tabs(["🤖 GenAI", "🔐 KMS"])


with tab1:
    # st.header("Amazon Bedrock 모델 호출")
    
    # 프롬프트 입력
    query = st.text_area("🔤 Enter Prompt", height=100)
    
    # 요청 실행 버튼
    if st.button("실행"):
        if not query:
            st.error("프롬프트를 입력해주세요.")
        else:
            # 로딩 표시
            with st.spinner("모델 응답을 기다리는 중..."):
                try:
                    # FastAPI 서버로 요청 전송
                    response = requests.post(f"{FASTAPI_URL}/genai/invoke", params={"query": query})
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # 결과 표시 영역
                        st.subheader("모델 응답")
                        st.markdown(result.get("body", "응답이 없습니다."))
                        
                        # 상태 코드 표시
                        st.text(f"상태 코드: {result.get('statusCode', '없음')}")
                    else:
                        st.error(f"오류 발생: {response.status_code} - {response.text}")
                
                except requests.exceptions.RequestException as e:
                    st.error(f"서버 연결 오류: {e}")
with tab2:
    # **최상단에 KMS Key 선택 Selectbox 추가**n
    selected_key = st.selectbox("🔑 Select KMS Key", KMS_KEYS)

    # 중앙 입력 박스
    plaintext = st.text_area("🔤 Enter text", height=100)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔒 Encrypt"):
            if plaintext:
                print(selected_key)
                response = requests.post(f"{FASTAPI_URL}/kms/encrypt", json={"key": selected_key, "text": plaintext})
                if response.status_code == 200:
                    encrypted_text = response.json().get("ciphertext", "")
                    st.success("✅ Encryption Successful!")
                    st.code(encrypted_text, language="plaintext")
                else:
                    st.error("❌ Encryption failed.")
            else:
                st.warning("⚠️ Please enter text to encrypt.")

    with col2:
        if st.button("🔓 Decrypt"):
            if plaintext:
                response = requests.post(f"{FASTAPI_URL}/kms/decrypt", json={"key": selected_key, "text": plaintext})
                if response.status_code == 200:
                    decrypted_text = response.json().get("decrypted_text", "")
                    st.success("✅ Decryption Successful!")
                    st.code(decrypted_text, language="plaintext")
                else:
                    st.error("❌ Decryption failed.")
            else:
                st.warning("⚠️ Please enter encrypted text to decrypt.")
