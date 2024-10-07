# crawl_gpt.py
import re
from bs4 import BeautifulSoup
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the insecure request warning
warnings.simplefilter('ignore', InsecureRequestWarning)

def fetch_gpt_data():
    # 두 링크 리스트
    links = [
        'http://www.38.co.kr/html/fund/index.htm?o=k&page=1',
        'http://www.38.co.kr/html/fund/index.htm?o=k&page=2'
    ]

    result_list = []

    # Loop over each link to scrape data
    for link in links:
        response = requests.get(link, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')

        rows = soup.find('table', {
            'width': '100%',
            'border': '0',
            'cellspacing': '0',
            'cellpadding': '3',
            'bgcolor': '#FFFFFF',
            'summary': '공모주 청약일정'
        }).find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 5:
                check_td = cells[2].text.strip()

                if check_td != "-":
                    stock_name_raw = cells[0].find('a').text.strip()
                    # 정규식으로 href 속성에 있는 URL 추출
                    pattern = r'href="(/html/fund/\?o=v&amp;no=\d+&amp;l=&amp;page=\d+)"'
                    match = re.search(pattern, str(cells[0]))
                    if match:
                        # 추출한 상대 경로 URL
                        relative_url = match.group(1)

                        # &amp;를 &로 변경하고, 절대 경로로 변환
                        absolute_url = 'http://www.38.co.kr' + relative_url.replace('&amp;', '&')

                        # 결과 출력
                        print(absolute_url)
                    else:
                        print("URL을 찾을 수 없습니다.")
                    stock_name = re.sub(r'\s*\(.*?\)', '', stock_name_raw)

                    ipo_schedule = cells[1].text.strip()
                    confirmed_ipo_price = cells[2].text.strip()
                    expected_ipo_price = cells[3].text.strip()
                    subscription_rate = cells[4].text.strip()
                    underwriter = cells[5].text.strip()

                    row_data = {
                        "종목명": stock_name,
                        "공모주 일정": ipo_schedule,
                        "확정공모가": confirmed_ipo_price,
                        "희망공모가": expected_ipo_price,
                        "청약경쟁률": subscription_rate,
                        "주간사": underwriter,
                        "link": absolute_url
                    }
                    print(absolute_url)
                    result_list.append(row_data)
    
    return result_list
