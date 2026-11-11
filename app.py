import json
import os
from flask import Flask, render_template, request
from google import genai
from google.genai import types

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-3.5-flash-lite"

SAMPLE_TEXT = (
    "Штучний інтелект (ШІ) — це галузь комп'ютерних наук, що займається створенням "
    "інтелектуальних машин, здатних виконувати завдання, які зазвичай вимагають людського інтелекту. "
    "До них належать візуальне сприйняття, розпізнавання мови, прийняття рішень та переклад між мовами. "
    "Машинне навчання (МН) є підгалуззю ШІ, яка надає системам здатність автоматично навчатися та "
    "вдосконалюватися на основі досвіду без явного програмування. Глибоке навчання використовує "
    "багаторівневі нейронні мережі для аналізу складних даних. Попри значний прогрес, розвиток ШІ "
    "викликає етичні занепокоєння, зокрема щодо конфіденційності даних, упередженості алгоритмів "
    "та можливої втрати робочих місць через автоматизацію."
)

LONG_DOCUMENT = (
    "Розділ 1. Вступ до штучного інтелекту.\n"
    "Штучний інтелект (ШІ) є однією з найважливіших технологій XXI століття. "
    "Він охоплює розробку алгоритмів, що дозволяють комп'ютерам імітувати людський розум. "
    "Основні напрями включають комп'ютерне бачення, обробку природної мови та робототехніку.\n\n"
    "Розділ 2. Машинне навчання та Нейронні мережі.\n"
    "Машинне навчання надає можливість аналізувати великі масиви даних та виявляти закономірності. "
    "Глибоке навчання побудоване на штучних нейронних мережах, які моделюють роботу людського мозку. "
    "Це дозволило досягти прориву у розпізнаванні образів, генерації тексту та синтезі мовлення.\n\n"
    "Розділ 3. Етичні та соціальні виклики ШІ.\n"
    "Швидкий розвиток ШІ створює низку ризиків. До них належать проблеми конфіденційності, "
    "алгоритмічна упередженість та загроза автоматизації робочих місць. "
    "Для мінімізації ризиків необхідне впровадження міжнародних стандартів регулювання ШІ."
) * 4

