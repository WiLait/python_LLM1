import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("LLM_MODEL_1")

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def ask_model(prompt: str) -> tuple[str, float]:
    started = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Отвечай точно и по существу."},
                {"role": "user", "content": prompt},
            ],
        )
        elapsed = time.perf_counter() - started
        text = response.choices[0].message.content
        return text, elapsed
    except Exception as e:
        elapsed = time.perf_counter() - started
        return f"Ошибка API: {str(e)}", elapsed

if __name__ == "__main__":
    answer, latency = ask_model("Объясни разницу между хешированием и шифрованием.")
    print(answer)
    print(f"\nВремя ответа: {latency:.2f} с")