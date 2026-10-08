import os
import sys
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

prompts = [
    "Объясни студенту 4 курса разницу между хешированием и симметричным шифрованием. Не более 120 слов.",
    "Определи тип события: «После 15 неудачных попыток входа с одного IP выполнен успешный вход администратора». Ответь одним словом.",
    "Суммируй следующий текст в одно предложение: «Zero Trust — это модель безопасности, которая требует строгой проверки каждого пользователя и устройства, пытающегося получить доступ к ресурсам сети, независимо от того, находятся они внутри периметра компании или снаружи».",
    "Извлеки из текста имя, должность и компанию: «Иван Петров, ведущий инженер по безопасности в ООО Ромашка, сегодня подписал отчет». Ответь в формате JSON.",
    "Напиши функцию на Python, которая принимает строку и возвращает True, если она является валидным email адресом, и False в противном случае. Без лишних пояснений.",
    "Найди ошибку в коде и объясни, как её исправить: def add(a, b): return a + b * 2 (при вызове add(2, 3) ожидается 10, а возвращается 8).",
    "У Алисы, Боба и Чарли есть три шляпы: красная, зеленая и синяя. Алиса не носит красную. Боб носит зеленую. Кто какую шляпу носит?",
    "Какие основные меры необходимо предпринять для защиты веб-приложения от SQL-инъекций? Назови не менее трех.",
    "Перепиши фразу в официально-деловом стиле: «Мы не можем сделать это в срок, потому что у нас сломалась база данных».",
    "Перечисли три главных преимущества использования VPN. Ответ должен строго содержать только нумерованный список без вступительных и заключительных слов."
]

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

def sanitize_filename(filename):
    """Replace invalid characters for filenames with underscores"""
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

if __name__ == "__main__":
    # Handle command line arguments
    selected_models = []
    
    if len(sys.argv) == 1:
        # No arguments provided - interactive mode
        print("Доступные модели:")
        for i, model in enumerate(MODELS, start=1):
            print(f"  [{i}] {model}")
        
        user_input = input("Введите номер модели для теста (или 'all' для всех): ")
        
        if user_input.lower() == 'all':
            selected_models = MODELS.copy()
        else:
            try:
                index = int(user_input) - 1
                if 0 <= index < len(MODELS):
                    selected_models = [MODELS[index]]
                else:
                    print("Ошибка: Неверный номер модели")
                    sys.exit(1)
            except ValueError:
                print("Ошибка: Введите число или 'all'")
                sys.exit(1)
    elif len(sys.argv) == 2:
        # One argument provided
        arg = sys.argv[1]
        if arg.lower() == 'all':
            selected_models = MODELS.copy()
        else:
            try:
                index = int(arg) - 1
                if 0 <= index < len(MODELS):
                    selected_models = [MODELS[index]]
                else:
                    print("Ошибка: Неверный номер модели")
                    sys.exit(1)
            except ValueError:
                print("Ошибка: Введите корректный номер модели или 'all'")
                sys.exit(1)
    else:
        # More than one argument provided - invalid
        print("Использование: python main.py [номер_модели|all]")
        sys.exit(1)
    
    results = []
    
    for model in selected_models:
        print(f"\nТестируем модель: {model}")
        for i, prompt in enumerate(prompts, start=1):
            print(f"  Запрос {i}/{len(prompts)}")
            answer, latency = ask_model(prompt, model)
            
            # Check if there was an error
            error = None
            if answer.startswith("Ошибка API:"):
                error = answer
                answer = None
            
            results.append({
                'model': model,
                'prompt_id': i,
                'latency': latency,
                'answer': answer,
                'error': error
            })
    
    # Save results to CSV file with appropriate filename
    if len(selected_models) == 1:
        filename = f"results_{sanitize_filename(selected_models[0])}.csv"
    else:
        filename = "results_all.csv"
        
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"\nРезультаты сохранены в файл {filename}")