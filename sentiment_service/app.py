from flask import Flask, jsonify, request
from llama_cpp import Llama
import os

app = Flask(__name__)

# Загрузка модели
MODEL_PATH = os.getenv('MODEL_PATH', '/models/llama-3-8b-instruct.Q4_K_M.gguf')
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=4
)

PROMPT_TEMPLATE = """[INST] Анализ настроения текста. Оцени от -100 до 100, где -100 крайне негативный, 100 крайне позитивный. Ответ только числом.
Текст: {text}
Ответ: [/INST]"""

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json.get('text', '')
    prompt = PROMPT_TEMPLATE.format(text=text[:2000])
    
    output = llm(
        prompt,
        max_tokens=10,
        temperature=0.1,
        stop=["\n"]
    )
    
    try:
        sentiment = int(output['choices'][0]['text'].strip())
        return jsonify({'sentiment': max(-100, min(100, sentiment))})
    except:
        return jsonify({'sentiment': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
