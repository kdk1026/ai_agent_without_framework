import asyncio

# 1. 상태(State) 정의: 각 노드가 공유하고 업데이트할 데이터 구조
from typing import Optional, TypedDict

from gemini.utils import llm_call_async

"""
    [LangGraph 예제] https://github.com/kdk1026/langgraph_study_02/blob/main/src/study_02.py
"""

# 1. 상태(State) 정의: 각 작업의 결과물을 담을 그릇
class WriterState(TypedDict):
    topic: str
    poem: Optional[str]
    story: Optional[str]
    joke: Optional[str]
    final_report: Optional[str]

# --- [Worker Nodes] ---

async def write_poem(state: WriterState):
    topic = state["topic"]
    print(f"   [Worker A] '{topic}' 주제로 시(Poem) 작성 시작...")
    # Gemini 모델을 사용하여 비동기 호출
    response = await llm_call_async(f"'{topic}'에 대한 아름다운 시를 짧게 써줘.")
    return {"poem": response}

async def write_story(state: WriterState):
    topic = state["topic"]
    print(f"   [Worker B] '{topic}' 주제로 소설(Story) 작성 시작...")
    response = await llm_call_async(f"'{topic}'에 대한 감동적인 짧은 이야기를 써줘.")
    return {"story": response}

async def write_joke(state: WriterState):
    topic = state["topic"]
    print(f"   [Worker C] '{topic}' 주제로 농담(Joke) 작성 시작...")
    response = await llm_call_async(f"'{topic}'에 대한 재미있는 아재개그를 하나 해줘.")
    return {"joke": response}

# --- [Aggregator Node] ---

async def aggregator(state: WriterState):
    print("\n--- [Aggregator] 모든 원고 도착! 최종 편집 및 종합 요약 중 ---")
    
    # 각 워커의 결과물을 조합하여 최종 프롬프트 생성
    summary_prompt = (
        f"다음은 '{state['topic']}'을 주제로 작성된 세 가지 글입니다.\n"
        f"1. 시: {state['poem']}\n"
        f"2. 소설: {state['story']}\n"
        f"3. 농담: {state['joke']}\n\n"
        "이 내용들을 멋지게 편집하여 하나의 완성된 종합 선물세트 리포트로 만들어줘."
    )
    
    # 최종 편집장 역할도 LLM에게 맡길 수 있습니다.
    final_text = await llm_call_async(summary_prompt)
    return {"final_report": final_text}

async def main():
    # 초기 입력 상태
    state: WriterState = {
        "topic": "직장인의 월요일",
        "poem": None,
        "story": None,
        "joke": None,
        "final_report": None
    }

    print(f"====== 워크플로우 시작: 주제 - {state['topic']} ======")

    # 1. 병렬 실행 (Fan-out): 시인, 소설가, 개그맨이 동시에 일을 시작합니다.
    tasks = [
        write_poem(state),
        write_story(state),
        write_joke(state)
    ]
    
    # asyncio.gather를 통해 병렬 실행 후 결과를 리스트로 받음
    results = await asyncio.gather(*tasks)

    # 2. 상태 업데이트: 병렬 작업 결과를 state에 병합
    for result in results:
        state.update(result)

    # 3. 취합 실행 (Fan-in): 모든 결과가 모인 후 편집장이 마무리
    final_result = await aggregator(state)
    state.update(final_result)

    print("\n================ FINAL REPORT ================")
    print(state["final_report"])
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(main())