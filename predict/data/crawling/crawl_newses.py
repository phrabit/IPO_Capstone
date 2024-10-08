from link_crawler import NaverCrawler
from summary.news_extractor import extract_title_content
from codes.predict.data.crawling.crawl_test import merge_data
import pandas as pd
from datetime import datetime, timedelta

def parse_start_date(date_range):
    # '공모주 일정' 값에서 첫 번째 날짜(시작 날짜)를 추출하는 함수
    start_date_str = date_range.split('~')[0].strip()
    return datetime.strptime(start_date_str, "%Y.%m.%d")

def main(merged_with_initial_rate):
    crawler = NaverCrawler()
    all_df = pd.DataFrame()

    for stock_info in merged_with_initial_rate:
        stock = stock_info['종목명']
        ipo_date_range = stock_info['공모주 일정']

        # '공모주 일정'에서 첫 번째 날짜를 추출하고 30일을 뺌
        start_date = parse_start_date(ipo_date_range)
        one_month_ago = (start_date - timedelta(days=30)).date()
        print(f"one_month_ago:{one_month_ago}")

        # 종목명을 입력하여 뉴스 데이터 크롤링
        df = crawler.crawling(stock, one_month_ago)

        if df.empty:
            print(f"{stock}에 대한 기사를 찾을 수 없습니다.")
            continue

        # 각 row마다 기사 제목과 본문을 추출하여 'content' 컬럼에 추가
        df['content'] = df.apply(lambda row: extract_title_content(row)[1], axis=1)
        print("본문 추가 완료 @@@@@@@@@@@@@@")
        print(df['content'])

        # 해당 종목명에 대한 데이터프레임을 통합
        all_df = pd.concat([all_df, df], ignore_index=True)

    # 최종 데이터프레임 저장 또는 출력
    print(f"크롤링 완료. 총 {len(all_df)}개의 기사 데이터 수집 완료.")
    print(all_df)
    all_df.to_csv("zenix.csv", index = False, encoding = "utf-8-sig")
    return all_df

if __name__ == '__main__':
    # 종목명을 입력
    # merged_with_initial_rate = merge_data
    # Given list of dictionaries
    merged_with_initial_rate = [
        {'종목명': '제닉스', '공모주 일정': '2024.09.19~09.20', '확정공모가': '40,000', '희망공모가': '28,000~34,000', '청약경쟁률': '895.75:1', '주간사': '신영증권,KB증권', '시초가수익률(%)': '47.5%'}
        # {'종목명': 'KB스팩30호', '공모주 일정': '2024.09.10~09.11', '확정공모가': '2,000', '희망공모가': '2,000~2,000', '청약경쟁률': '619.62:1', '주간사': 'KB증권', '시초가수익률(%)': '42%'},
        # {'종목명': '아이언디바이스', '공모주 일정': '2024.09.09~09.10', '확정공모가': '7,000', '희망공모가': '4,900~5,700', '청약경쟁률': '1964.99:1', '주간사': '대신증권', '시초가수익률(%)': '157.14%'},
        # {'종목명': '미래에셋비전스팩7호', '공모주 일정': '2024.09.02~09.03', '확정공모가': '2,000', '희망공모가': '2,000~2,000', '청약경쟁률': '1004.03:1', '주간사': '미래에셋증권', '시초가수익률(%)': '37%'},
        # {'종목명': '아이스크림미디어', '공모주 일정': '2024.08.21~08.22', '확정공모가': '32,000', '희망공모가': '32,000~40,200', '청약경쟁률': '12.89:1', '주간사': '삼성증권', '시초가수익률(%)': '-7.19%'},
        # {'종목명': '이엔셀', '공모주 일정': '2024.08.12~08.13', '확정공모가': '15,300', '희망공모가': '13,600~15,300', '청약경쟁률': '928.06:1', '주간사': 'NH투자증권', '시초가수익률(%)': '129.41%'},
        # {'종목명': '엠83', '공모주 일정': '2024.08.12~08.13', '확정공모가': '16,000', '희망공모가': '11,000~13,000', '청약경쟁률': '638.05:1', '주간사': '신영증권,유진투자증권', '시초가수익률(%)': '62.5%'},
        # {'종목명': '티디에스팜', '공모주 일정': '2024.08.09~08.12', '확정공모가': '13,000', '희망공모가': '9,500~10,700', '청약경쟁률': '1608.17:1', '주간사': '한국투자증권', '시초가수익률(%)': '107.69%'},
        # {'종목명': '대신밸런스스팩18호', '공모주 일정': '2024.08.09~08.12', '확정공모가': '2,000', '희망공모가': '2,000~2,000', '청약경쟁률': '135.53:1', '주간사': '대신증권', '시초가수익률(%)': '31%'},
        # {'종목명': '케이쓰리아이', '공모주 일정': '2024.08.08~08.09', '확정공모가': '15,500', '희망공모가': '12,500~15,500', '청약경쟁률': '34.28:1', '주간사': '하나증권', '시초가수익률(%)': '1.94%'},
        # {'종목명': '전진건설로봇', '공모주 일정': '2024.08.08~08.09', '확정공모가': '16,500', '희망공모가': '13,800~15,700', '청약경쟁률': '1087.26:1', '주간사': '미래에셋증권', '시초가수익률(%)': '66.67%'},
        # {'종목명': '넥스트바이오메디컬', '공모주 일정': '2024.08.07~08.08', '확정공모가': '29,000', '희망공모가': '24,000~29,000', '청약경쟁률': '65.83:1', '주간사': '한국투자증권', '시초가수익률(%)': '-6.9%'},
        # {'종목명': '유라클', '공모주 일정': '2024.08.06~08.07', '확정공모가': '21,000', '희망공모가': '18,000~21,000', '청약경쟁률': '1080.44:1', '주간사': '키움증권', '시초가수익률(%)': '32.86%'}
    ]
    # Run the main function with the list of stock names
    result_df = main(merged_with_initial_rate)
