from langchain_core.prompts import PromptTemplate

# 프롬프트에 들어갈 내용
PROMPT_TEMPLATE = """\
사용자 메시지에 응답하세요. 제공된 문맥이 있다면, 해당 문맥을 기반으로 답변을 작성하세요. \
답변은 한국어로 명확하게 작성해야 합니다. \
주식 및 공모주에 대한 답변을 구체적으로 해야 합니다. \
추가적인 정보가 필요할 경우, 사용자에게 질문을 통해 더 많은 정보를 요청하세요. \
답변을 마친 후 "FINISHED"를 포함시키세요.

>>> 문맥: {context}
>>> 사용자 입력: {user_input}
>>> 응답: {response}\
"""

# Langchain_core의 PromptTemplate 모듈에 위의 템플릿과 input_variables를 파라미터로 전달
# input_variables: 최종 프롬프트 템플릿에 들어갈 변수명 리스트
PROMPT = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["user_input", "context", "response"],
)

# 질문을 생성할 때 프롬프트로 들어갈 내용
# QUESTION_GENERATOR_PROMPT_TEMPLATE = """\
# 사용자 입력과 기존의 부분적인 응답을 문맥으로 삼아, 다음 용어/개체/구절에 대한 질문을 작성하세요: \
# 질문은 명확하고 구체적이어야 합니다.

# >>> 사용자 입력: {user_input}
# >>> 기존 부분 응답: {current_response}

# "[질문 생성] "{uncertain_span}"에 대한 질문은?? \n\n:"""

QUESTION_GENERATOR_PROMPT_TEMPLATE = """ "{user_input}"에 대한 정확한 답변을 위한 가장 유사한 단 하나의 질문만 해줘."""

# Langchain_core의 PromptTemplate 모듈에 위의 템플릿과 input_variables를 파라미터로 전달
# input_variables: 최종 프롬프트 템플릿에 들어갈 변수명 리스트
QUESTION_GENERATOR_PROMPT = PromptTemplate(
    template=QUESTION_GENERATOR_PROMPT_TEMPLATE,
    input_variables=["user_input", "current_response", "uncertain_span"],
)
