import pickle
import numpy as np
from tensorflow.keras.models import load_model

# Load the best model saved during training
best_model = load_model('/root/workspace/codes/model/Predict/best_model_.keras')


with open('/root/workspace/codes/model/Predict/scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)


# 회귀 예측 함수 정의
def predict_ipo_return(input_data):
    """
    입력 데이터를 받아 시초가 수익률을 예측하는 함수
    input_data는 {'ASVI_수요예측일': 값, 'ASVI_공모청약일': 값, 'ASVI_청약일_상장전일_기간': 값, '감성점수(평균)': 값, '기관청약경쟁률': 값, '의무보유확약률(%)': 값, '유통가능물량(백만원)': 값, '밴드수익률': 값} 형식으로 제공해야 함
    """

    # st.write(best_model)

    input_array = np.array([[
        input_data['ASVI_수요예측일'],
        input_data['ASVI_공모청약일'],
        input_data['ASVI_청약일_상장전일_기간'],
        input_data['감성점수(평균)'],
        input_data['기관청약경쟁률'],
        input_data['의무보유확약률(%)'],
        input_data['유통가능물량(백만원)'],
        input_data['밴드수익률']
    ]])

    #st.write(f"입력 데이터 (ndarray): {input_array}")

    # 스케일링
    scaled_regression_data = scaler.transform(input_array)
    #st.write(f"scaled_regression_data : {scaled_regression_data}")

    # 예측
    prediction = best_model.predict(scaled_regression_data)
    #st.write(f"prediction결과값: {prediction}")
    return prediction[0]
