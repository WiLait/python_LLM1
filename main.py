import os
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")

# Collect model names from environment variables
MODELS = []
i = 1
while True:
    model_var = f"LLM_MODEL_{i}"
    model_name = os.getenv(model_var)
    if model_name is None:
        break
    MODELS.append(model_name)
    i += 1

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def ask_model(prompt: str, model_name: str) -> tuple[str, float]:
    started = time.perf_counter()
    try:
        response = client.chat.completions.create(
            model=model_name,
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
    results = []
    
    for model in MODELS:
        print(f"\nТестируем модель: {model}")
        for i, prompt in enumerate(prompts, start=1):
            print(f"  Запрос {i}/{len(prompts)}")
            answer, latency = ask_model(prompt, model)
            
            # Check if there was an error
            error = None
            if answer.startswith("Ошибка API:"):
                error = answer
            
            results.append({
                'model': model,
                'prompt_id': i,
                'latency': latency,
                'answer': answer,
                'error': error
            })
    
    # Save results to CSV file
    df = pd.DataFrame(results)
    df.to_csv('results.csv', index=False)
    print("\nРезультаты сохранены в файл results.csv")