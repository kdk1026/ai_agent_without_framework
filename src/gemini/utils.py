import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')

# 제미나이는 하나의 클라이언트로 동기/비동기 모두 지원합니다.
client = genai.Client(api_key=gemini_api_key)

# 모델 설정 (기본 모델 지정)
DEFAULT_MODEL = "gemini-3-flash-preview"

def llm_call(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """동기 호출 방식"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text
    except Exception as e:
        if "429" in str(e):
            print("대기 시간이 필요합니다. API 사용량이 초과되었습니다. (잠시 후 다시 시도)")
        else:
            print(f"오류 발생: {e}")
    
async def llm_call_async(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """비동기 호출 방식 (client.aio 사용)"""

    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents=prompt
        )
        print(model, "완료")
        return response.text
    except Exception as e:
        if "429" in str(e):
            print("대기 시간이 필요합니다. API 사용량이 초과되었습니다. (잠시 후 다시 시도)")
        else:
            print(f"오류 발생: {e}")


if __name__ == "__main__":
    # 1. 동기 호출 테스트
    test = llm_call("안녕")
    print(f"동기 호출 결과: {test}")