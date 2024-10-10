import re
import os
import json
import urllib.parse
import pandas as pd
from pydantic import BaseModel
from openai import OpenAI # 이게 찐퉁이다! 하지만 아직 튜닝전이라 summary가 계속 반복되는 이슈 발생
# from langchain.llms import OpenAI  # 이건 야매다. retrieve 과정 없으므로 빠른 채팅 가능 API 비용 아낌.
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

# 웹드라이버 설정
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 화면 출력 없이 실행하려면 이 옵션을 사용
options.add_argument('--no-sandbox')  # Colab 환경에서 실행할 때 필요한 옵션
options.add_argument('--disable-dev-shm-usage')  # Colab 환경에서 실행할 때 필요한 옵션
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')

# 버전에 상관 없이 os에 설치된 크롬 브라우저 사용
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(3)

# 불필요한 특수문자를 제거해주는 함수
def cleaning_text(text: str) -> str:
    text = re.sub(' +', ' ', text)  # ' +'를 ' '로 대체
    text = re.sub('\n', '', text)
    text = re.sub('\r\r\r', '', text)  # '\r\r\r' 문자 제거
    text = re.sub('\r', '', text)  # '\r' 문자 제거
    text = re.sub('\u200b', '', text)
    text = re.sub('\xa0', '', text)
    text = re.sub('[-=+,#/\?:^$@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', text)
    return text

