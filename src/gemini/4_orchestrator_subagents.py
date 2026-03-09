import asyncio
import json
from typing import List
from pydantic import BaseModel

from utils import llm_call, llm_call_async


## 1. 데이터 모델 정의
class Section(BaseModel):
    name: str
    description: str

## 2. 노드 역할 함수 정의

# [Orchestrator] 계획 수립
async def orchestrator_step(topic: str) -> List[Section]:
    print(f"\n--- [Orchestrator] '{topic}' 보고서 계획 수립 중 ---")
    
    prompt = f"""
    '{topic}'에 대한 보고서 목차를 짜줘. 3개 섹션 이내로 구성해.
    응답은 반드시 아래와 같은 JSON 형식으로만 해줘. 다른 설명은 생략해.
    {{
        "sections": [
            {{"name": "섹션제목", "description": "내용 가이드"}},
            ...
        ]
    }}
    """
    
    # LLM 호출
    response_text = await llm_call_async(prompt)
    
    # JSON 파싱 (순수 파이썬에서는 직접 처리가 필요)
    try:
        # 마크다운 제거나 공백 제거 후 파싱
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        sections = [Section(**s) for s in data["sections"]]
        print(f"생성된 계획: {[s.name for s in sections]}")
        return sections
    except Exception as e:
        print(f"JSON 파싱 에러: {e}")
        return []

# [Worker] 개별 섹션 작성 (병렬 실행될 함수)
async def worker_step(section: Section) -> str:
    print(f"   --- [Worker] 집필 중: {section.name} ---")
    
    prompt = f"""
    다음 섹션에 대한 내용을 짧게 작성해줘.
    제목: {section.name}
    내용 가이드: {section.description}
    """
    
    content = await llm_call_async(prompt)
    return f"## {section.name}\n{content}\n"

# [Synthesizer] 결과 취합
def synthesizer_step(contents: List[str]) -> str:
    print("\n--- [Synthesizer] 모든 원고 취합 및 최종 편집 ---")
    return "\n".join(contents)

## 3. 메인 실행 흐름 (Main Workflow)
async def run_report_pipeline(topic: str):
    # Step 1: 계획 수립 (Sequential)
    sections = await orchestrator_step(topic)
    
    if not sections:
        print("계획 수립에 실패했습니다.")
        return

    # Step 2: 섹션별 병렬 집필 (Parallel / Map)
    # asyncio.gather를 사용하여 모든 worker를 동시에 실행합니다.
    print(f"\n--- [Parallel Processing] {len(sections)}개의 섹션 동시 작성 시작 ---")
    tasks = [worker_step(section) for section in sections]
    completed_sections = await asyncio.gather(*tasks)

    # Step 3: 취합 (Reduce)
    final_report = synthesizer_step(completed_sections)
    
    print("\n================ 최종 보고서 ================")
    print(final_report)
    return final_report

# 실행
async def main():
    user_query = "생성형 AI의 미래"
    
    # CASE 1 : 그냥 질문했을 때   
    print("\n============================CASE 1==========================\n")
    print(llm_call(user_query))
    
    # CASE 2 : 오케스트레이터 패턴으로 질문했을 때
    print("\n============================CASE 2==========================\n")
    final_output = await run_report_pipeline(user_query)
    # 최종 응답 생성
    print("\n============================최종응답==========================\n")
    print(final_output)   

if __name__ == "__main__":
    asyncio.run(main())