from chatbot._ResponseChain import _ResponseChain
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast
from langchain_core.outputs import Generation
from langchain_core.language_models import (
    BaseLanguageModel
)

class _OpenAIResponseChain(_ResponseChain):
    """사용자 입력과 문맥에서 응답을 생성하는 체인입니다."""

    llm: BaseLanguageModel
    # 토큰과 로그 확률을 추출하는 함수
    def _extract_tokens_and_log_probs(
        self, generations: List[Generation]
    ) -> Tuple[Sequence[str], Sequence[float]]:
        print("*@*@*@*@*@ _EXTRACT_TOKENS_AND_LOG_PROBS in _OpenAIResponseChain CLASS *@*@*@*@*@")
        # token, log_probs 리스트 초기화
        tokens = []
        log_probs = []
        # generations 리스트의 각 원소에 대해 반복
        for gen in generations:
            # generations(생성된 텍스트)가 없으면 오류 발생
            if gen.generation_info is None:
                raise ValueError
            # 토큰 추출 및 리스트에 추가
            tokens.extend(gen.generation_info["logprobs"]["tokens"])
            # 로그 확률 추출 및 리스트에 추가
            log_probs.extend(gen.generation_info["logprobs"]["token_logprobs"])
        # 추출된 토큰과 로그 확률 반환
        return tokens, log_probs
