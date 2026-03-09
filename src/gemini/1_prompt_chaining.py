from utils import llm_call

"""
    [LangGraph 예제] https://github.com/kdk1026/langgraph_study_02/blob/main/src/study_01.py
"""

# 1. State 정의 (순수 파이썬에서는 딕셔너리로 관리)
# 별도의 TypedDict 없이도 동작하지만, 구조 파악을 위해 주석으로 남깁니다.
# state = {"topic": "", "draft_joke": "", "improved_joke": "", "final_joke": ""}

"""
    2. 단계별 함수(Node 역할) 정의
"""

# [Step 1] 초안 생성
def generate_joke(topic: str) -> str:
    print(f"\n--- [1단계] '{topic}' 주제로 농담 초안 생성 중 ---")
    prompt = f"'{topic}'에 대한 짧고 재미있는 농담을 하나 만들어줘. 다른 말은 하지 말고 농담 하나만 해"
    return llm_call(prompt)

# [Step 2] 윤색/수정
def critique_and_improve(original_joke: str) -> str:
    print("\n--- [2단계] 더 웃기게 수정 중 (아재개그 스타일) ---")
    prompt = f"""
    다음 농담을 보고, 더 썰렁하고 재미있는 '아재개그' 스타일로 개선해줘. 다른 말은 하지 말고 하나만 답변해.
    원문: {original_joke}
    """
    return llm_call(prompt)

# [Step 3] 최종 포장
def polish_joke(improved_joke: str) -> str:
    print("\n--- [3단계] 이모지 추가 및 마무리 ---")
    prompt = f"""
    다음 농담에 적절한 이모지를 듬뿍 넣어서 SNS에 올리기 좋게 꾸며줘.
    농담: {improved_joke}
    """
    return llm_call(prompt)

"""
    3. 실행 흐름 제어 (Graph/Chain 역할)
"""
def run_joke_pipeline(topic: str):
    # 결과를 담을 딕셔너리 (LangGraph의 State와 동일한 역할)
    state = {"topic": topic}

    # Step 1 실행
    state["draft_joke"] = generate_joke(state["topic"])

    # Step 2 실행
    state["improved_joke"] = critique_and_improve(state["draft_joke"])

    # Step 3 실행
    state["final_joke"] = polish_joke(state["improved_joke"])

    return state

# --- 메인 실행부 ---
if __name__ == "__main__":
    initial_topic = "고양이"
    result = run_joke_pipeline(initial_topic)

    print("\n" + "="*50)
    print(f"주제: {result['topic']}")
    print(f"1차 초안: {result['draft_joke']}")
    print(f"2차 수정: {result['improved_joke']}")
    print("-" * 30)
    print(f"최종 완성:\n{result['final_joke']}")