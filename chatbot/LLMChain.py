
import warnings
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast
from pydantic import Field

from langchain.chains.base import Chain
from langchain_core.prompts import BasePromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import  StrOutputParser, BaseLLMOutputParser
from langchain_core.runnables import Runnable
from langchain.chains.llm import LLMChain
from langchain.chains.base import Chain
from langchain_core.prompts import BasePromptTemplate
from langchain_core.outputs import Generation
from langchain_community.llms import OpenAI
from langchain_core.callbacks import (
    CallbackManagerForChainRun,
)
from langchain_core.callbacks import (
    AsyncCallbackManager,
    AsyncCallbackManagerForChainRun,
    CallbackManager,
    CallbackManagerForChainRun,
    Callbacks,
)
from langchain_core.language_models import (
    BaseLanguageModel,
    LanguageModelInput,
)
from langchain_core.load.dump import dumpd
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import BaseLLMOutputParser, StrOutputParser
from langchain_core.outputs import ChatGeneration, Generation, LLMResult
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.utils.input import get_colored_text



def get_colored_text(text, color):
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "endc": "\033[0m",
    }
    return f"{colors.get(color, colors['endc'])}{text}{colors['endc']}"

# LLMChain은 Chain의 모든 함수와 속성들을 상속받음
# Chain은 LLMChain에게 기본적인 구조와 인터페이스 제공
class LLMChain_3(Chain): # src: https://github.com/langchain-ai/langchain/blob/master/libs/langchain/langchain/chains/llm.py
    """Chain to run queries against LLMs.

    This class is deprecated. See below for an example implementation using
    LangChain runnables:

        .. code-block:: python

            from langchain_core.prompts import PromptTemplate
            from langchain_openai import OpenAI

            prompt_template = "Tell me a {adjective} joke"
            prompt = PromptTemplate(
                input_variables=["adjective"], template=prompt_template
            )
            llm = OpenAI()
            chain = prompt | llm

            chain.invoke("your adjective here")

    Example:
        .. code-block:: python

            from langchain.chains import LLMChain
            from langchain_community.llms import OpenAI
            from langchain_core.prompts import PromptTemplate
            prompt_template = "Tell me a {adjective} joke"
            prompt = PromptTemplate(
                input_variables=["adjective"], template=prompt_template
            )
            llm = LLMChain(llm=OpenAI(), prompt=prompt)
    """

    # LLMChain 클래스가 LangChain에서 직렬화 가능한지를 나타내는 Boolean 값을 반환
    # 직렬화(Serialization)란?
    # 객체의 상태를 바이트 스트림이나 문자열로 변환하는 과정. 
    # 객체를 저장하거나 네트워크를 통해 전송할 때 유용.
    # => LangChain 프레임워크 내에서 LLMChain 객체가 저장, 전송, 복원될 수 있음
    @classmethod
    def is_lc_serializable(self) -> bool:
        print("*@*@*@*@*@ IS_LC_SERIALIZABLE in LLMChain CLASS *@*@*@*@*@")
        # LLMChain 클래스가 LangChain에서 직렬화 가능한지를 나타내는 Boolean 값을 반환
        return True

    prompt: BasePromptTemplate
    """사용할 프롬프트 객체"""
    llm: Union[
        Runnable[LanguageModelInput, str], Runnable[LanguageModelInput, BaseMessage]
    ]
    """호출할 언어 모델"""
    # 출력 키 설정, 기본값은 "text"
    output_key: str = "text"  #: :meta private:
    # 사용할 출력 파서. StrOutputParser: 가장 가능성 높은 문자열을 반환 => 기본값
    output_parser: BaseLLMOutputParser = Field(default_factory=StrOutputParser)
    # 최종 파싱된 결과만 반환할지 여부 설정, 기본값은 True. False인 경우, 생성에 대한 추가 정보를 반환.
    return_final_only: bool = True
    # LLM에 전달할 추가 인자들을 저장하는 딕셔너리
    llm_kwargs: dict = Field(default_factory=dict)

    class Config:
        print("*@*@*@*@*@ Config CLASS in LLMChain CLASS *@*@*@*@*@")
        """Configuration for this pydantic object."""

        # extra = Extra.forbid
        extra = 'forbid'
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        print("*@*@*@*@*@ INPUT_KEYS in LLMChain CLASS *@*@*@*@*@")
        # 프롬프트에 입력되는 입력 키들을 반환
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        print("*@*@*@*@*@ OUTPUT_KEYS in LLMChain CLASS *@*@*@*@*@")
        # 항상 텍스트 키를 반환
        if self.return_final_only:
            return [self.output_key]
        else:
            return [self.output_key, "full_generation"]

    # 입력을 받아 LLM 응답을 생성하고 출력을 만듦
    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        print("*@*@*@*@*@ _CALL in LLMChain CLASS *@*@*@*@*@")
        response = self.generate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]
    
    # 입력 리스트로부터 LLM 결과를 생성
    def generate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> LLMResult:
        print("*@*@*@*@*@ GENERATE in LLMChain CLASS *@*@*@*@*@")
        # 입력 리스트와 run_manager를 사용하여 프롬프트와 중지 조건을 준비 (prep_prompts의 return값 2개)
        prompts, stop = self.prep_prompts(input_list, run_manager=run_manager)
        print(f"*@*@*@*@*@ prompts of GENERATE in LLMChain CLASS: {prompts}")
        # run_manager가 존재하면 자식 콜백을 가져오고, 없으면 None으로 설정
        callbacks = run_manager.get_child() if run_manager else None
        # self.llm이 BaseLanguageModel의 인스턴스인지 확인: OpenAI의 GPT모델은 BaseLanguageModel에 속함
        if isinstance(self.llm, BaseLanguageModel):
            print("*@*@*@*@*@ isinstance of GENERATE in LLMChain CLASS *@*@*@*@*@")
            # BaseLanguageModel 인스턴스인 경우 generate_prompt 메서드 호출
            result = self.llm.generate_prompt(
                prompts,
                stop,
                callbacks=callbacks,
                **self.llm_kwargs,
            )
            print(f"*@*@*@*@*@ retrun value of GENERATE in LLMChain CLASS: {result}")
            return self.llm.generate_prompt(
                prompts,
                stop,
                callbacks=callbacks,
                **self.llm_kwargs,
            )
        else:
            print("*@*@*@*@*@ else of GENERATE in LLMChain CLASS *@*@*@*@*@")
            # 그 외의 경우 Runnable 인터페이스를 사용하여 배치 처리
            # self.llm.bind -> 주어진 매개변수를 이용해 새로운 Runnable 인스턴스 생성
            results = self.llm.bind(stop=stop, **self.llm_kwargs).batch(
                cast(List, prompts), {"callbacks": callbacks}
            )
            # 결과를 저장할 리스트 초기화
            generations: List[List[Generation]] = []
            # 각 결과에 대해 처리
            for res in results:
                if isinstance(res, BaseMessage):
                    # 결과가 BaseMessage 인스턴스인 경우 ChatGeneration으로 변환
                    generations.append([ChatGeneration(message=res)])
                else:
                    # 그 외의 경우 일반 Generation으로 변환
                    generations.append([Generation(text=res)])
            # 최종 LLMResult 객체 반환
            return LLMResult(generations=generations)
    
    # 이하 메서드들(agenerate, prep_prompts, aprep_prompts 등)은 비동기 처리와 프롬프트 준비 등을 담당
    # 각 메서드의 구체적인 기능은 메서드 이름과 구현에서 유추 가능

    # 입력으로부터 LLM 결과를 비동기적으로 생성
    # 비동기 웹 어플리케이션(Ex. FastAPI)를 사용할 때 agnerate 함수 호출 가능
    async def agenerate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> LLMResult:
        print("*@*@*@*@*@ AGENERATE in LLMChain CLASS *@*@*@*@*@")
        # 입력 리스트와 run_manager를 사용하여 프롬프트와 중지 조건을 비동기적으로 준비
        prompts, stop = await self.aprep_prompts(input_list, run_manager=run_manager)
        
        # run_manager가 존재하면 자식 콜백을 가져오고, 없으면 None으로 설정
        callbacks = run_manager.get_child() if run_manager else None
        
        # self.llm이 BaseLanguageModel의 인스턴스인지 확인
        if isinstance(self.llm, BaseLanguageModel):
            # BaseLanguageModel 인스턴스인 경우 agenerate_prompt 메서드를 비동기적으로 호출
            return await self.llm.agenerate_prompt(
                prompts,
                stop,
                callbacks=callbacks,
                **self.llm_kwargs,
            )
        else:
            # BaseLanguageModel이 아닌 경우 Runnable 인터페이스를 사용하여 비동기 배치 처리
            results = await self.llm.bind(stop=stop, **self.llm_kwargs).abatch(
                cast(List, prompts), {"callbacks": callbacks}
            )
            # 결과를 저장할 리스트 초기화
            generations: List[List[Generation]] = []
            for res in results:
                if isinstance(res, BaseMessage):
                    generations.append([ChatGeneration(message=res)])
                else:
                    generations.append([Generation(text=res)])
            return LLMResult(generations=generations)
    
    # input으로부터 prompt 준비
    def prep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        print("*@*@*@*@*@ PREP_PROMPTS in LLMChain CLASS *@*@*@*@*@")
        
        # 중지 조건 초기화
        stop = None
        
        # 입력 리스트가 비어있으면 빈 리스트와 None을 반환
        if len(input_list) == 0:
            return [], stop
        
        # 첫 번째 입력에 'stop' 키가 있으면 중지 조건으로 설정
        if "stop" in input_list[0]:
            stop = input_list[0]["stop"]
        
        # 프롬프트를 저장할 리스트 초기화
        prompts = []
        
        # 각 입력에 대해 반복
        for inputs in input_list:
            # 프롬프트의 입력 변수에 해당하는 값만 선택
            selected_inputs = {k: inputs[k] for k in self.prompt.input_variables}
            
            # 선택된 입력으로 프롬프트 포맷팅
            prompt = self.prompt.format_prompt(**selected_inputs)
            
            # 포맷팅된 프롬프트를 녹색으로 색칠
            _colored_text = get_colored_text(prompt.to_string(), "green")
            _text = "Prompt after formatting:\n" + _colored_text
            
            # run_manager가 존재하면 텍스트 로깅
            if run_manager:
                run_manager.on_text(_text, end="\n", verbose=self.verbose)
            
            # 현재 입력의 'stop' 값이 이전에 설정한 stop과 다르면 오류 발생
            if "stop" in inputs and inputs["stop"] != stop:
                raise ValueError(
                    "If `stop` is present in any inputs, should be present in all."
                )
            
            # 포맷팅된 프롬프트를 리스트에 추가
            prompts.append(prompt)
        
        # 준비된 프롬프트 리스트와 중지 조건 반환
        return prompts, stop

    async def aprep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        print("*@*@*@*@*@ APREP_PROMPTS in LLMChain CLASS *@*@*@*@*@")
        """Prepare prompts from inputs."""
        stop = None
        if len(input_list) == 0:
            return [], stop
        if "stop" in input_list[0]:
            stop = input_list[0]["stop"]
        prompts = []
        for inputs in input_list:
            selected_inputs = {k: inputs[k] for k in self.prompt.input_variables}
            prompt = self.prompt.format_prompt(**selected_inputs)
            _colored_text = get_colored_text(prompt.to_string(), "green")
            _text = "Prompt after formatting:\n" + _colored_text
            if run_manager:
                await run_manager.on_text(_text, end="\n", verbose=self.verbose)
            if "stop" in inputs and inputs["stop"] != stop:
                raise ValueError(
                    "If `stop` is present in any inputs, should be present in all."
                )
            prompts.append(prompt)
        return prompts, stop

    def apply(
        self, input_list: List[Dict[str, Any]], callbacks: Callbacks = None
    ) -> List[Dict[str, str]]:
        print("*@*@*@*@*@ APPLY in LLMChain CLASS *@*@*@*@*@")
        """Utilize the LLM generate method for speed gains."""
        # 콜백 매니저 구성
        # 주어진 callbacks, 자체 callbacks, verbose 옵션을 사용하여 CallbackManager 설정
        callback_manager = CallbackManager.configure(
            callbacks, self.callbacks, self.verbose
        )
        
        # 체인 시작 이벤트 발생
        # dumpd(self)는 현재 객체의 직렬화된 표현을 제공
        run_manager = callback_manager.on_chain_start(
            dumpd(self),
            {"input_list": input_list},
        )
        
        try:
            # generate 메서드를 호출하여 응답 생성
            response = self.generate(input_list, run_manager=run_manager)
        except BaseException as e:
            # 예외 발생 시 체인 에러 이벤트 발생 후 예외를 다시 발생
            run_manager.on_chain_error(e)
            raise e
        
        # 응답으로부터 출력 생성
        outputs = self.create_outputs(response)
        
        # 체인 종료 이벤트 발생
        run_manager.on_chain_end({"outputs": outputs})
        
        # 생성된 출력 반환
        return outputs
    
    # 이하 메서드들(aapply, predict, apredict 등)은 다양한 방식의 LLM 실행과 결과 처리를 담당
    # 각 메서드의 구체적인 기능은 메서드 이름과 구현에서 유추 가능

    async def aapply(
        self, input_list: List[Dict[str, Any]], callbacks: Callbacks = None
    ) -> List[Dict[str, str]]:
        print("*@*@*@*@*@ AAPPLY in LLMChain CLASS *@*@*@*@*@")
        """Utilize the LLM generate method for speed gains."""
        callback_manager = AsyncCallbackManager.configure(
            callbacks, self.callbacks, self.verbose
        )
        run_manager = await callback_manager.on_chain_start(
            dumpd(self),
            {"input_list": input_list},
        )
        try:
            response = await self.agenerate(input_list, run_manager=run_manager)
        except BaseException as e:
            await run_manager.on_chain_error(e)
            raise e
        outputs = self.create_outputs(response)
        await run_manager.on_chain_end({"outputs": outputs})
        return outputs

    @property
    def _run_output_key(self) -> str:
        print("*@*@*@*@*@ _RUN_OUTPUT_KEY in LLMChain CLASS *@*@*@*@*@")
        return self.output_key

    def create_outputs(self, llm_result: LLMResult) -> List[Dict[str, Any]]:
        print("*@*@*@*@*@ CREATE_OUTPUTS in LLMChain CLASS *@*@*@*@*@")
        # """Create outputs from response."""
        result = [
            # Get the text of the top generated string.
            {
                self.output_key: self.output_parser.parse_result(generation),
                "full_generation": generation,
            }
            for generation in llm_result.generations
        ]
        if self.return_final_only:
            result = [{self.output_key: r[self.output_key]} for r in result]
        return result

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        print("*@*@*@*@*@ _ACALL in LLMChain CLASS *@*@*@*@*@")
        response = await self.agenerate([inputs], run_manager=run_manager)
        return self.create_outputs(response)[0]

    def predict(self, callbacks: Callbacks = None, **kwargs: Any) -> str:
        print("*@*@*@*@*@ PREDICT in LLMChain CLASS *@*@*@*@*@")
        # """Format prompt with kwargs and pass to LLM.

        # Args:
        #     callbacks: Callbacks to pass to LLMChain
        #     **kwargs: Keys to pass to prompt template.

        # Returns:
        #     Completion from LLM.

        # Example:
        #     .. code-block:: python

        #         completion = llm.predict(adjective="funny")
        # """
        return self(kwargs, callbacks=callbacks)[self.output_key]

    async def apredict(self, callbacks: Callbacks = None, **kwargs: Any) -> str:
        print("*@*@*@*@*@ APREDICT in LLMChain CLASS *@*@*@*@*@")
        """Format prompt with kwargs and pass to LLM.

        Args:
            callbacks: Callbacks to pass to LLMChain
            **kwargs: Keys to pass to prompt template.

        Returns:
            Completion from LLM.

        Example:
            .. code-block:: python

                completion = llm.predict(adjective="funny")
        """
        return (await self.acall(kwargs, callbacks=callbacks))[self.output_key]

    def predict_and_parse(
        self, callbacks: Callbacks = None, **kwargs: Any
    ) -> Union[str, List[str], Dict[str, Any]]:
        print("*@*@*@*@*@ PREDICT_AND_PARSE in LLMChain CLASS *@*@*@*@*@")
        """Call predict and then parse the results."""
        warnings.warn(
            "The predict_and_parse method is deprecated, "
            "instead pass an output parser directly to LLMChain."
        )
        result = self.predict(callbacks=callbacks, **kwargs)
        if self.prompt.output_parser is not None:
            return self.prompt.output_parser.parse(result)
        else:
            return result

    async def apredict_and_parse(
        self, callbacks: Callbacks = None, **kwargs: Any
    ) -> Union[str, List[str], Dict[str, str]]:
        print("*@*@*@*@*@ APREDICT_AND_PARSE in LLMChain CLASS *@*@*@*@*@")
        """Call apredict and then parse the results."""
        warnings.warn(
            "The apredict_and_parse method is deprecated, "
            "instead pass an output parser directly to LLMChain."
        )
        result = await self.apredict(callbacks=callbacks, **kwargs)
        if self.prompt.output_parser is not None:
            return self.prompt.output_parser.parse(result)
        else:
            return result

    def apply_and_parse(
        self, input_list: List[Dict[str, Any]], callbacks: Callbacks = None
    ) -> Sequence[Union[str, List[str], Dict[str, str]]]:
        print("*@*@*@*@*@ APPLY_AND_PARSE in LLMChain CLASS *@*@*@*@*@")
        """Call apply and then parse the results."""
        warnings.warn(
            "The apply_and_parse method is deprecated, "
            "instead pass an output parser directly to LLMChain."
        )
        result = self.apply(input_list, callbacks=callbacks)
        return self._parse_generation(result)

    def _parse_generation(
        self, generation: List[Dict[str, str]]
    ) -> Sequence[Union[str, List[str], Dict[str, str]]]:
        print("*@*@*@*@*@ _PARSE_GENERATION in LLMChain CLASS *@*@*@*@*@")
        if self.prompt.output_parser is not None:
            return [
                self.prompt.output_parser.parse(res[self.output_key])
                for res in generation
            ]
        else:
            return generation

    async def aapply_and_parse(
        self, input_list: List[Dict[str, Any]], callbacks: Callbacks = None
    ) -> Sequence[Union[str, List[str], Dict[str, str]]]:
        print("*@*@*@*@*@ AAPPLY_AND_PARSE in LLMChain CLASS *@*@*@*@*@")
        """Call apply and then parse the results."""
        warnings.warn(
            "The aapply_and_parse method is deprecated, "
            "instead pass an output parser directly to LLMChain."
        )
        result = await self.aapply(input_list, callbacks=callbacks)
        return self._parse_generation(result)

    @property
    def _chain_type(self) -> str:
        print("*@*@*@*@*@ _CHAIN_TYPE in LLMChain CLASS *@*@*@*@*@")
        return "llm_chain"

    @classmethod
    def from_string(cls, llm: BaseLanguageModel, template: str) -> LLMChain:
        print("*@*@*@*@*@ FROM_STRING in LLMChain CLASS *@*@*@*@*@")
        # 문자열 템플릿과 LLM을 이용해 LLMChain 인스턴스 생성
        prompt_template = PromptTemplate.from_template(template)
        return cls(llm=llm, prompt=prompt_template)
    # 주어진 텍스트의 토큰 수를 반환
    def _get_num_tokens(self, text: str) -> int:
        print("*@*@*@*@*@ GET_NUM_TOKENS in LLMChain CLASS *@*@*@*@*@")
        return _get_language_model(self.llm).get_num_tokens(text)


