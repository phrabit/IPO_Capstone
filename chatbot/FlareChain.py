import re
import numpy as np
from typing import Any, Dict, List, Optional, Sequence, Tuple
from langchain_core.retrievers import BaseRetriever
from pydantic import Field
from langchain.chains.flare.base import FlareChain, QuestionGeneratorChain
from langchain_core.callbacks import (
    CallbackManagerForChainRun
)
from langchain_core.language_models import (
    BaseLanguageModel
)
from langchain.chains.base import Chain

from chatbot._OpenAIResponseChain import _OpenAIResponseChain
from chatbot._ResponseChain import _ResponseChain
from chatbot.FinishedOutputParser import FinishedOutputParser





# 낮은 신뢰도를 가진 토큰의 스팬(구간)을 찾는 함수
def _low_confidence_spans(
    tokens: Sequence[str],
    log_probs: Sequence[float],
    min_prob: float,
    min_token_gap: int,
    num_pad_tokens: int,
) -> List[str]:
    print("*@*@*@*@*@ _LOW_CONFIDENCE_SPANS in SOLO *@*@*@*@*@")

    # 주어진 확률 임계값(threshold)보다 낮은 확률을 가진 토큰의 인덱스를 찾음
    _low_idx = np.where(np.exp(log_probs) < min_prob)[0]
    # 공백이 아닌 토큰만 필터링
    low_idx = [i for i in _low_idx if tokens[i].strip()]

    # 낮은 신뢰도를 가진 토큰이 없으면 빈 리스트 반환
    if len(low_idx) == 0:
        return []
    # low_idx[0]: 낮은 신뢰도를 가지는 첫 번째 토큰의 인덱스
    # span의 시작: low_idx[0]
    # span의 끝: low_idx[0] + num_pad_tokens + 1 (num_pad_tokens: 패딩으로 추가할 토큰의 수) (+1: 마지막 인덱스를 포함하려면 python의 슬라이싱 문법 상 +1을 해줘야 함)
    # 즉, spans는 span의 시작과 끝이 위와 같이 [시작점, 종료점]을 나타내는 리스트를 포함하는 리스트
    # 첫 번째 낮은 신뢰도 토큰을 중심으로 한 스팬(구간)을 설정하는 역할
    spans = [[low_idx[0], low_idx[0] + num_pad_tokens + 1]]
    # 나머지 낮은 신뢰도 토큰에 대해 반복
    for i, idx in enumerate(low_idx[1:]):
        # 이전 토큰과의 거리가 min_token_gap보다 작으면 이전 스팬을 확장
        end = idx + num_pad_tokens + 1
        if idx - low_idx[i] < min_token_gap:
            spans[-1][1] = end
        # 그렇지 않으면 새로운 스팬 시작
        else:
            spans.append([idx, end])
    # 각 스팬에 해당하는 토큰들을 문자열로 결합하여 반환
    return ["".join(tokens[start:end]) for start, end in spans]


