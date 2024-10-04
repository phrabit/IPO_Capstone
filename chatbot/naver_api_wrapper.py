import re
import os
import json
import urllib.parse
import pandas as pd
from pydantic import BaseModel
# from openai import OpenAI # 이게 찐퉁이다! 하지만 아직 튜닝전이라 summary가 계속 반복되는 이슈 발생
from langchain.llms import OpenAI  # 이건 야매다. retrieve 과정 없으므로 빠른 채팅 가능 API 비용 아낌.
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI()

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
        prompt = f"입력된 내용을 query(질문)에 맞게 핵심만 요약해줘. query에 해당하는 내용이 없을 경우, ''를 반환해줘.\n\n제목: {title}\n내용: {description}\n질문: {query}"
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
    def run(self, query: str, max_row: int = 31):
        print("*@*@*@*@*@ RUN in NaverAPIWrapper CLASS *@*@*@*@*@")
        print(f"***************************쿼리:{query} Naver검색 중***************************")
        # 입력 query
        query_url = urllib.parse.quote(query)
        # 한 번에 표시할 검색 결과 개수 (기본값: 10, 최댓값: 100)
        display = 5
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

        for start_index in range(start, end, display):
            # url 설정
            print(f"*************************** URL 설정 start_index:{start_index} ***************************")
            url = "https://openapi.naver.com/v1/search/webkr?query=" + query_url + \
                  "&display=" + str(display) + \
                  "&start=" + str(start_index) + \
                  "&sort=" + sort
            # request library에 url 전달
            request = urllib.request.Request(url)
            # cliend ID 및 secret key 헤더로 추가
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)

            try:
                # request library를 이용해서 url, client ID, secret key가 포함된 request를 urlopen 함수에 전달
                response = urllib.request.urlopen(request)
                # response code
                rescode = response.getcode()
                # response code가 200인 경우 (정상작동)
                if rescode == 200:
                    # 
                    response_body = response.read()
                    items = json.loads(response_body.decode('utf-8'))['items']
                    # 불필요한 tag 제거
                    remove_tag = re.compile('<.*?>')
                    # 아이템 반복적으로 가져오기
                    # items가 1개 이상일 때 for문 적용
                    if len(items)>0:
                        for item_index in range(0, len(items)): 
                            link = items[item_index]['link']
                            # trash_links에 해당한다면 jump
                            if any(trash in link for trash in self.trash_links):
                                continue
                            else:
                                # title
                                title = cleaning_text(items[item_index]['title'])
                                # description
                                description = cleaning_text(items[item_index]['description'])
                                # summary
                                summary = self.summarize_text(title, description, query)
                                if summary != repr(''):
                                    print(f"*************************** description: {description} *******************")
                                    print(f"*************************** summary: {summary} ***************************")
                                    # summary를 리스트에 추가
                                    summaries.append(summary)
                                # df의 알맞은 index에 title, link, description 입력
                                df.loc[row_count] = [title, link, description]
                                row_count += 1
                    continue
                else:
                    print("Error Code:", rescode)
            except Exception as e:
                print("Exception:", e)
        # 모든 API 호출이 끝난 후
        if not summaries:  # 결과가 없는 경우
            return []  # 빈 리스트 반환
        return summaries  # 요약 리스트 반환
