import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 화면 출력 없이 실행하려면 이 옵션을 사용
options.add_argument('--no-sandbox')  # Colab 환경에서 실행할 때 필요한 옵션
options.add_argument('--disable-dev-shm-usage')  # Colab 환경에서 실행할 때 필요한 옵션
options.add_argument('--disable-gpu')
options.add_argument('--disable-software-rasterizer')

# 1) 맨 첫 버전
# driver = webdriver.Chrome(options=options)  # 'chromedriver'는 PATH에 있는 경우 생략 가능

# 2) 1차 수정 - 로컬 실행은 됨
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 3) 2차 수정 - Streamlit Cloud에서 Webdriver 실행되게 하는 코드 -> But, 로컬 및 클라우드 상에서도 실행 X
# driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)

print("Chrome WebDriver Version:", driver.capabilities['chrome']['chromedriverVersion'])
base_url = "https://www.naver.com"
driver.quit()

class NewsCrawler:
  def mt(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('h1',{'class':'subject'})
    if title is None:
      title=''
    else:
      title=title.text
    text=soup.find('div',{'id':'textBody'})
    if text is None:
      text=''
    else:
      text=text.text
    return title, text

  def mk(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup = BeautifulSoup(response.text,'html.parser')
    title=soup.find('h2',{'class':'news_ttl'})
    if title is None:
      title = soup.find('div',{'class':'news_title_text'})
      if title is None:
        title = ''
      else:
        title = title.find('h1', {'class':'top_title'}).text
    else:
      title=title.text

    content = soup.find('div',{'class':'news_cnt_detail_wrap'})
    if content is None:
      # 예외처리 시작
      content = soup.find('div',{'itemprop':'articleBody'})
      if content is None:
        content = soup.find('h1',{'class':'page_ttl f12_stit'})
        if content is None:
          content = ''
        else:
          content = content.text
      else:
        content = content.text
      # 예외처리 끝
    else:
      content = content.text
    return title, content

  def sedaily(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('h1',{'class':'art_tit'})
    if title is None:
      title=soup.find('div',{'class':'sub_view'}).find('div').find('h2')
      if title is None:
        title = ''
      else:
        title = title.text
    else:
      title=title.text
    content=soup.find('div',{'class':'article_view'})
    if content is None:
      content=soup.find('div',{'itemprop':'articleBody'})
      if content is None:
        content = ''
      else:
        content = content.text
    else:
      content=content.text
    return title, content

  def thebell(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('p',{'class':'tit'})
    if title is None:
      title=''
    else:
      title=title.text
    content=soup.find('div',{'class':'viewSection'})
    if content is None:
      content=''
    else:
      content=content.text[60:]
    return title, content

  def hankyung(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    driver.implicitly_wait(3)
    try:
      title = driver.find_element('class name', 'article-contents')
      if title is None:
        title=''
      else:
        title=title.find_element('class name', 'headline').text
    except:
      title = driver.find_element('class name', 'article-tit').text

    text = driver.find_element('class name', 'article-body').text
    return title, text

  def etoday(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('h1',{'class':'main_title'})
    if title is None:
      title=''
    else:
      title=title.text
    text=soup.find('div',{'class':'articleView'})
    content_list=[]
    if text is None:
      text=''
    else:
      text=text.find_all('p')
      for i in range(len(text)):
        content_list.append(text[i].text)
      text=" ".join(content_list) #본문
    return title, text

  def moneys(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('h1',{'class':'title'})
    if title is None:
      title=soup.find('h1',{'class':'mgt37'}).text
    else:
      title=title.text
    content = soup.find('article', {'class':'article'})
    content = content.find('div', {'class':'bottom'})
    conetent = content.find('div', {'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content

  def asiae(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('h1',{'class':'mainTitle'})
    if title is None:
      # 예외
      title=soup.find('div', {'class':'area_title'})
      if title is None:
        title = ''
      else:
        title = title.find('h1').text
      # 예외 끝
    else:
      title=title.text
    text=soup.find('div',{'class':'va_cont'})
    content_list=[]
    if text is None:
      # 예외
      text=soup.find('div',{'itemprop':'articleBody'})
      if text is None:
        text=''
      else:
        text=text.find_all('p')
        content_list=[]
        for i in range(len(text)):
          content_list.append(text[i].text)
        text=" ".join(content_list) #본문
      # 예외 끝
    else:
      text=text.find_all('p')
      content_list=[]

      for i in range(len(text)):
        content_list.append(text[i].text)
      text=" ".join(content_list) #본문
    return title, text

  def seoulfn(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('div',{'class':'article-head-title'})
    if title is None:
      title=''
    else:
      title=title.text
    text=soup.find('div',{'id':'article-view-content-div'})
    content_list=[]
    if text is None:
      text=''
    else:
      text=text.find_all('p')

      for i in range(len(text)):
        content_list.append(text[i].text)
      text=" ".join(content_list) #본문
    return title,  text

  def dealsite(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('div',{'class':'read-news-title'})
    if title is None:
      title=''
    else:
      title=title.text
    text=soup.find('div',{'class':'rnmc-right rnmc-right1 content-area'})
    content_list=[]
    if text is None:
      text=''
    else:
      text=text.find_all('p')

      for i in range(len(text)):
        content_list.append(text[i].text)
      text=" ".join(content_list) #본문
    return title, text

  def bizwatch(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')
    title=soup.find('div',{'class':'top_content'}).find('h1')
    if title is None:
      title=''
    else:
      title=title.text

    text=soup.find('div',{'itemprop':'articleBody'})
    content_list=[]
    if text is None:
      text=''
    else:
      text=text.find_all('p')

      for i in range(len(text)):
        content_list.append(text[i].text)
      text=" ".join(content_list) #본문
    return title, text

  def economist(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.get(link)
    driver.implicitly_wait(3)
    title = driver.find_element('id', 'article_body')
    if title is None:
      title=''
    else:
      title=title.find_element('class name', 'view-article-title').text
    text = driver.find_element('class name', 'content').text
    return title, text

  def license_news(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.get(link)
    driver.implicitly_wait(3)
    title = driver.find_element('class name', 'article-view-header')
    if title is None:
      title=''
    else:
      title=title.find_element('class name', 'heading').text
    text = driver.find_element('id', 'article-view-content-div').text
    return title, text

  def sisa(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.get(link)
    driver.implicitly_wait(3)
    title = driver.find_element('class name', 'article-header-wrap')
    if title is None:
      title=''
    else:
      title=title.find_element('class name', 'article-head-title').text
    text = driver.find_element('id', 'article-view-content-div').text
    return title, text

  def chungcheong(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.get(link)
    driver.implicitly_wait(3)
    title = driver.find_element('class name', 'article-view-header')
    if title is None:
      title=''
    else:
      title=title.find_element('class name', 'heading').text
    text = driver.find_element('id', 'article-view-content-div').text
    return title, text

  def chosun(self, link):
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    driver.get(link)
    driver.implicitly_wait(3)
    title = driver.find_element('class name', 'article-header__headline')
    if title is None:
      title=''
    else:
      title=title.text
    text = driver.find_element('class name', 'article-body').text
    return title, text

  def jkmail(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'article-header-wrap'})
    if title is None:
      title=''
    else:
      title=title.find('div', {'class':'article-head-title'}).text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def inv(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'articleHeader'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'class':'WYSIWYG articlePage'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def yn(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('p', {'class':'article-top-title'})
    if title is None:
      # 예외
      title=soup.find('h1', {'class':'article-top-title'})
      if title is None:
        title = ''
      else:
        title = title.text


    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def cbc(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'article-header-wrap'})
    if title is None:
      title=''
    else:
      title=title.find('div', {'class':'article-head-title'}).text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def blt(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('header',{'class':'article-view-header'})
    if title is None:
      title=''
    else:
      title=title.find('h1', {'class':'heading'}).text

    content = soup.find('article',{'itemprop' : 'articleBody'})
    if content is None:
      content = ''
    else:
      content=content.text
    return title, content # title, content 완료

  def thefact(self, link):
    response = requests.get(link)
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h2',{'class':'articleTitle'})
    if title is None:
      title=soup.find('div',{'class':'articleTitle'})
      if title is None:
        title = ''
      else:
        title = title.text
    else:
      title=title.text

    content = soup.find('div',{'class' : 'mArticle'})
    if content is None:
      content = soup.find('div',{'itemprop' : 'articleBody'})
      if content is None:
        content = ''
      else:
        content = content.text
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def asiaa(self, link):
    response = requests.get(link)  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h3',{'class':'heading'})
    if title is None:
      title=''
    else:
      title=title.text

    content = soup.find('article',{'id' : 'article-view-content-div'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def culture(self, link):
    response = requests.get(link)  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h3',{'class':'heading'})
    if title is None:
      title=''
    else:
      title=title.text

    content = soup.find('div',{'style' : 'text-align:center'})
    if content is None:
      content = soup.find('div',{'class' : 'article-body'})
      if content is None:
        content = ''
      else:
        content = content.text
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def pim(self, link):
    response = requests.get(link)  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h2',{'id':'main-title'})
    if title is None:
      title=''
    else:
      title=title.text

    content = soup.find('div',{'id':'news-contents'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def e_daily(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'news_titles'})
    if title is None:
      title=''
    else:
      title=title.find('h1').text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def biz_post(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'detail_title'})
    if title is None:
      title=''
    else:
      title=title.find('h2').text

    content=soup.find('div',{'class':'detail_editor'})
    if content is None:
      content=soup.find('dd',{'class':'clearfix'})
      if content is None:
        content = ''
      else:
        content = content.text
    else:
      content=content.text
    return title, content # title, content 완료

  def sisa_e(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'heading'})
    if title is None:
      title=''
    else:
      title=title.text
    content_list = []
    content=soup.find('article',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def fn_news(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'tit_view'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'id':'article_content'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def international_news(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h3',{'class':'heading'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('article',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def daily_ahn(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'title'})
    if title is None:
      title=''
    else:
      title=title.text

    content_list = []
    content=soup.find('div',{'class':'article'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def mtn(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'news-header'})
    if title is None:
      title=''
    else:
      title=title.find('h1').text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def aju_e(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'inner font_num1'})
    if title is None:
      title=''
    else:
      title=title.find('h1').text

    # 본문 추출
    content = soup.find('section', {'class': 'article_wrap left_content'})
    content = content.find('div', {'itemprop': 'articleBody'})
    print(content)
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def news_tomato(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'rn_stitle'})
    if title is None:
      title=''
    else:
      title=title.text

    content_list = []
    content=soup.find('div',{'class':'rns_text'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def news1(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'title'})
    if title is None:
      title=soup.find('div',{'class':'photo_article'})
      if title is None:
        title = ''
      else:
        title = title.find('h3').text
    else:
      title=title.find('h2').text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=soup.find('p',{'itemprop':'articleBody'})
      if content is None:
        content = ''
      else:
        content=content.text
    else:
      content=content.text
    return title, content # title, content 완료

  def hk_tv(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'title-news'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'class':'box-news-body'})
    if content is None:
      content = soup.find('p', {'class':'title-news'})
      if content is None:
        content = ''
      else:
        content = content.text
    else:
      content=content.text
    return title, content # title, content 완료

  def mt_broadcast(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('header',{'class':'css-10o447f'})
    if title is None:
      title=''
    else:
      title=title.find('h1').text

    content=soup.find('div',{'class':'css-16jbccu'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def thestock(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'article-head-title'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'itemprop':'articleBody'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def asia_times(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'article_title_area'})
    if title is None:
      title=''
    else:
      title=title.find('h6').text

    content=soup.find('div',{'class':'row article_txt_container'})
    content=content.find('div',{'class':'col-12'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def news_way(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'headline'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'class':'view-area'})
    content=content.find('div',{'class':'view-text'})
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료

  def news_today(self, link):
      response = requests.get(link)
      response.encoding = 'utf-8'
      soup = BeautifulSoup(response.text, 'html.parser')

      # 기사 제목 추출
      title_tag = soup.find('div', class_='h-group cf')
      if title_tag is None:
          title = '제목을 찾을 수 없습니다.'
      else:
          span_tag = title_tag.find('h2')
          if span_tag:
              title = span_tag.text.strip()
          else:
              title = '제목을 찾을 수 없습니다.'


      # 본문 추출
      content = soup.find('div', {'class' : 'view_con cf'})

      if content is None:
          content = ""
      else:
          paragraphs = content.find_all('p')
          content_list = [p.text.strip() for p in paragraphs if p.text.strip()]
          content = " ".join(content_list)

      return title, content

  def yh_news(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'tit'})
    if title is None:
      title=''
    else:
      title=title

    content=soup.find('article',{'class':'story-news article'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def herald_economy(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('li',{'class':'article_title ellipsis2'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'class':'article_view'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def n_daily(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('div',{'class':'article-header'})
    if title is None:
      title=''
    else:
      title=title.find('h1').text

    content=soup.find('li',{'class':'par'})
    if content is None:
      content=''
    else:
      content=content.find_all('div')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def yh_info_mx(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h3',{'class':'heading'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('article',{'id':'article-view-content-div'})
    if content is None:
      content=''
    else:
      content=content.find_all('p')
      content_list=[]
      for i in range(len(content)):
        content_list.append(content[i].text)
      content=" ".join(content_list) #본문
    return title, content # title, content 완료

  def newsis(self, link):
    response = requests.get(link)
    response.encoding = 'utf-8'  # 지정된 인코딩으로 설정
    soup=BeautifulSoup(response.text,'html.parser')

    title=soup.find('h1',{'class':'tit title_area'})
    if title is None:
      title=''
    else:
      title=title.text

    content=soup.find('div',{'class':'viewer'})
    content=soup.find('article')
    if content is None:
      content=''
    else:
      content=content.text
    return title, content # title, content 완료