# FlareChain
class FlareChain(Chain):
    """검색기, 질문 생성기, 응답 생성기를 결합한 체인"""

    question_generator_chain: QuestionGeneratorChain # FROM_LLM에서 정의
    """불확실한 구간에서 질문을 생성하는 체인"""
    response_chain: _ResponseChain # FROM_LLM에서 정의
    """사용자 입력과 문맥에서 응답을 생성하는 체인""" 
    output_parser: FinishedOutputParser = Field(default_factory=FinishedOutputParser)
    """체인이 완료되었는지 여부를 판단하는 파서"""
    retriever: BaseRetriever
    """사용자 입력에서 관련 문서를 검색하는 검색기"""
    min_prob: float = 0.2
    """토큰이 낮은 확률로 간주되기 위한 최소 확률"""
    min_token_gap: int = 5
    """두 낮은 확률 구간 사이의 최소 토큰 수"""
    num_pad_tokens: int = 2
    """낮은 확률 구간 주위에 추가할 토큰 수"""
    max_iter: int = 10
    """최대 반복 횟수입니다."""
    start_with_retrieval: bool = True
    """검색부터 시작할지 여부"""

    @property
    def input_keys(self) -> List[str]:
        print("*@*@*@*@*@ INPUT_KEYS in FlareChain CLASS *@*@*@*@*@")
        # """체인의 입력 키들"""
        return ["user_input"]

    @property
    def output_keys(self) -> List[str]:
        print("*@*@*@*@*@ OUTPUT_KEYS in FlareChain CLASS *@*@*@*@*@")
        # """체인의 출력 키들"""
        return ["response"]

    # _do_generation 함수 수정
    def _do_generation(
        self,
        questions: List[str],
        user_input: str,
        response: str,
        _run_manager: CallbackManagerForChainRun,
    ) -> Tuple[str, bool]:
        print("*@*@*@*@*@ _DO_GENERATION in FlareChain CLASS *@*@*@*@*@")
        callbacks = _run_manager.get_child()
        docs = []
        
        # 각 질문에 대해 관련 문서를 검색
        for question in questions:
            retrieved_docs = self.retriever.invoke(question)
            # 검색된 문서가 없을 경우 처리
            if retrieved_docs:
                docs.extend(retrieved_docs)
        
        # 검색된 문서들의 내용을 하나의 문자열로 결합
        context = "\n\n".join(d.page_content for d in docs) if docs else ""
        
        # response_chain을 사용하여 결과 예측
        result = self.response_chain.predict(
            user_input=user_input,
            context=context,
            response=response,
            callbacks=callbacks,
        )
        
        # 결과를 파싱하여 주변 텍스트와 완료 여부 반환
        marginal, finished = self.output_parser.parse(result)
        
        # 위의 marginal과 finished를 함수의 결과로 return
        return marginal, finished

    # 낮은 신뢰도 구간에 대해 추가 검색하는 함수
    # _do_retrieval에서 생성된 질문을 기반으로 _do_generation 함수 호출함 -> 이 과정에서 response값 업데이트 안됨.
    def _do_retrieval(
        self,
        low_confidence_spans: List[str],
        _run_manager: CallbackManagerForChainRun,
        user_input: str,
        response: str,
        initial_response: str,
    ) -> Tuple[str, bool]:
        print("*@*@*@*@*@ _DO_RETRIEVAL in FlareChain CLASS *@*@*@*@*@")
        # bytes를 포함하는 문장을 제거
        # sentences = initial_response.split('. ')
        # cleaned_sentences = [sentence for sentence in sentences if 'bytes' not in sentence]
        # cleaned_text = ''.join(cleaned_sentences)

        # initial_response = cleaned_text

        # 바이트 관련 문자열 제거
        initial_response = re.sub(r'bytes:[^ ]+', '', initial_response)
        
        # 각 낮은 신뢰도 구간에 대해 질문 생성 입력 준비
        question_gen_inputs = [
            {
                "user_input": user_input,
                "current_response": initial_response,
                "uncertain_span": span,
            }
            for span in low_confidence_spans
        ]
        callbacks = _run_manager.get_child()
        
        question_gen_outputs = self.question_generator_chain.apply(
            question_gen_inputs, callbacks=callbacks
        )
        questions = [
            output[self.question_generator_chain.output_keys[0]]
            for output in question_gen_outputs
        ]
        
        # 생성된 질문들을 로그에 기록
        _run_manager.on_text(
            f"Generated Questions: {questions}", color="yellow", end="\n"
        )
        print(f"*@*@*@*@*@ questions of _DO_RETRIEVAL in FlareChain CLASS *@*@*@*@*@\n*@*@*@*@*@ {questions} *@*@*@*@*@")
        
        # 생성된 질문들을 사용하여 응답 생성
        marginal, finished = self._do_generation(questions, user_input, response, _run_manager)
        
        # 기존 response에 새로 생성된 marginal을 추가
        updated_response = response.strip() + " " + marginal
        return updated_response, finished

    # FlareChain의 주요 실행 함수
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, Any]:
        print("*@*@*@*@*@ _CALL in FlareChain CLASS *@*@*@*@*@")
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()

        user_input = inputs[self.input_keys[0]]

        response = ""

        for i in range(self.max_iter):
            # 현재 응답 상태를 로그에 기록
            _run_manager.on_text(
                f"Current Response: {response}", color="blue", end="\n"
            )
            _input = {"user_input": user_input, "context": "", "response": response}
            # 토큰과 로그 확률 생성
            tokens, log_probs = self.response_chain.generate_tokens_and_log_probs(
                _input, run_manager=_run_manager
            )

            # 낮은 신뢰도 구간 식별
            low_confidence_spans = _low_confidence_spans(
                tokens,
                log_probs,
                self.min_prob,
                self.min_token_gap,
                self.num_pad_tokens,
            )
            initial_response = response.strip() + " " + "".join(tokens)
            if not low_confidence_spans:
                response = initial_response
                final_response, finished = self.output_parser.parse(response)
                if finished:
                    # bytes를 포함하는 문장을 제거
                    sentences = final_response.split('. ')
                    cleaned_sentences = [sentence for sentence in sentences if 'bytes' not in sentence]
                    cleaned_text = '. '.join(cleaned_sentences)

                    # 마지막 문장의 끝에 마침표 추가 (원본 텍스트의 형식을 유지하기 위해)
                    cleaned_text += '.'
                    final_response = cleaned_text
                    return {self.output_keys[0]: final_response}
                continue
            
            # 낮은 신뢰도 구간에 대해 추가 검색 수행
            marginal, finished = self._do_retrieval(
                low_confidence_spans,
                _run_manager,
                user_input,
                response,
                initial_response,
            )
            response = response.strip() + " " + marginal
            # bytes를 포함하는 문장을 제거
            sentences = response.split('. ')
            cleaned_sentences = [sentence for sentence in sentences if 'bytes' not in sentence]
            cleaned_text = '. '.join(cleaned_sentences)

            # 마지막 문장의 끝에 마침표 추가 (원본 텍스트의 형식을 유지하기 위해)
            cleaned_text += '.'
            response = cleaned_text
            if finished:
                break
        return {self.output_keys[0]: response}

    @classmethod
    def from_llm(
        cls, llm : BaseLanguageModel, max_generation_len: int = 128, **kwargs: Any
    ) -> FlareChain:
        
        try:
            from langchain_openai import OpenAI
        except ImportError:
            raise ImportError(
                "FlareChain을 사용하려면 OpenAI가 필요합니다. "
                "langchain-openai를 설치하세요."
                "pip install langchain-openai"
            )
        # 질문 생성 체인 초기화
        question_gen_chain = QuestionGeneratorChain(llm=llm)
        
        response_llm = OpenAI(
           max_tokens=max_generation_len, logprobs=1, temperature=0
        )

        # 응답 체인 초기화
        response_chain = _OpenAIResponseChain(llm=response_llm)
        # FlareChain 인스턴스 생성 및 반환
        # cls: class의 약자 / 여기서는 FlareChain을 가리킴
        return cls(
            question_generator_chain=question_gen_chain,
            response_chain=response_chain,
            **kwargs,
        )

