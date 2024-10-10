import langchain
from chatbot.NaverApiWrapper import NaverAPIWrapper
from chatbot.retriever import NaverSearchRetriever
from chatbot.FlareChain import FlareChain
from langchain_openai import ChatOpenAI


class Chat:
    naver_api_wrapper = NaverAPIWrapper(
        client_id='bwTPNiweAOyeEjscBCaw',
        client_secret='fdSAFBfv6Q',
        trash_links=["tistory", "kin", "youtube", "book", "news", "dcinside",
                    "fmkorea", "ruliweb", "theqoo", "clien", "mlbpark", "instiz", "todayhumor"]
    )
    retriever = NaverSearchRetriever(search=naver_api_wrapper)


    langchain.verbose = True
    # FROM_LLM에서 FLARE_CHAIN의 question_generator_chain과 response_chain 및 기타 인자들 정의  
    flare = FlareChain.from_llm(
        llm = ChatOpenAI(model = "gpt-3.5-turbo", temperature=0),
        retriever=retriever,
        max_generation_len=512,
        min_token_gap = 4, # 구간 사이의 최소 토큰 수
        num_pad_tokens = 5, # 추가할 토큰 수 증가시키기
        min_prob=0.3,
    )