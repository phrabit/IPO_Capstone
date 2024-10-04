from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.callbacks.manager import CallbackManager

# LangChain이 지원하는 Ollama 모델을 사용합니다.
def get_summary_chain():
    summary_llm = ChatOllama(
        model="llama3.1-instruct-8b:latest",
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )

    # 프롬프트 템플릿을 정의하여, core_word를 중심으로 요약을 생성하도록 설정합니다.
    summary_prompt = ChatPromptTemplate.from_template(
        """다음 뉴스 기사를 3개의 문장으로 요약해줘. 각 문장은 '1.', '2.', '3.'으로 시작하며, 한 줄에 하나의 문장만 작성해야 해. 
        또한 각 문장은 마침표('.')로 끝나야 하고, 문장은 반드시 한 문장으로 간결하게 작성해줘. 
        '{core_word}'와 관련된 핵심 내용만 포함해줘.\n\n기사 본문: {article_content}"""
    )

    # 템플릿에 original_text를 포함한 질문을 전달합니다.
    chain = summary_prompt | summary_llm | StrOutputParser()
    return chain