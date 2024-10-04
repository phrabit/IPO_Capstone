import os
from chatbot.naver_api_wrapper import NaverAPIWrapper
from pydantic import Field
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.openai import OpenAIEmbeddings
from urllib.error import HTTPError
from langchain_core.retrievers import BaseRetriever
from langchain.schema import BaseRetriever
from dotenv import load_dotenv

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

class NaverSearchRetriever(BaseRetriever):
    search: NaverAPIWrapper = Field(...)

    def get_relevant_documents(self, query: str):
        print("*@*@*@*@*@ GET_RELEVANT_DOCUMENTS in NaverSearchRetriever CLASS *@*@*@*@*@")
        try:
            print(f"***************** 관련 문서 찾기 ****************")
            # search: NaverAPIWrapper
            # NaverAPIWrapper의 run 함수에 query 파라미터로 전달
            # => df['Summary']의 값들을 list로 return
            # 즉, texts는 요약된 text들의 list
            texts = self.search.run(query)
            # Text Splitter 생성
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=250,
                chunk_overlap=50,
                length_function=len,
                add_start_index=True,
            )
            # Text Splitter 적용
            texts = text_splitter.create_documents([texts])
            embeddings_model = OpenAIEmbeddings(openai_api_key=OPENAI_KEY) # text-embedding-ada-002
            from langchain_community.vectorstores import Qdrant
            # Vector DB 생성
            db = Qdrant.from_documents(
                texts,
                embeddings_model,
                location=":memory:",  # Local mode with in-memory storage only
                collection_name="my_documents",
            )
            # 유사한 문서 5개 추출하도록 retrieve 설정
            retrieve = db.as_retriever(
                                        search_type="similarity",
                                        search_kwargs={'k': 5}
                                    )
            # 네이버 Search API에 입력한 동일한 query 입력
            # 위에 설정된 retrieve로 query에 대해서 유사한 document 5개 return 
            docs = retrieve.get_relevant_documents(query)
            # 5개의 문서 return
            return docs
        except HTTPError as e:
            print(f"Error occurred while fetching documents: {e}")
            return []
        except TypeError as e:
            print(f"Error occurred while processing texts: {e}")
            return []
        except KeyError as e:
            print(f"Key error occurred: {e}")
            return []

    async def aget_relevant_documents(self, query: str):
        print("*@*@*@*@*@ AGET_RELEVANT_DOCUMENTS in NaverSearchRetriever CLASS *@*@*@*@*@")
        raise NotImplementedError
