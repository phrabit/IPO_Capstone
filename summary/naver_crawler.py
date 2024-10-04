import time
import warnings
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class NaverCrawler:
    def naver(self, link):
        # 네이버 뉴스 크롤링 코드
        response = requests.get(link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        article_link = []
        title_list = []
        article_list = []
        date_list = []

        news_links = soup.find_all('a', attrs={'class': 'news_tit'})
        for i in range(min(10, len(news_links))):
            article_link.append(news_links[i].get('href'))
            title_list.append(news_links[i].get('title'))
            art_temp = soup.find_all('a', attrs={'class': 'info press'})[i]
            if art_temp.find('i') is not None:
                art_temp.find('i').decompose()
            article_list.append(art_temp.text)

        date = soup.find_all('span', attrs={'class': 'info'})
        for i in range(min(20, len(date))):
            date_temp = soup.find_all('span', attrs={'class': 'info'})[i]
            word_to_remove = '면'
            if word_to_remove in date_temp.text:
                continue
            date_list.append(date_temp.text)

        return article_link, article_list, title_list, date_list

    def convert_relative_date(self, relative_date):
        # 상대 날짜를 절대 날짜로 변환하는 코드
        if isinstance(relative_date, str):
            if '일 전' in relative_date:
                days_ago = int(relative_date.split('일 전')[0])
                current_date = datetime.today()
                modified_date = current_date - timedelta(days=days_ago)
                return modified_date.strftime('%Y.%m.%d.')  # Updated date format
            elif '시간 전' in relative_date:
                hours_ago = int(relative_date.split('시간 전')[0])
                current_date = datetime.today()
                modified_date = current_date - timedelta(hours=hours_ago)
                return modified_date.strftime('%Y.%m.%d.')  # Updated date format
            elif '분 전' in relative_date:
                minutes_ago = int(relative_date.split('분 전')[0])
                current_date = datetime.today()
                modified_date = current_date - timedelta(minutes=minutes_ago)
                return modified_date.strftime('%Y.%m.%d.')  # Updated date format
        return relative_date

    def crawling(self, stock):
        warnings.simplefilter(action='ignore', category=FutureWarning)
        keyword = f'"{stock}"%2B"공모주"'
        max_page = 3
        df = pd.DataFrame(columns=['link', 'article', 'name', 'title', 'date'])

        print(f"{stock} 크롤링 시작 !@!")

        # Calculate the date one month ago from the current date -> 현재는 24시간 내의 기사들만!
        one_month_ago = (datetime.now() - timedelta(days=30)).date()

        for j in range(max_page):
            try:
                if j == 0:
                    url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + keyword + "&sort=1&photo=0&field=0&pd=0&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:all,a:all&start=1"
                else:
                    url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + keyword + f"&sort=1&photo=0&field=0&pd=0&ds=&de=&mynews=0&office_type=0&office_section_code=0&news_office_checked=&office_category=0&service_area=0&nso=so:dd,p:all,a:all&start={j}1"

                naver_data = self.naver(url)

                if len(naver_data[0]) == 0 or len(naver_data[1]) == 0 or len(naver_data[2]) == 0 or len(naver_data[3]) == 0:
                    print(f"{stock} 크롤링 다시 해봐. 기사 0개야.")

                if len(naver_data[0]) < 10 or len(naver_data[1]) < 10 or len(naver_data[2]) < 10 or len(naver_data[3]) < 10:
                    new_rows = []
                    for i in range(len(naver_data[0])):
                        article_date_str = naver_data[3][i]
                        article_date = self.convert_relative_date(article_date_str)
                        article_date = datetime.strptime(article_date, "%Y.%m.%d.").date()
                        if article_date < one_month_ago:
                            # If the article date is older than one month ago, break the loop
                            return df
                        new_rows.append({
                            'link': naver_data[0][i],
                            'article': naver_data[1][i],
                            'name': stock,
                            'title': naver_data[2][i],
                            'date': article_date
                        })
                    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                    break

                new_rows = []
                for i in range(10):
                    article_date_str = naver_data[3][i]
                    article_date = self.convert_relative_date(article_date_str)
                    article_date = datetime.strptime(article_date, "%Y.%m.%d.").date()
                    if article_date < one_month_ago:
                        # If the article date is older than one month ago, break the loop
                        return df
                    new_rows.append({
                        'link': naver_data[0][i],
                        'article': naver_data[1][i],
                        'name': stock,
                        'title': naver_data[2][i],
                        'date': article_date
                    })
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)

                time.sleep(3)

            except Exception as e:
                print(f"An error occurred on page {j + 1}: {e}")
                print("Retrying after 5 seconds...")
                time.sleep(5)

        print(f"{stock} 크롤링 완료 !@! 기사 개수 (중복 제거 전):", len(df))
        # Remove duplicates based on the 'link' column
        df.drop_duplicates(subset='link', keep='first', inplace=True)
        print(f"{stock} 크롤링 완료 !@! 기사 개수 (중복 제거 후):", len(df))
        return df
