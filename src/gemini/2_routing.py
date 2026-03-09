from utils import llm_call

# 전문가 함수들 (Expert Functions)
def billing_expert(user_prompt):
    print("--- [Billing Expert] 결제 전문가가 답변 작성 중 ---")
    prompt = f"당신은 결제 및 환불 전문가입니다. 다음 문의에 대해 정중하게 답변하세요: {user_prompt}"
    return llm_call(prompt)

def technical_expert(user_prompt):
    print("--- [Tech Expert] 기술 지원 엔지니어가 분석 중 ---")
    prompt = f"당신은 IT 엔지니어입니다. 다음 기술 문제에 대해 해결책을 제시하세요: {user_prompt}"
    return llm_call(prompt)

def shipping_expert(user_prompt):
    print("--- [Shipping Expert] 물류 담당자가 배송 조회 중 ---")
    prompt = f"당신은 배송 관리자입니다. 다음 배송 문의에 대해 답변하세요: {user_prompt}"
    return llm_call(prompt)

def general_expert(user_prompt):
    print("--- [General] 일반 상담원이 답변 중 ---")
    prompt = f"다음 문의에 친절하게 답변하세요: {user_prompt}"
    return llm_call(prompt)

# 라우터 메인 로직
def run_router_workflow(user_prompt : str):
    # 1. 의도 파악을 위한 라우팅 프롬프트
    router_prompt = f"""
    사용자의 질문을 분석하여 가장 적합한 담당자를 선택하세요.
    - BILLING: 결제, 환불, 가격, 구독 관련
    - TECH: 기술적 오류, 설치, API, 버그 관련
    - SHIPPING: 배송 상태, 위치, 배송지 변경 관련
    - GENERAL: 그 외 일반적인 인사, 서비스 안내 등

    사용자 질문: {user_prompt}
    
    카테고리 이름(BILLING, TECH, SHIPPING, GENERAL)만 정확히 응답하세요.
    """
    
    # 2. 라우터 호출 (기본 모델 사용)
    selected_category = llm_call(router_prompt).strip().upper()
    print(f"[Router] 선택된 담당자: {selected_category}")

    # 3. 카테고리에 따른 함수 매핑
    expert_map = {
        "BILLING": billing_expert,
        "TECH": technical_expert,
        "SHIPPING": shipping_expert,
        "GENERAL": general_expert
    }

    # 4. 적절한 함수 실행 (없을 경우 일반 상담으로 유도)
    expert_func = expert_map.get(selected_category, general_expert)
    response = expert_func(user_prompt)
    
    return response

query1 = "어제 결제했는데 환불하고 싶어"
print(query1)
response = run_router_workflow(query1)
print()


query2 = "로그인이 계속 실패하는데 서버 문제인가?"
print(query2)
response = run_router_workflow(query2)
print()


query3 = "내 택배가 지금 어디쯤 오고 있나?"
print(query3)
response = run_router_workflow(query3)
print()


query4 = "안녕, 좋은 아침이야"
print(query4)
response = run_router_workflow(query4)