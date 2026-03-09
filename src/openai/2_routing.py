from utils import llm_call

def run_router_workflow(user_prompt : str):
    router_prompt = f"""
    사용자의 프롬프트/질문: {user_prompt}

    각 모델은 서로 다른 기능을 가지고 있습니다. 사용자의 질문에 가장 적합한 모델을 선택하세요:
    - gpt-5-nano: 일반적인 작업에 가장 적합한 모델 (기본값)
    - o4-mini: 코딩 및 복잡한 문제 해결에 적합한 모델
    - gpt-5-mini: 간단한 사칙연산 등의 작업에 적합한 모델
    
    모델명만 단답형으로 응답하세요
    """
    print(router_prompt)
    selected_model = llm_call(router_prompt)
    print("선택한 모델", selected_model)
    response = llm_call(user_prompt, model = selected_model)
    print(response)
    return response

query1 = "1더하기 2는 뭐지?"
print(query1)
response = run_router_workflow(query1)
print()


query2 = "리스본 여행일정을 짜줘"
print(query2)
response = run_router_workflow(query2)
print()


query3 = "파이썬으로 API 웹서버를 만들어줘"
print(query3)
response = run_router_workflow(query3)