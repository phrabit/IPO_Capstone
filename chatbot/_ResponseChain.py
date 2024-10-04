from abc import abstractmethod
from chatbot.LLMChain import LLMChain_3
from typing import Any, Dict, List, Optional, Sequence, Tuple
from langchain_core.prompts import BasePromptTemplate
from langchain_core.outputs import Generation
from langchain_core.callbacks import (
    CallbackManagerForChainRun,
)
from langchain.chains.flare.prompts import (
    PROMPT
)


class _ResponseChain(LLMChain_3):
    """응답을 생성하는 체인의 기본 클래스"""

    prompt: BasePromptTemplate = PROMPT

    @classmethod
    def is_lc_serializable(cls) -> bool:
        print("*@*@*@*@*@ IS_LC_SERIALIZABLE in _ResponseChain CLASS *@*@*@*@*@")
        return False

    @property
    def input_keys(self) -> List[str]:
        print("*@*@*@*@*@ INPUT_KEYS in _ResponseChain CLASS *@*@*@*@*@")
        return self.prompt.input_variables

    def generate_tokens_and_log_probs(
        self,
        _input: Dict[str, Any],
        *,
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Tuple[Sequence[str], Sequence[float]]:
        print("*@*@*@*@*@ GENERATE_TOKENS_AND_LOG_PROBS in _ResponseChain CLASS *@*@*@*@*@")
        llm_result = self.generate([_input], run_manager=run_manager)
        print(f"*@*@*@*@*@ llm_result in _ResponseChain CLASS: {llm_result}")
        tokens, log_probs = self._extract_tokens_and_log_probs(llm_result.generations[0])

        return tokens, log_probs

    @abstractmethod
    def _extract_tokens_and_log_probs(
        self, generations: List[Generation]
    ) -> Tuple[Sequence[str], Sequence[float]]:
        print("*@*@*@*@*@ _EXTRACT_TOKENS_AND_LOG_PROBS in _ResponseChain CLASS *@*@*@*@*@")
        """응답에서 토큰과 로그 확률을 추출"""
