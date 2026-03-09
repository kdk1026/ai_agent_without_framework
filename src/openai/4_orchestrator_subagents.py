import asyncio
import json
from .utils import llm_call, llm_call_async

DEFAULT_MODEL = "gpt-5-nano"

# 병렬 처리를 위한 함수
# async def run_llm_parallel(prompt_list):
#     tasks = [llm_call_async(prompt) for prompt in prompt_list]
#     responses = []
    
#     for task in asyncio.as_completed(tasks):
#         result = await task
#         responses.append(result)
#     return responses

# 질문과 응답의 순서를 매칭시키기 위해서는 gather 이용이 필요함 ('25.07.23 업데이트)
async def run_llm_parallel(prompt_list):
    tasks = [llm_call_async(prompt) for prompt in prompt_list]
    responses = await asyncio.gather(*tasks)
    return responses

# 파이썬 f string에서는 {} 1개는 변수, JSON에서는 2개를 사용해야 함
def get_orchestrator_prompt(user_query):
    return f"""
다음 사용자 질문을 분석하고, 이를 3개의 관련된 하위 질문으로 분해하십시오:

다음 형식으로 응답을 제공하십시오:

{{
    "analysis": "사용자 질문에 대한 이해를 상세히 설명하고, 작성한 하위 질문들의 근거를 설명하십시오.",
    "subtasks": [
        {{
            "description": "이 하위 질문의 초점과 의도를 설명하십시오.",
            "sub_question": "질문 1"
        }},
        {{
            "description": "이 하위 질문의 초점과 의도를 설명하십시오.",
            "sub_question": "질문 2"
        }}
        // 필요에 따라 추가 하위 질문 포함
    ]
}}
최대 3개의 하위 질문을 생성하세요

사용자 질문: {user_query}
"""

def get_worker_prompt(user_query, sub_question, description):
    return f"""
    다음 사용자 질문에서 파생된 하위 질문을 다루는 작업을 맡았습니다:
    원래 질문:  {user_query}
    하위 질문: {sub_question}

    지침: {description}

    하위 질문을 철저히 다루는 포괄적이고 상세한 응답을 해주세요
    """

async def orchestrate_task(user_query):
    """
    오케스트레이터를 실행하여 원래 질문을 하위 질문으로 분해하고,
    각각의 하위 질문을 병렬적으로 실행하여 종합적인 응답을 생성합니다.
    """

    # 1단계 : 사용자 질문 기반으로 여러 질문 도출
    orchestrator_prompt = get_orchestrator_prompt(user_query)
    print("\n============================orchestrator prompt============================\n")
    print(orchestrator_prompt)
    orchestrator_response = llm_call(orchestrator_prompt, model=DEFAULT_MODEL)
 
    # 응답 결과 (1단계) 출력
    print("\n============================orchestrator response==========================\n")
    print(orchestrator_response)
 
    response_json = json.loads(orchestrator_response.replace('```json', '').replace('```', ''))
    
    analysis = response_json.get("analysis", "")
    sub_tasks = response_json.get("subtasks", [])

    # 2단계 : 각 하위질문에 대한 LLM 호출
    worker_prompts = [get_worker_prompt(user_query, task["sub_question"], task["description"]) for task in sub_tasks]
    print("\n============================worker prompts==========================\n")
    for prompt in worker_prompts:
        print(prompt)

    worker_responses = await run_llm_parallel(worker_prompts)
    
    # 응답결과(2단계) 출력
    print("\n============================worker responses==========================\n")
    for response in worker_responses:
        print(response) 
    
    # 3단계 : 하위질문 응답 종합 및 LLM 호출
    aggregator_prompt = f"""아래는 사용자의 원래 질문에 대해서 하위 질문을 나누고 응답한 결과입니다.
    아래 질문 및 응답내용을 포함한 최종 응답을 제공해주세요.
    ## 요청사항
    - 하위질문 응답내용이 최대한 포괄적이고 상세하게 포함되어야 합니다
    사용자의 원래 질문:
    {user_query}

    하위 질문 및 응답:
    """
    
    for i in range(len(sub_tasks)):
        aggregator_prompt += f"\n{i+1}. 하위 질문: {sub_tasks[i]['sub_question']}\n"
        aggregator_prompt += f"\n   응답: {worker_responses[i]}\n"
    
    print("\n============================aggregator prompt==========================\n")
    print(aggregator_prompt)
    
    final_response = llm_call(aggregator_prompt, model=DEFAULT_MODEL)
    
    return final_response


async def main():
    user_query = "AI는 미래 일자리에 어떤 영향을 미칠까?"
    
    # CASE 1 : 그냥 질문했을 때   
    print("\n============================CASE 1==========================\n")
    print(llm_call(user_query, model=DEFAULT_MODEL))
    
    # CASE 2 : 오케스트레이터 패턴으로 질문했을 때
    print("\n============================CASE 2==========================\n")
    final_output = await orchestrate_task(user_query)
    # 최종 응답 생성
    print("\n============================최종응답==========================\n")
    print(final_output)   
asyncio.run(main())