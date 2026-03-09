from typing import List
from utils import llm_call

def prompt_chain_workflow(initial_input: str, prompt_chain: List[str]) -> List[str]:
    response_chain = []
    response = initial_input

    for i, prompt in enumerate(prompt_chain, 1):
        print(f"\n==== 단계 {i} ====\n")
        final_prompt = f"{prompt}\n사용자 입력:\n{response}"
        print(f"🔹 프롬프트:\n{final_prompt}\n")

        response = llm_call(final_prompt)
        response_chain.append(response)
        print(f"✅ 응답:\n{response}\n")

    return response_chain


## 처음 입력값을 계속 유지해야 하는 경우!
def prompt_chain_workflow_2(initial_input: str, prompt_chain: List[str]) -> List[str]:
    response_chain = []
    response = initial_input

    for i, prompt in enumerate(prompt_chain, 1):
        print(f"\n==== 단계 {i} ====\n")
        final_prompt = f"{prompt}\n\n🔹 문맥(Context):\n{response}\n🔹 사용자 입력: {initial_input}"
        print(f"🔹 프롬프트:\n{final_prompt}\n")

        response = llm_call(final_prompt)
        response_chain.append(response)
        print(f"✅ 응답:\n{response}\n")

    return response_chain


initial_input ="""
나는 여름 휴가를 계획 중이야. 따뜻한 날씨를 좋아하고, 자연 경관과 역사적인 장소를 둘러보는 걸 좋아해.
어떤 여행지가 나에게 적합할까?
"""

# 프롬프트 체인: LLM이 단계적으로 여행을 계획하도록 유도
prompt_chain = [
    ## 여행 후보지 3곳을 추천하고 그 이유를 설명
"""사용자의 여행 취향을 바탕으로 적합한 여행지 3곳을 추천하세요. 
- 먼저 사용자가 입력한 희망사항을 요약해줘
- 사용자가 입력한 희망사항을 반영해서 왜 적합한 여행지인지 설명해주세요
- 각 여행지의 기후, 주요 관광지, 활동 등을 설명하세요.
""",

    ## 여행지 1곳을 선택하고 활동 5가지 나열
"""다음 여행지 3곳 중 하나를 선택하세요. 선택한 여행지 알려주세요. 그리고 선택한 이유를 설명해주세요.
- 해당 여행지에서 즐길 수 있는 주요 활동 5가지를 나열하세요. 
- 활동은 자연 탐방, 역사 탐방, 음식 체험 등 다양한 범주에서 포함되도록 하세요.
""",

    ## 선택한 여행지에서 하루 일정 계획
"""사용자가 하루 동안 이 여행지에서 시간을 보낼 계획입니다. 
- 오전, 오후, 저녁으로 나누어 일정을 짜고, 각 시간대에 어떤 활동을 하면 좋을지 설명하세요.
""",
]

responses = prompt_chain_workflow_2(initial_input,prompt_chain)

final_answer = responses[-1]
print(final_answer)