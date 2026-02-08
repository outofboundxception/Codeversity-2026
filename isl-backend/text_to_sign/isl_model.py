import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))

ASSET_BASE = "sign_assets"

def process_sentence(text: str):
    text = text.lower()
    words = word_tokenize(text)
    words = [w for w in words if w.isalnum()]

    result = []
    for word in words:
        if word not in stop_words or word in ["i", "you", "me", "we"] or word.isdigit():
            result.append(lemmatizer.lemmatize(word))
    return result

def generate_isl_sequence(text: str):
    tokens = process_sentence(text)
    sequence = []

    for token in tokens:
        word_path = f"{ASSET_BASE}/words/{token}.jpg"
        if os.path.exists(word_path):
            sequence.append(word_path)
        else:
            for char in token:
                if char.isalpha():
                    sequence.append(f"{ASSET_BASE}/alphabets/{char}.jpg")
                elif char.isdigit():
                    sequence.append(f"{ASSET_BASE}/numbers/{char}.jpg")

    return sequence
