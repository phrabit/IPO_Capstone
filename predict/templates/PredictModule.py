import streamlit as st
from catboost import CatBoostClassifier
from predict.get_data import get_stock_data
from predict.regression import predict_ipo_return

def run_predict():
    # Load the CatBoost model
    save_path = '/root/workspace/codes/model/Predict/best_catboost_model.cbm'
    loaded_model = CatBoostClassifier()
    loaded_model.load_model(save_path)
    st.subheader("공모주 시초가 예측")

    stock_name = st.text_input('종목명을 입력하세요')
    if st.button('Predict 시초가 수익률'):
        ipo_data = get_stock_data(stock_name)

        if not stock_name:
            st.write("종목명을 입력하세요.")
        elif ipo_data is None:
            st.write(f"'{stock_name}'에 해당하는 데이터를 찾을 수 없습니다.")
        else:
            prediction = loaded_model.predict(ipo_data)
            if prediction[0] == 1:
                st.write("Predicted 시초가 수익 예측: 상승")
            elif prediction[0] == 0:
                st.write("Predicted 시초가 수익 예측: 하락")
            new_input_data = {
                'ASVI_수요예측일': ipo_data[0][0],
                'ASVI_공모청약일': ipo_data[0][1],
                'ASVI_청약일_상장전일_기간': ipo_data[0][2],
                '감성점수(평균)': ipo_data[0][3],
                '기관청약경쟁률': ipo_data[0][4],
                '의무보유확약률(%)': ipo_data[0][5],
                '유통가능물량(백만원)': ipo_data[0][6],
                '밴드수익률': ipo_data[0][7]
            }
            predicted_return = predict_ipo_return(new_input_data)
            st.write(f"예측된 시초가 수익률: {predicted_return[0] * 100:.2f}%")
