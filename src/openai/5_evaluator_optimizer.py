from utils import llm_call

def loop_workflow(user_query, evaluator_prompt, max_retries=5) -> str:
    """평가자가 생성된 요약을 통과할 때까지 최대 max_retries번 반복."""

    retries = 0
    while retries < max_retries:
        print(f"\n========== 📝 요약 프롬프트 (시도 {retries + 1}/{max_retries}) ==========\n")
        print(user_query)
        
        summary = llm_call(user_query, model="gpt-5-mini")
        print(f"\n========== 📝 요약 결과 (시도 {retries + 1}/{max_retries}) ==========\n")
        print(summary)
        
        final_evaluator_prompt = evaluator_prompt + summary
        evaluation_result = llm_call(final_evaluator_prompt, model="gpt-5-nano").strip()

        print(f"\n========== 🔍 평가 프롬프트 (시도 {retries + 1}/{max_retries}) ==========\n")
        print(final_evaluator_prompt)

        print(f"\n========== 🔍 평가 결과 (시도 {retries + 1}/{max_retries}) ==========\n")
        print(evaluation_result)

        if "평가결과 = PASS" in evaluation_result:
            print("\n✅ 통과! 최종 요약이 승인되었습니다.\n")
            return summary
        
        retries += 1
        print(f"\n🔄 재시도 필요... ({retries}/{max_retries})\n")

        # If max retries reached, return last attempt
        if retries >= max_retries:
            print("❌ 최대 재시도 횟수 도달. 마지막 요약을 반환합니다.")
            return summary  # Returning the last attempted summary, even if it's not perfect.

        # Updating the user_query for the next attempt with full history
        user_query += f"{retries}차 요약 결과:\n\n{summary}\n"
        user_query += f"{retries}차 요약 피드백:\n\n{evaluation_result}\n\n"

def main():
    ## 기사 링크 : https://zdnet.co.kr/view/?no=20250213091248
    input_article = """
오픈AI가 몇 주 안에 새로운 모델인 'GPT-4.5'를 출시하며 분산돼 있던 생성형 인공지능(AI) 모델을 통합키로 했다. 추론용 모델인 'o' 시리즈를 정리하고 비(非)추론 모델인 'GPT' 시리즈로 합칠 예정이다.

13일 업계에 따르면 샘 알트먼 오픈AI 최고경영자(CEO)는 지난 12일 자신의 X(옛 트위터)에 'GPT-4.5'를 조만간 출시할 것이라고 밝혔다. 현 세대인 'GPT-4o'의 뒤를 잇는 마지막 '비추론 AI'로, 내부적으로는 '오라이언(Orion)'이라고 불렸다.

현재 챗GPT 이용자를 비롯한 오픈AI의 고객들은 'GPT-4o', 'o1', 'o3-미니', 'GPT-4' 등 모델들을 각자 선택해 활용하고 있다. 최신 모델은 'GPT-4'를 개선한 'GPT-4o'로, 'GPT-4'는 2023년 하반기, 'GPT-4o'는 2024년 상반기 출시됐다.

오픈AI는 'GPT-5'도 지난해 공개하려고 했으나, 예상보다 저조한 성과를 거둬 출시가 연기된 상태다. 이에 그간 연산 시간을 늘려 성능을 높인 'o'시리즈 추론 모델을 새롭게 내세웠다.

샘 알트먼 CEO는 "이후 공개될 'GPT-5'부터는 추론 모델인 'o'시리즈와 'GPT'를 통합하겠다"며 "모델과 제품라인이 복잡해졌음을 잘 알고 있고, 앞으로는 각 모델을 선택해 사용하기보다 그저 잘 작동하길 원한다"고 말했다.
    """
    
    user_query = f"""
당신의 목표는 주어진 기사를 요약하는 것입니다. 
아래 주어진 기사 내용을 요약해주세요.
이전 시도의 요약과 피드백이 있다면, 이를 반영하여 개선된 요약을 작성하세요.

기사 내용: 
{input_article}
    """
    
    evaluator_prompt = """
다음 요약을 평가하십시오:

## 평가기준
1. 핵심 내용 포함 여부 
   - 원문의 핵심 개념과 논리적 흐름이 유지되어야 합니다.  
   - 불필요한 세부 사항은 줄이되, 핵심 정보가 누락되면 감점 요인입니다.  
   - 단어 선택이 다소 달라도, 주요 개념과 의미가 유지되면 PASS 가능합니다.  
   - 원문의 중요 개념 15% 이상이 빠졌다면 FAIL입니다.  

2. 정확성 & 의미 전달  
   - 요약이 원문의 의미를 왜곡하지 않고 정확하게 전달해야 합니다.  
   - 숫자, 인명, 날짜 등 객관적 정보가 틀리면 FAIL입니다.  
   - 문장이 다르게 표현되었더라도 원문의 의미를 유지하면 PASS 가능합니다.  
   - 논리적 비약이 크거나 잘못된 해석이 포함되면 FAIL입니다.  

3. 간결성 및 가독성  
   - 문장이 과하게 길거나 반복적이면 감점 요인입니다.  
   - 직역체 표현은 가독성을 해치지 않으면 허용 가능하지만, 지나치면 FAIL입니다.  
   - 일부 단어의 표현 방식이 달라도 자연스럽다면 PASS 가능합니다.  
   - 문장이 지나치게 어색해서 독해가 어렵다면 FAIL입니다.  

4. 문법 및 표현  
   - 맞춤법, 띄어쓰기 오류가 5개 이상이면 FAIL입니다.  
   - 사소한 문법 실수는 감점 요인이나, 의미 전달에 영향을 주면 FAIL입니다.  
   - 문장이 비문이거나 문맥상 어색한 표현이 많으면 FAIL입니다.  

## 평가결과 응답예시  
- 모든 기준이 충족되었으면 "평가결과 = PASS"를 출력하세요.
- 수정이 필요한 경우, 구체적인 문제점을 지적하고 반드시 개선 방향을 제시하세요.    
- 중대한 오류가 있다면 "평가결과 = FAIL"을 출력하고, 반드시 주요 문제점을 설명하세요.  
요약 결과 :
    """

    final_summary = loop_workflow(user_query, evaluator_prompt, max_retries=5)
    print("\n✅ 최종 요약:\n", final_summary)

if __name__ == "__main__":
    main()