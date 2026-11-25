
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

MODEL = os.environ.get("AI_MODEL", "gpt-5.5")

SYSTEM_PROMPT = """
Ты CRYPROGAMMA AI — универсальный помощник.

Ты умеешь:
- отвечать на вопросы;
- помогать с программированием;
- объяснять технологии;
- помогать с математикой;
- объяснять криптовалюты;
- общаться на разных языках.

Отвечай понятно, дружелюбно и по существу.
Не выдумывай факты.
Не проси пароли, приватные ключи и seed-фразы.
CRYPROGAMMA — демонстрационный кошелёк.
Не утверждай, что выполняешь реальные финансовые операции.
"""

histories = {}

def ask_ai(user_id, message):
    if not os.environ.get("OPENAI_API_KEY"):
        return "AI пока не настроен администратором."

    if not isinstance(message, str) or not message.strip():
        return "Напиши свой вопрос."

    if len(message) > 4000:
        return "Сообщение слишком длинное."

    history = histories.setdefault(str(user_id), [])

    history.append({
        "role": "user",
        "content": message.strip()
    })

    try:
        response = client.responses.create(
            model=MODEL,
            instructions=SYSTEM_PROMPT,
            input=history[-12:],
            max_output_tokens=1000
        )

        answer = response.output_text

        if not answer:
            answer = "Не удалось сформировать ответ."

        history.append({
            "role": "assistant",
            "content": answer
        })

        histories[str(user_id)] = history[-12:]

        return answer

    except Exception as error:
        print("AI ERROR:", str(error))
        history.pop()
        return "AI временно недоступен. Попробуй позже."


def clear_history(user_id):
    histories.pop(str(user_id), None)