@app.route('/', methods=['GET', 'POST'])
def index():
    active_tab = request.form.get('active_tab', 'task1')
    results = {}

    if request.method == 'POST':
        try:
            if active_tab == 'task1':
                simple_prompt = f"Проаналізуй наведений текст та визнач його основні ідеї:\n\n{SAMPLE_TEXT}"
                
                advanced_prompt = f"""Ти викладач університету. Проаналізуй наведений текст.

Контекст:
{SAMPLE_TEXT}

Виконай завдання поетапно:
1. Визнач основну тему.
2. Виділи 3–5 ключових ідей.
3. Визнач основні поняття.
4. Сформулюй короткий висновок.

Результат подай у вигляді чітко структурованого маркованого списку."""

                res_simple = client.models.generate_content(model=MODEL_NAME, contents=simple_prompt).text
                res_advanced = client.models.generate_content(model=MODEL_NAME, contents=advanced_prompt).text

                results['task1'] = {
                    'simple_prompt': simple_prompt,
                    'simple_res': res_simple,
                    'advanced_prompt': advanced_prompt,
                    'advanced_res': res_advanced
                }
                
            elif active_tab == 'task2':
                single_prompt = f"Згенеруй 2 тестові питання з варіантами відповідей та вказанням правильної відповіді за текстом:\n\n{SAMPLE_TEXT}"
                res_single = client.models.generate_content(model=MODEL_NAME, contents=single_prompt).text

                p1 = f"Визнач основні поняття та ключові факти з тексту:\n\n{SAMPLE_TEXT}"
                step1_facts = client.models.generate_content(model=MODEL_NAME, contents=p1).text

                p2 = f"На основі цих виділених фактів сформуй 2 тестові запитання з 4 варіантами відповідей і вкажи правильну:\n\n{step1_facts}"
                step2_tests = client.models.generate_content(model=MODEL_NAME, contents=p2).text

                results['task2'] = {
                    'single_res': res_single,
                    'decomposed_res': f" Крок 1: Виділення фактів \n{step1_facts}\n\n Крок 2: Генерація тестів \n{step2_tests}"
                }

            elif active_tab == 'task3':
                react_prompt = f"""Проаналізуй текст та визнач, які твердження є фактами, а які — висновками або оцінками автора.

Текст:
{SAMPLE_TEXT}

Виконай завдання, дотримуючись суворої структури:
1. Задача: Сформулюй ціль аналізу.
2. План дій: Запиши кроки, які ти виконаєш.
3. Виконання: Проаналізуй текст за планом.
4. Перевірка: Зроби самоперевірку отриманих результатів.
5. Результат: Подай фінальний підсумок."""

                res_react = client.models.generate_content(model=MODEL_NAME, contents=react_prompt).text
                results['task3'] = {'react_res': res_react}

            elif active_tab == 'task4':
                json_prompt = f"""Проаналізуй текст та поверни результат у строго визначеному JSON форматі.

Текст:
{SAMPLE_TEXT}

Структура JSON повинена бути наступною:
{{
  "topic": "основна тема",
  "key_ideas": ["ідея 1", "ідея 2"],
  "keywords": ["слово 1", "слово 2"],
  "conclusion": "короткий висновок"
}}"""

                raw_json = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=json_prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                ).text

                try:
                    parsed_data = json.loads(raw_json)
                    parse_status = "Успішно розібрано через Python (json.loads)"
                except Exception as parse_err:
                    parsed_data = {"error": str(parse_err)}
                    parse_status = "Помилка валідації JSON"

                results['task4'] = {
                    'raw_json': raw_json,
                    'parsed_data': parsed_data,
                    'status': parse_status
                }

            elif active_tab == 'task5':

                no_chunk_prompt = f"Зроби підсумкове узагальнення документу:\n\n{LONG_DOCUMENT}"
                res_no_chunk = client.models.generate_content(model=MODEL_NAME, contents=no_chunk_prompt).text

                doc_len = len(LONG_DOCUMENT)
                chunk_size = doc_len // 3
                chunks = [LONG_DOCUMENT[i:i + chunk_size] for i in range(0, doc_len, chunk_size)]

                summaries = []
                for idx, chunk in enumerate(chunks, 1):
                    p = f"Зроби короткий висновок цього фрагмента тексту (Chunk {idx}):\n\n{chunk}"
                    s = client.models.generate_content(model=MODEL_NAME, contents=p).text
                    summaries.append(f"Фрагмент {idx}:\n{s}")

                combined_summaries = "\n\n".join(summaries)
                final_chunk_prompt = f"Об'єднай наступні окремі висновки у єдиний підсумковий документ:\n\n{combined_summaries}"
                res_chunked = client.models.generate_content(model=MODEL_NAME, contents=final_chunk_prompt).text

                overlap = 150
                sw_chunks = []
                start = 0
                while start < doc_len:
                    end = start + chunk_size
                    sw_chunks.append(LONG_DOCUMENT[start:end])
                    start = end - overlap if end < doc_len else doc_len
                
                sw_summaries = []
                for idx, sw_chunk in enumerate(sw_chunks, 1):
                    p = f"Зроби короткий висновок фрагмента тексту зі сковзним вікном (Window {idx}):\n\n{sw_chunk}"
                    s = client.models.generate_content(model=MODEL_NAME, contents=p).text
                    sw_summaries.append(f"Вікно {idx}:\n{s}")
                    
                    combined_sw = "\n\n".join(sw_summaries)
                    final_sw_prompt = f"Об'єднай наступні висновки, отримані через скользяще вікно, у єдиний підсумковий документ:\n\n{combined_sw}"
                    res_sw = client.models.generate_content(model=MODEL_NAME, contents=final_sw_prompt).text

                results['task5'] = {
                    'no_chunk_res': res_no_chunk,
                    'chunked_res': res_chunked,
                    'sw_res': res_sw,
                    'chunks_count': len(chunks),
                    'sw_chunks_count': len(sw_chunks)
                }

            elif active_tab == 'task6':
                test_prompt = "Придумай 3 оригінальні та креативні метафори для пояснення поняття 'Алгоритм'."

                temp_results = {}
                for t in [0.0, 0.5, 1.0]:
                    cfg = types.GenerateContentConfig(temperature=t)
                    resp = client.models.generate_content(model=MODEL_NAME, contents=test_prompt, config=cfg)
                    temp_results[str(t)] = resp.text

                topp_results = {}
                for p in [0.5, 0.8, 1.0]:
                    cfg = types.GenerateContentConfig(top_p=p, temperature=0.7)
                    resp = client.models.generate_content(model=MODEL_NAME, contents=test_prompt, config=cfg)
                    topp_results[str(p)] = resp.text

                results['task6'] = {
                    'temp_results': temp_results,
                    'topp_results': topp_results
                }

        except Exception as e:
            results['error'] = f"Виникла помилка під час запиту до API: {str(e)}"

    return render_template('index.html', active_tab=active_tab, results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)