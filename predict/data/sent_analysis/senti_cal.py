import tensorflow as tf
import numpy as np
import pandas as pd
from transformers import BertTokenizer, TFBertForSequenceClassification

MODEL_NAME = "klue/bert-base"
MAX_SEQ_LEN = 64
NUM_LABELS = 3

tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
model = tf.keras.models.load_model('/root/workspace/codes/predict/data/sent_analysis/model/best_model.h5', custom_objects={'TFBertForSequenceClassification': TFBertForSequenceClassification})

def preprocess_text(text):
    tokens = tokenizer.encode_plus(text, max_length=MAX_SEQ_LEN, padding='max_length',
                                   truncation=True, return_tensors='tf')
    return [tokens['input_ids'], tokens['attention_mask'], tokens['token_type_ids']]

def predict_sentiment(text):
    preprocessed = preprocess_text(text)
    prediction = model.predict(preprocessed)

    if isinstance(prediction, tuple):
        logits = prediction[0]
    else:
        logits = prediction

    sentiment_score = tf.nn.softmax(logits, axis=-1).numpy()[0]
    sentiment_label = ['중립', '긍정', '부정']

    result = {sentiment_label[i]: float(sentiment_score[i]) for i in range(NUM_LABELS)}

    neutral_threshold = 0.5

    if result['중립'] >= neutral_threshold:
        final_sentiment = '중립'
    else:
        final_sentiment = '긍정' if result['긍정'] > result['부정'] else '부정'

    return final_sentiment

def get_sentiment_score(sentiment_type):
    if sentiment_type == '긍정':
        return 1.0
    elif sentiment_type == '중립':
        return 0.5
    else:  # 부정
        return 0.0

def analyze_sentiment(df):
    df['sentiment_type'] = df['content'].apply(predict_sentiment)
    df['sentiment_score'] = df['sentiment_type'].apply(get_sentiment_score)
    return df

df = pd.read_csv('/root/workspace/codes/predict/data/sent_analysis/data/zenix.csv', encoding = 'utf-8-sig')

result_df = analyze_sentiment(df)

print(result_df)