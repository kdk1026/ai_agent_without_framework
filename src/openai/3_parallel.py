import asyncio

from .utils import llm_call_async


async def run_llm_parallel(prompt_details):
    tasks = [llm_call_async(prompt['user_prompt'], prompt['model']) for prompt in prompt_details]
    responses = []
    
    for task in asyncio.as_completed(tasks):
        result = await task
        print("LLM 응답 완료:", result)
        responses.append(result)
    
    return responses

async def main():
    question = ("아래 문장을 자연스러운 한국어로 번역해줘:\n"
                "\"Do what you can, with what you have, where you are.\" — Theodore Roosevelt")
    
    parallel_prompt_details = [
        {"user_prompt": question, "model": "gpt-5-nano"},
        {"user_prompt": question, "model": "gpt-5-mini"},
        {"user_prompt": question, "model": "o4-mini"},
    ]
    
    responses = await run_llm_parallel(parallel_prompt_details)
    
    aggregator_prompt = ("다음은 여러 개의 AI 모델이 사용자 질문에 대해 생성한 응답입니다.\n"
                         "당신의 역할은 이 응답들을 모두 종합하여 최종 답변을 제공하는 것입니다.\n"
                         "일부 응답이 부정확하거나 편향될 수 있으므로, 신뢰성과 정확성을 갖춘 응답을 생성하는 것이 중요합니다.\n\n"
                         "사용자 질문:\n"
                         f"{question}\n\n"
                         "모델 응답들:")
    
    for i in range(len(parallel_prompt_details)):
        aggregator_prompt += f"\n{i+1}. 모델 응답: {responses[i]}\n"
    
    print("---------------------------종합 프롬프트:-----------------------\n", aggregator_prompt)
    final_response = await llm_call_async(aggregator_prompt, model="gpt-4o")
    print("---------------------------최종 종합 응답:-----------------------\n", final_response)

# 비동기 main 함수 실행
asyncio.run(main())