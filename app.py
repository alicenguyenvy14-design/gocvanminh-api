from pathlib import Path
import os
import unicodedata
import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

bundle = joblib.load(Path(__file__).with_name('toxic_logreg_final.joblib'))
pipeline = bundle['pipeline']
threshold = float(bundle.get('threshold', 0.5))
toxic_index = list(pipeline.classes_).index(1)
app = FastAPI(title='Góc Văn Minh — Phân loại bình luận')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in os.getenv(
        'ALLOWED_ORIGINS', 'https://gocvanminh.odoo.com'
    ).split(',') if x.strip()],
    allow_credentials=False,
    allow_methods=['POST', 'GET'],
    allow_headers=['Content-Type'],
)

class Comment(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

@app.get('/health')
def health():
    return {'status': 'ok', 'model': 'TF-IDF + Logistic Regression'}

@app.post('/predict')
def predict(comment: Comment):
    text = ' '.join(unicodedata.normalize('NFC', comment.text).lower().split())
    if not text:
        raise HTTPException(422, 'Bình luận không được để trống.')
    score = float(pipeline.predict_proba([text])[0, toxic_index])
    label = int(score >= threshold)
    return {'label': label, 'result': 'Toxic' if label else 'Không toxic',
            'toxic_score': score}
