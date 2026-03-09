import json
from utils import llm_call

"""
    [LangGraph 예제] https://github.com/kdk1026/langgraph_study_02/blob/main/src/study_04.py
"""

# 1. 초기 상태 설정
state = {
    "product_name": "자율주행 자동차",
    "ad_copy": "",
    "feedback": "",
    "status": "fail",
    "iteration_count": 0
}

# 2. 노드 함수 정의 (순수 파이썬 함수)

def copywriter_logic(state):
    product = state["product_name"]
    feedback = state["feedback"]
    count = state["iteration_count"]

    print(f"\n--- [Copywriter] 광고 문구 작성 중 (시도: {count + 1}) ---")

    if not feedback:
        # 첫 시도: 건조하게 작성 유도
        prompt = f"'{product}'의 기능 위주로 인스타그램 홍보 문구를 건조하게 작성해줘. 홍보 문구만 답변하고 반드시 20자 이하로 작성하시오."
    else:
        # 피드백 반영 시도
        prompt = f"""
        '{product}' 인스타그램 홍보 문구를 다시 작성해.
        <피드백 반영>: {feedback}
        <제약사항>: 홍보 문구만 답변하고 50자 이하로 작성할 것.
        """

    response = llm_call(prompt)
    
    # 상태 업데이트
    state["ad_copy"] = response.strip()
    state["iteration_count"] += 1
    return state

def manager_logic(state):
    ad_copy = state["ad_copy"]
    print("\n--- [Manager] 문구 검수 중 ---")
    print(f"   ㄴ 신입의 결과물: {ad_copy}")

    # JSON 출력을 유도하는 프롬프트 (structured_output 대신 사용)
    prompt = f"""
    당신은 마케팅 팀장입니다. 다음 문구를 평가하여 JSON 형식으로만 응답하세요.
    문구: "{ad_copy}"

    <평가 기준>
    1. 해시태그(#) 3개 이상
    2. '할인' 또는 '특가' 포함
    3. 감성적이고 활기찬 톤

    응답 형식:
    {{"status": "pass" 또는 "fail", "feedback": "탈락 시 조언"}}
    """

    response = llm_call(prompt)
    
    try:
        # JSON 문자열만 추출하여 파싱 (llm_call의 결과가 마크다운 형식을 포함할 수 있음)
        result = json.loads(response.replace("```json", "").replace("```", "").strip())
        state["status"] = result.get("status", "fail")
        state["feedback"] = result.get("feedback", "")
    except:
        # 파싱 실패 시 기본값 처리
        state["status"] = "fail"
        state["feedback"] = "형식 오류로 인한 재작성 요청"
        raise
        
    return state

# 3. 메인 실행 루프
def main(state):
    print("--- 광고 카피 제작 프로세스 시작 ---")

    while state["iteration_count"] < 3:
        # 1. 카피 작성
        state = copywriter_logic(state)
        
        # 2. 검수
        state = manager_logic(state)
        
        # 3. 조건부 라우팅 (Pass 여부 확인)
        if state["status"] == "pass":
            print(f"\n✅ 최종 승인됨! (시도 횟수: {state['iteration_count']})")
            break
        else:
            print(f"❌ 불합격: {state['feedback']}")

    if state["status"] != "pass":
        print("\n⚠️ 최대 수정 횟수(3회)를 초과하여 프로세스를 종료합니다.")

    print("\n--- 최종 결과 ---")
    print(f"문구: {state['ad_copy']}")

if __name__ == "__main__":
    main(state)