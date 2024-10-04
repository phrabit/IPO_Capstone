import pandas as pd

df = pd.read_csv('/root/workspace/codes/predict/data/real_final_ZZin.csv', encoding='utf-8')

def get_stock_data(stock_name):
    stock_data = df[df['종목명'] == stock_name]
    if stock_data.empty:
        return None, None
    # 분류/회귀 모델에 사용할 8개의 데이터
    ipo_features = ['ASVI_수요예측일', 'ASVI_공모청약일', 'ASVI_청약일_상장전일_기간', 
                    '감성점수(평균)', '기관청약경쟁률', '의무보유확약률(%)', 
                    '유통가능물량(백만원)', '밴드수익률']
    ipo_data = stock_data[ipo_features].values

    return ipo_data

