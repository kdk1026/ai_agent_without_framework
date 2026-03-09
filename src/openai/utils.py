import os
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI, RateLimitError


load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

client = AsyncOpenAI(
    api_key=openai_api_key,  
)
sync_client = OpenAI(
    api_key=openai_api_key,
)

# 모델 설정 (기본 모델 지정)
DEFAULT_MODEL = "gpt-5-mini"

def llm_call(prompt: str,  model: str = DEFAULT_MODEL) -> str:
    """동기 호출 방식"""

    try:
        messages = []
        messages.append({"role": "user", "content": prompt})
        chat_completion = sync_client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return chat_completion.choices[0].message.content
    except RateLimitError as e:
        print("OpenAI API 사용량 초과 (429): 잠시 후 다시 시도하세요.")
    except Exception as e:
        print(f"오류 발생: {e}") 

async def llm_call_async(prompt: str,  model: str = DEFAULT_MODEL) -> str:
    """비동기 호출 방식 """
    
    try:
        messages = []
        messages.append({"role": "user", "content": prompt})
        chat_completion = await client.chat.completions.create(
            model=model,
            messages=messages,
        )
        print(model,"완료")
        
        return chat_completion.choices[0].message.content
    except RateLimitError as e:
        print("OpenAI API 사용량 초과 (429): 잠시 후 다시 시도하세요.")
    except Exception as e:
        print(f"오류 발생: {e}") 


if __name__ == "__main__":
    test = llm_call("안녕")
    print(f"동기 호출 결과: {test}")