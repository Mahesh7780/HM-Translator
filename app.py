from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

app = Flask(__name__)

# Supported languages (you can expand this list further)
SUPPORTED_LANGUAGES = {
    'eng_Latn': 'English',
    'fra_Latn': 'French',
    'deu_Latn': 'German',
    'spa_Latn': 'Spanish',
    'ita_Latn': 'Italian',
    'por_Latn': 'Portuguese',
    'rus_Cyrl': 'Russian',
    'zho_Hans': 'Chinese (Simplified)',
    'jpn_Jpan': 'Japanese',
    'kor_Hang': 'Korean',
    'arb_Arab': 'Arabic',
    'hin_Deva': 'Hindi',
    'tam_Taml': 'Tamil',
    'tel_Telu': 'Telugu',
    'ben_Beng': 'Bengali',
    'urd_Arab': 'Urdu',
    'nld_Latn': 'Dutch',
    'tur_Latn': 'Turkish',
    'vie_Latn': 'Vietnamese',
    'swh_Latn': 'Swahili',
    'tha_Thai': 'Thai',
    'ukr_Cyrl': 'Ukrainian',
    'pol_Latn': 'Polish',
    'ron_Latn': 'Romanian',
    'ces_Latn': 'Czech'
}

# Load model and tokenizer
MODEL_NAME = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def translate(text, src_lang="eng_Latn", tgt_lang="fra_Latn"):
    try:
        tokenizer.src_lang = src_lang
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(tgt_lang),
            max_length=512
        )
        result = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
        return result
    except Exception as e:
        return f"Translation error: {str(e)}"

@app.route('/')
def home():
    return render_template("index.html", languages=SUPPORTED_LANGUAGES)

@app.route('/translate', methods=['POST'])
def handle_translation():
    data = request.json
    text = data.get('text', '').strip()
    src = data.get('src', 'eng_Latn')
    tgt = data.get('tgt', 'fra_Latn')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    if src not in SUPPORTED_LANGUAGES or tgt not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported language code'}), 400

    translation = translate(text, src, tgt)
    
    if translation.startswith("Translation error:"):
        return jsonify({'error': translation}), 500

    return jsonify({'translation': translation})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
