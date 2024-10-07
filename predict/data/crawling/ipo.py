import re
from bs4 import BeautifulSoup
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time

# Suppress only the insecure request warning
warnings.simplefilter('ignore', InsecureRequestWarning)

def fetch_ipo_data(url, max_retries=5, delay=2):
    # 재시도 로직
    for attempt in range(max_retries):
        try:
            # 요청을 보내고 HTML 페이지를 가져옵니다.
            response = requests.get(url, verify=False, timeout=10)
            if response.status_code == 200:
                break  # 성공적으로 데이터를 받으면 루프 탈출
        except requests.exceptions.RequestException as e:
            print(f"요청 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt + 1 == max_retries:
                print(f"최대 재시도 횟수 초과: {url}")
                return {}
            time.sleep(delay)  # 재시도 전에 잠깐 대기

    soup = BeautifulSoup(response.text, 'html.parser')

    # 결과를 저장할 딕셔너리
    ipo_data = {}

    try:
        # 데이터 추출
        total_shares = soup.find('td', string="총공모주식수")
        if total_shares:
            total_shares = total_shares.find_next_sibling('td').text.strip()
            ipo_data["총공모주식수"] = total_shares

        expected_price = soup.find('td', string="희망공모가액")
        if expected_price:
            expected_price = expected_price.find_next_sibling('td').text.strip()
            ipo_data["희망공모가액"] = expected_price

        final_price = soup.find('td', string="확정공모가")
        if final_price:
            final_price = final_price.find_next_sibling('td').text.strip()
            ipo_data["확정공모가"] = final_price
        
        # 기관경쟁률 추출
        institution_rate_label = soup.find('font', string="기관경쟁률")
        if institution_rate_label:
            institution_rate = institution_rate_label.find_parent('td').find_next_sibling('td').text.strip()
            ipo_data["기관경쟁률"] = institution_rate

        # 의무보유확약 추출
        holding_commitment_label = soup.find('font', string="의무보유확약")
        if holding_commitment_label:
            holding_commitment = holding_commitment_label.find_parent('td').find_next_sibling('td').text.strip()
            ipo_data["의무보유확약"] = holding_commitment

    except AttributeError as e:
        print(f"데이터 추출 중 오류 발생: {e} - URL: {url}")
    
    return ipo_data
