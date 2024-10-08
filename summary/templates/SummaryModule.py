import streamlit as st
import time
from summary.news_extractor import extract_title_content
from summary.naver_crawler import NaverCrawler
from model.Summary.summary_model import get_summary_chain

# def run_summary():
#     st.subheader("📰 검색한 공모주에 대한 Top3 뉴스들 요약")

#     # Text input -> 공모주 이름
#     input_text = st.text_input("공모주 이름만 입력해주세요.")

#     crawler = NaverCrawler()
#     summary_chain = get_summary_chain()

#     if st.button("Search"):
#         if input_text:
#             with st.spinner("Search for Top3 News..."):
#                 start_time = time.time()
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
#                 time_text = st.empty()

#                 # 크롤링 시작
#                 crawling_start = time.time()
#                 status_text.text("크롤링 중...")
#                 newses = crawler.crawling(input_text)
#                 crawling_end = time.time()
#                 crawling_time = crawling_end - crawling_start
#                 status_text.text("크롤링 완료!")

#                 newses['content'] = ''
#                 total_steps = len(newses) + 3
#                 current_step = 1

#                 # 전처리 시작
#                 preprocessing_start = time.time()
#                 status_text.text("뉴스 본문 추출 중...")
#                 for index, row in newses.iterrows():
#                     title, content = extract_title_content(row)
#                     if not content or content.strip() == '':
#                         continue 
#                     newses.at[index, 'content'] = content
#                     progress = current_step / total_steps
#                     progress_bar.progress(progress)
#                     current_step += 1

#                 newses = newses[newses['content'] != ''].reset_index(drop=True)
#                 if len(newses) > 0:
#                     preprocessing_end = time.time()
#                     status_text.text("뉴스 본문 추출 완료!")
#                     top3_newses = newses.iloc[:3].copy()
#                     top3_newses['summary'] = ''

#                     summarization_start = time.time()
#                     status_text.text("요약 중...")
#                     for i in range(len(top3_newses)):
#                         original_text = top3_newses['content'][i]
#                         core_word = input_text
#                         question = {"core_word": core_word, "article_content": original_text}
#                         summary = summary_chain.invoke(question)
#                         top3_newses.loc[i, 'summary'] = summary

#                         progress = current_step / total_steps
#                         progress_bar.progress(progress)
#                         current_step += 1

#                     summarization_end = time.time()
#                     status_text.text("요약 완료!")
                    
#                     st.subheader("Summary:")
#                     for j in range(len(top3_newses)):
#                         st.markdown(f"**제목:** {top3_newses['title'][j]}")
#                         st.markdown(f"**요약:**")
#                         summary_sentences = top3_newses['summary'][j].split("\n")
#                         for sentence in summary_sentences:
#                             if sentence.strip():
#                                 st.write(sentence.strip())
#                         st.markdown(f"**링크:** {top3_newses['link'][j]}")
#                         st.markdown("---")
#                 else:
#                     st.warning("No valid news articles found after filtering.")

# def run_summary():
#     st.subheader("📰 검색한 공모주에 대한 Top3 뉴스들 요약")

#     # Text input -> 공모주 이름
#     input_text = st.text_input("공모주 이름을 입력해주세요")

#     # 크롤러 및 체인 초기화
#     crawler = NaverCrawler()
#     summary_chain = get_summary_chain()

#     # 검색 버튼
#     if st.button("🔍 Search"):
#         if input_text:
#             with st.spinner("🔍 Top3 뉴스 검색 중..."):
#                 start_time = time.time()
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
#                 time_text = st.empty()

#                 # 크롤링 시작
#                 status_text.text("🕵️‍♂️ 뉴스 크롤링 중...")
#                 newses = crawler.crawling(input_text)
#                 newses['content'] = ''
#                 total_steps = len(newses) + 3
#                 current_step = 1

#                 # 뉴스 본문 추출 및 전처리
#                 status_text.text("🔍 뉴스 본문 추출 중...")
#                 for index, row in newses.iterrows():
#                     title, content = extract_title_content(row)
#                     if not content or content.strip() == '':
#                         continue 
#                     newses.at[index, 'content'] = content
#                     progress = current_step / total_steps
#                     progress_bar.progress(progress)
#                     current_step += 1

