from summary.news_crawler import NewsCrawler
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from requests.exceptions import TooManyRedirects

crawler = NewsCrawler()

def extract_title_content(row):
  # if row['article']=='머니투데이':
  #   title, content = crawler.mt(row)
  if row['article'] == '매일경제':
    title, content = crawler.mk(row['link'])
  elif row['article']=='서울경제신문' or row['article'] == '서울경제':
    try:
      title, content= crawler.sedaily(row['link'])
    except AttributeError:
      print(f"AttributeError occured in 서울경제신문 or 서울경제.")
  elif row['article']=='더벨(thebell)' or row['article'] == '더벨':
    row['link'] = row['link'] + '&svccode=00&page=1&sort=thebell_check_time'
    row['link'] = row['link'].replace('/front/free/contents/news/article_view.asp', '/free/content/ArticleView.asp')
    title, content = crawler.thebell(row['link'])
  elif row['article']=='한국경제':
    try:
      title, content= crawler.hankyung(row['link'])
    except NoSuchElementException:
      print(f"NoSuchElementException occured in 한국경제.")
    except WebDriverException:
      print(f"WebDriverException occured in 한국경제.")
  elif row['article']=='이투데이':
    title, content = crawler.etoday(row['link'])
  elif row['article']=='머니s' or row['article'] == '머니S':
    title, content = crawler.moneys(row['link'])
  elif row['article']=='아시아경제':
    title, content = crawler.asiae(row['link'])
  elif row['article']=='서울파이낸스':
    title, content = crawler.seoulfn(row['link'])
  elif row['article']=='딜사이트':
    try:
      title, content= crawler.dealsite(row['link'])
    except Exception as e:
      print(f"Error occurred at index with link {row['link']}: {e}")
  elif row['article']=='비즈워치' or row['article']=='비즈워치언론사 선정':
    title, content = crawler.bizwatch(row['link'])
  elif row['article']=='이코노미스트':
    title, content = crawler.economist(row['link'])
  elif row['article']=='라이센스뉴스':
    title, content = crawler.license_news(row['link'])
  elif row['article']=='시사저널e':
    title, content = crawler.sisa(row['link'])
  elif row['article']=='충청신문':
    title, content = crawler.chungcheong(row['link'])
  elif row['article']=='조선비즈' or row['article'] == '조선비즈언론사 선정':
    try:
      title, content= crawler.chosun(row['link'])
    except NoSuchElementException:
      print(f'NoSuchElementException occurred in 조선비즈.')
  elif row['article']=='전국매일신문':
    title, content = crawler.jkmail(row['link'])
  elif row['article']=='Investing.com':
    title, content = crawler.inv(row['link'])
  elif row['article']=='영남일보':
    if row['link'].startswith('//'):
        row['link'] = 'https:' + row['link']  # Add https: at the beginning
    title, content = crawler.yn(row['link'])
  elif row['article']=='CBC뉴스':
    title, content = crawler.cbc(row['link'])
  elif row['article']=='블로터':
    title, content = crawler.blt(row['link'])
  elif row['article']=='더팩트':
    title, content = crawler.thefact(row['link'])
  elif row['article']=='아시아에이':
    title, content = crawler.asiaa(row['link'])
  elif row['article']=='문화뉴스':
    title, content = crawler.culture(row['link'])
  elif row['article']=='뉴스핌':
    title, content = crawler.pim(row['link'])
  ###### 네이버 추가 ######
  elif row['article']=='이데일리':
    title, content = crawler.e_daily(row['link'])
  elif row['article']=='비즈니스포스트':
    try:
      title, content= crawler.biz_post(row['link'])
    except TooManyRedirects:
      print(f"Too many redirects for URL: {row['link']}")
  elif row['article']=='시사저널이코노미':
    title, content = crawler.sisa_e(row['link'])
  elif row['article']=='파이낸셜뉴스':
    title, content = crawler.fn_news(row['link'])
  elif row['article']=='국제뉴스':
    title, content = crawler.international_news(row['link'])
  elif row['article']=='데일리안':
    title, content = crawler.daily_ahn(row['link'])
  elif row['article']=='MTN':
    title, content = crawler.mtn(row['link'])
  elif row['article']=='아주경제':
    title, content = crawler.aju_e(row['link'])
  elif row['article']=='뉴스토마토':
    title, content = crawler.news_tomato(row['link'])
  elif row['article']=='뉴스1':
    title, content = crawler.news1(row['link'])
  elif row['article']=='한국경제TV':
    title, content = crawler.hk_tv(row['link'])
    if content != '해당기사가 삭제되었거나 보유기간이 종료되었습니다. ':
        title, content = crawler.hk_tv(row['link'])
  elif row['article']=='머니투데이방송':
    title, content = crawler.mt_broadcast(row['link'])
  elif row['article']=='더스탁':
    title, content = crawler.thestock(row['link'])
  elif row['article']=='아시아타임즈':
    title, content = crawler.asia_times(row['link'])
  elif row['article']=='뉴스웨이':
    title, content = crawler.news_way(row['link'])
  elif row['article']=='뉴스투데이':
    title, content = crawler.news_today(row['link'])
  elif row['article']=='연합뉴스':
    title, content = crawler.yh_news(row['link'])
  elif row['article']=='헤럴드경제':
    title, content = crawler.herald_economy(row['link'])
  elif row['article']=='뉴데일리':
    title, content = crawler.n_daily(row['link'])
  elif row['article']=='연합인포맥스':
    title, content = crawler.yh_info_mx(row['link'])
  elif row['article']=='뉴시스':
    title, content = crawler.newsis(row['link'])
  else:
    title, content = row['title'], ''
  return title, content