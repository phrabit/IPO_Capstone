from crawl_gpt import fetch_gpt_data
from crawl_open import fetch_open_data
from ipo import fetch_ipo_data

def merge_data():
    # 두 모듈의 데이터를 가져옴
    gpt_data = fetch_gpt_data()
    open_data = fetch_open_data()

    # 종목명을 비교할 때, 공백과 대소문자를 무시하도록 처리
    for gpt_item in gpt_data:
        for open_item in open_data:
            # 종목명을 모두 소문자로 변환하고, 공백 제거 후 비교
            if gpt_item['종목명'].replace(" ", "").lower() == open_item['종목명'].replace(" ", "").lower():
                gpt_item['시초가수익률(%)'] = open_item['시초가수익률(%)']
                break  # 매칭된 경우, 더 이상 검색하지 않고 다음 종목으로 넘어감

    # '시초가수익률(%)' 값이 있는 종목만 필터링
    merged_with_initial_rate = [item for item in gpt_data if '시초가수익률(%)' in item]

    # 각 종목의 링크를 사용하여 추가 정보를 가져와 병합
    for item in merged_with_initial_rate:
        # a 태그의 href에서 링크를 추출하여 IPO 데이터 가져오기
        link_tag = item.get('link')
        print(f"link_tag:{link_tag}")
        if link_tag:
            ipo_data = fetch_ipo_data(link_tag)
            
            # 병합된 데이터를 기존 딕셔너리에 추가
            item.update(ipo_data)

    # 병합된 데이터 출력
    for item in merged_with_initial_rate:
        print(item)

    return merged_with_initial_rate

if __name__ == '__main__':
    merge_data()