#                 # 뉴스 본문이 있는 뉴스만 필터링
#                 newses = newses[newses['content'] != ''].reset_index(drop=True)
#                 if len(newses) > 0:
#                     status_text.text("📝 요약 중...")

#                     # Top 3 뉴스 추출 및 요약
#                     top3_newses = newses.iloc[:3].copy()
#                     top3_newses['summary'] = ''

#                     for i in range(len(top3_newses)):
#                         original_text = top3_newses['content'][i]
#                         core_word = input_text
#                         question = {"core_word": core_word, "article_content": original_text}
#                         summary = summary_chain.invoke(question)
#                         top3_newses.loc[i, 'summary'] = summary

#                         progress = current_step / total_steps
#                         progress_bar.progress(progress)
#                         current_step += 1

#                     status_text.text("✅ 요약 완료!")
                    
#                     # 요약 결과 표시
#                     st.subheader("요약 결과")
#                     for j in range(len(top3_newses)):
#                         # 뉴스 카드 형식으로 출력
#                         st.markdown(f"""
#                         <div style="background-color:#f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
#                             <h4>📰 제목: {top3_newses['title'][j]}</h4>
#                             <p><strong>요약:</strong> {top3_newses['summary'][j]}</p>
#                             <p><strong>링크:</strong> <a href="{top3_newses['link'][j]}" target="_blank">{top3_newses['link'][j]}</a></p>
#                         </div>
#                         """, unsafe_allow_html=True)
#                 else:
#                     st.warning("🔍 필터링 후 유효한 뉴스 기사를 찾을 수 없습니다.")


def run_summary():
    st.subheader("📰 Summarize the top 3 news for the public stocks you searched for")

    # Text input -> 공모주 이름
    input_text = st.text_input("Please enter the name of the public offering")

    # 크롤러 및 체인 초기화
    crawler = NaverCrawler()
    summary_chain = get_summary_chain()

    # 검색 버튼
    if st.button("🔍 Search"):
        if input_text:
            with st.spinner("🔍 Searching for Top3 News..."):
                start_time = time.time()
                progress_bar = st.progress(0)  # Progress bar 추가
                status_text = st.empty()

                # 크롤링 시작
                status_text.text("🕵️‍♂️ Crawling news...")
                newses = crawler.crawling(input_text)
                newses['content'] = ''
                total_steps = len(newses) + 3
                current_step = 1

                # 뉴스 본문 추출 및 전처리
                status_text.text("🔍 Extracting news Contents...")
                for index, row in newses.iterrows():
                    title, content = extract_title_content(row)
                    if not content or content.strip() == '':
                        continue 
                    newses.at[index, 'content'] = content
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    current_step += 1

                # 뉴스 본문이 있는 뉴스만 필터링
                newses = newses[newses['content'] != ''].reset_index(drop=True)
                if len(newses) > 0:
                    status_text.text("📝 Summarizing...")

                    # Top 3 뉴스 추출 및 요약
                    top3_newses = newses.iloc[:3].copy()
                    top3_newses['summary'] = ''

                    for i in range(len(top3_newses)):
                        original_text = top3_newses['content'][i]
                        core_word = input_text
                        question = {"core_word": core_word, "article_content": original_text}
                        summary = summary_chain.invoke(question)
                        top3_newses.loc[i, 'summary'] = summary

                        progress = current_step / total_steps
                        progress_bar.progress(progress)
                        current_step += 1

                    # 요약이 완료되면 progress bar 제거
                    progress_bar.empty()
                    status_text.empty()

                    # 요약 결과 표시
                    st.subheader("Summary results")
                    for j in range(len(top3_newses)):
                         # 요약 내용을 줄바꿈 처리
                        formatted_summary = top3_newses['summary'][j].replace('1)', '<br>1)').replace('2)', '<br>2)').replace('3)', '<br>3)')
                        formatted_summary = formatted_summary.replace('. ', '.<br>')  # 마침표 뒤에 줄바꿈 추가
                        st.markdown(f"""
                        <div style="background-color:#f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1);">
                            <h4>📃 {j+1}. {top3_newses['title'][j]}</h4>
                            <p><strong>Summary:</strong> {formatted_summary}</p>
                            <p><strong>Link:</strong> <a href="{top3_newses['link'][j]}" target="_blank">{top3_newses['link'][j]}</a></p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("🔍 No valid news articles were found after filtering.")
