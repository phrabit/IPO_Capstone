import streamlit as st
from catboost import CatBoostClassifier
from predict.get_data import get_stock_data
from predict.regression import predict_ipo_return

def run_predict():
    # Load the CatBoost model
    save_path = '/root/workspace/codes/model/Predict/best_catboost_model.cbm'
    loaded_model = CatBoostClassifier()
    loaded_model.load_model(save_path)
    st.subheader("💰 Predicting public stock opening prices")

    stock_name = st.text_input('Enter a stock name')

    if st.button('Predict'):
        ipo_data = get_stock_data(stock_name)

        if not stock_name:
            st.write("Enter a stock name")
        elif ipo_data is None:
            st.write(f"'{stock_name}'에 해당하는 데이터를 찾을 수 없습니다.")
        else:
            prediction = loaded_model.predict(ipo_data)

            st.markdown("---")  # 구분선
            st.markdown("### 📝 Input data")
            st.table({
                'ASVI_수요예측일': [ipo_data[0][0]],
                'ASVI_공모청약일': [ipo_data[0][1]],
                'ASVI_청약일_상장전일_기간': [ipo_data[0][2]],
                '감성점수(평균)': [ipo_data[0][3]],
                '기관청약경쟁률': [ipo_data[0][4]],
                '의무보유확약률(%)': [ipo_data[0][5]],
                '유통가능물량(백만원)': [ipo_data[0][6]],
                '밴드수익률': [ipo_data[0][7]]
            })

            st.markdown("---")
            st.markdown("### 🔮 Prediction results")
            if prediction[0] == 1:
                st.markdown("""
                <div style="padding: 10px; background-color: #DFF0D8; border-radius: 5px; border: 1px solid #D6E9C6;">
                    <h4>📈 Results: Rising</h4>
                </div>
                """, unsafe_allow_html=True)
            elif prediction[0] == 0:
                st.markdown("""
                <div style="padding: 10px; background-color: #F2DEDE; border-radius: 5px; border: 1px solid #EED3D7;">
                    <h4>📉 Results: Falling</h4>
                </div>
                """, unsafe_allow_html=True)

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
            
            # 예측된 수익률 카드 형태로 표시
            return_color = "#D6E9C6" if predicted_return[0] > 0 else "#EED3D7"
            st.markdown(f"""
            <div style="padding: 10px; background-color: {return_color}; border-radius: 5px; border: 1px solid #ddd;">
                <h4>📊 Predicted Opening Price Return: {predicted_return[0] * 100:.2f}%</h4>
            </div>
            """, unsafe_allow_html=True)