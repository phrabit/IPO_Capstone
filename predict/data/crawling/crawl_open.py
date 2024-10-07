# crawl_open.py
import re
from bs4 import BeautifulSoup
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.simplefilter('ignore', InsecureRequestWarning)

def fetch_open_data():
    link = 'http://ipo38.co.kr/ipo/index.htm?o=&key=7&page=1'
    response = requests.get(link, verify=False)
    response.encoding = 'euc-kr'
    
    soup = BeautifulSoup(response.text, 'html.parser')

    rows_white = soup.find_all('tr', {'bgcolor': '#FFFFFF'})
    rows_gray = soup.find_all('tr', {'bgcolor': '#F8F8F8'})
    rows = rows_white + rows_gray

    results = []

    for row in rows:
        columns = row.find_all('td')
        if len(columns) == 10:
            stock_name = columns[0].get_text(strip=True)
            stock_name = re.sub(r'\s*\(.*?\)', '', stock_name)
            initial_rate = columns[7].get_text(strip=True)
            
            if initial_rate not in ('%', '-%'):
                row_data = {
                    '종목명': stock_name,
                    '시초가수익률(%)': initial_rate
                }
                results.append(row_data)
    
    return results