class NaverAPIWrapper(BaseModel):
    client_id: str # API Key ID
    client_secret: str # API Secret Key
    trash_links: list # 제외할 link type

    # 텍스트 요약 함수
    def summarize_text(self, title, description, query): # 인자로 기사의 제목(Title), 요약내용(Description), 질문(query)을 받음
        print("*@*@*@*@*@ SUMMARIZE_TEXT in NaverAPIWrapper CLASS *@*@*@*@*@")
        # Prompt
        # prompt = f"입력된 내용을 query(질문)에 맞게 핵심만 요약해줘. query에 해당하는 내용이 없을 경우, ''를 반환해줘.\n\n제목: {title}\n내용: {description}\n질문: {query}"
        prompt = f"""다음 블로그 본문 내용을 1개의 문장으로 요약해줘.
        또한 각 문장은 마침표('.')로 끝나야 하고, 문장은 반드시 한 문장으로 간결하게 작성해줘. 
        '{query}'와 관련된 핵심 내용만 포함해줘.\n\n기사 본문: {description}"""
        
        print(f"***************************Prompt Type:{type(prompt)}***************************")
        # OpenAI clinet를 이용해 요약 시작
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a summarizer."},
                {"role": "user", "content": prompt}
            ]
        )
        # 요약된 텍스트
        summary = completion.choices[0].message.content.strip()
        # 요약된 텍스트 반환
        return summary

    # API 호출하는 함수
    def run(self, query: str, max_row: int = 1):
        print("*@*@*@*@*@ RUN in NaverAPIWrapper CLASS *@*@*@*@*@")
        print(f"***************************쿼리:{query} Naver검색 중***************************")
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        # selenium으로 검색 페이지 불러오기 #
        naver_urls = []
        postdate = []
        titles = []
        contents = []
        comments_texts = []
        # 입력 query
        query_url = urllib.parse.quote(query)
        # 한 번에 표시할 검색 결과 개수 (기본값: 10, 최댓값: 100)
        display = 1
        # 검색 시작 위치 (기본값: 1, 최댓값: 1000)
        start = 1
        # 검색 종료 위치 (최댓값: 1000)
        end = max_row
        # 검색 결과 정렬 방법 (sim: 정확도 순으로 내림차순 정렬 (기본값) / date: 날짜순으로 내림차순 정렬)
        sort = 'sim'

        # df 데이터프레임 생성
        df = pd.DataFrame(columns=['Title', 'Link', 'Description'])
        summaries = []  # 요약된 내용을 저장할 리스트
        # df['Summary'] = ''
        # row_count 변수 생성 및 초기화
        row_count = 0
        print(f"end:{end}")
        print(f"display:{display}")
        for start_index in range(end):
            # url 설정
            print(f"*************************** URL 설정 start_index:{start_index} ***************************")
            url = "https://openapi.naver.com/v1/search/blog?query=" + query_url + "&start=" + str(start_index+1) + "&display=" + str(display+1) + "&sort=" + sort # JSON 결과
            print(f"url:{url}")
            # url = "https://openapi.naver.com/v1/search/webkr?query=" + query_url + \
            #       "&display=" + str(display) + \
            #       "&start=" + str(start_index) + \
            #       "&sort=" + sort
            # request library에 url 전달
            request = urllib.request.Request(url)
            print(f"request:{request}")
            # cliend ID 및 secret key 헤더로 추가
            request.add_header("X-Naver-Client-Id",client_id)
            request.add_header("X-Naver-Client-Secret",client_secret)

            try:
                # request library를 이용해서 url, client ID, secret key가 포함된 request를 urlopen 함수에 전달
                response = urllib.request.urlopen(request)
                print(f"response:{response}")
                # response code
                rescode = response.getcode()
                print(f"rescode:{rescode}")
                # response code가 200인 경우 (정상작동)
                if rescode == 200:
                    response_body = response.read()
                    items = json.loads(response_body.decode('utf-8'))['items']
                    # 불필요한 tag 제거
                    remove_tag = re.compile('<.*?>')
                    # 아이템 반복적으로 가져오기
                    # items가 1개 이상일 때 for문 적용
                    
                    for row in items:
                        if('blog.naver' in row['link']):
                            naver_urls.append(row['link'])
                            postdate.append(row['postdate'])
                            title = row['title']
                            # html태그제거
                            pattern1 = '<[^>]*>'
                            title = re.sub(pattern=pattern1, repl='', string=title)
                            title = str(title)
                            titles.append(title)
                    time.sleep(2)
                else:
                    print("Error Code:" + rescode)
            except Exception as e:
                print("Exception:", e)
                    
        ###naver 기사 본문 및 제목 가져오기###
        # ConnectionError방지
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}
        naver_urls = [str(url) for url in naver_urls]
        naver_urls = list(dict.fromkeys(naver_urls))
        # print(f"naver_urls:{naver_urls}")
        postdate = [str(date) for date in postdate]
        postdate = list(dict.fromkeys(postdate))
        # print(f"postdate:{postdate}")
        titles = [str(title) for title in titles]
        titles = list(dict.fromkeys(titles))
        # print(f"titles:{titles}")
        try:
            for i in naver_urls:
                print(f"url 갯수:{len(naver_urls)}")
                print(i)
                driver.get(i)
                time.sleep(1)  # 대기시간 변경 가능

                iframe = driver.find_element(By.ID , "mainFrame") # id가 mainFrame이라는 요소를 찾아내고 -> iframe임
                driver.switch_to.frame(iframe) # 이 iframe이 내가 찾고자하는 html을 포함하고 있는 내용

                source = driver.page_source
                html = BeautifulSoup(source, "html.parser")
                # 검색결과 확인용
                # with open("Output.txt", "w") as text_file:
                #     text_file.write(str(html))
                
                # 기사 텍스트만 가져오기
                content = html.select("div.se-main-container")
                #  list합치기
                content = ''.join(str(content))

                # html태그제거 및 텍스트 다듬기
                content = re.sub(pattern=pattern1, repl='', string=content)
                pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
                content = content.replace(pattern2, '')
                content = content.replace('\n', '')
                content = content.replace('\u200b', '')
                content = str(content)
                # print(f"이번 content:{content}")
                contents.append(content)
                # print(f"contents[0]의 TYPE: {type(contents[0])}")
                # print(f"contents의 TYPE: {type(contents)}")

            for idx in range(len(naver_urls)): 
                # title - Ensure it's a string
                title = titles[idx]
                # print(f"일번 title:{title}")
                # content - Ensure it's a string
                content = contents[idx]
                # print(f"일번 content:{content}")
                # summary
                summary = self.summarize_text(str(title), str(content), str(query))
                if summary != repr(''):
                    print(f"*************************** content: {content} *******************")
                    print(f"*************************** summary: {summary} ***************************")
                    # summary를 리스트에 추가
                    summaries.append(summary)
                # Update news_df with cleaned values
                # news_df.loc[item_index, 'title'] = title
                # news_df.loc[item_index, 'content'] = content
        except:
            contents.append('error')          
                    
                    
        # 모든 API 호출이 끝난 후
        if not summaries:  # 결과가 없는 경우
            return []  # 빈 리스트 반환
        return summaries  # 요약 리스트 반환
