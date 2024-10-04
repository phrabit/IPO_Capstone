from langchain_core.prompts import BasePromptTemplate
from langchain.chains.flare.prompts import (
    QUESTION_GENERATOR_PROMPT
)
from typing import List
from langchain.chains.llm import LLMChain

class QuestionGeneratorChain(LLMChain):
    """불확실한 구간에서 질문을 생성하는 체인"""

    prompt: BasePromptTemplate = QUESTION_GENERATOR_PROMPT
    """체인을 위한 프롬프트 템플릿"""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        print("*@*@*@*@*@ IS_LC_SERIALIZABLE in QuestionGeneratorChain CLASS *@*@*@*@*@")
        return False

    # QuestionGeneratorChain이 사용할 입력 데이터의 키 리스트 return
    # uncertain_span: 불확실한 구간
    @property
    def input_keys(self) -> List[str]:
        print("*@*@*@*@*@ INPUT_KEYS in QuestionGeneratorChain CLASS *@*@*@*@*@")
        print(f"*@*@*@*@*@ uncertain_span in QuestionGeneratorChain CLASS *@*@*@*@*@")
        temp = ["user_input", "current_response", "uncertain_span"]
        print(f"*@*@*@*@*@ {temp} *@*@*@*@*@")
        """체인의 입력 키들"""
        return ["user_input", "current_response", "uncertain_span"]
