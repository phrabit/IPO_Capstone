import streamlit as st
import time
from summary.news_extractor import extract_title_content
from summary.naver_crawler import NaverCrawler
from model.Summary.summary_model import get_summary_chain

def run_summary():
    st.subheader("검색한 공모주에 대한 Top3 뉴스들 요약")

    # Text input -> 공모주 이름
    input_text = st.text_input("공모주 이름만 입력해주세요.")

    crawler = NaverCrawler()
    summary_chain = get_summary_chain()

    if st.button("Search"):
        if input_text:
            with st.spinner("Search for Top3 News..."):
                start_time = time.time()
                progress_bar = st.progress(0)
                status_text = st.empty()
                time_text = st.empty()

                # 크롤링 시작
                crawling_start = time.time()
                status_text.text("크롤링 중...")
                newses = crawler.crawling(input_text)
                crawling_end = time.time()
                crawling_time = crawling_end - crawling_start
                status_text.text("크롤링 완료!")

                newses['content'] = ''
                total_steps = len(newses) + 3
                current_step = 1

                # 전처리 시작
                preprocessing_start = time.time()
                status_text.text("뉴스 본문 추출 중...")
                for index, row in newses.iterrows():
                    title, content = extract_title_content(row)
                    if not content or content.strip() == '':
                        continue 
                    newses.at[index, 'content'] = content
                    progress = current_step / total_steps
                    progress_bar.progress(progress)
                    current_step += 1

                newses = newses[newses['content'] != ''].reset_index(drop=True)
                if len(newses) > 0:
                    preprocessing_end = time.time()
                    status_text.text("뉴스 본문 추출 완료!")
                    top3_newses = newses.iloc[:3].copy()
                    top3_newses['summary'] = ''

                    summarization_start = time.time()
                    status_text.text("요약 중...")
                    for i in range(len(top3_newses)):
                        original_text = top3_newses['content'][i]
                        core_word = input_text
                        question = {"core_word": core_word, "article_content": original_text}
                        summary = summary_chain.invoke(question)
                        top3_newses.loc[i, 'summary'] = summary

                        progress = current_step / total_steps
                        progress_bar.progress(progress)
                        current_step += 1

                    summarization_end = time.time()
                    status_text.text("요약 완료!")
                    
                    st.subheader("Summary:")
                    for j in range(len(top3_newses)):
                        st.markdown(f"**제목:** {top3_newses['title'][j]}")
                        st.markdown(f"**요약:**")
                        summary_sentences = top3_newses['summary'][j].split("\n")
                        for sentence in summary_sentences:
                            if sentence.strip():
                                st.write(sentence.strip())
                        st.markdown(f"**링크:** {top3_newses['link'][j]}")
                        st.markdown("---")
                else:
                    st.warning("No valid news articles found after filtering.")
