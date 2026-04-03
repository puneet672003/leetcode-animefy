from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from core.config import Config


class LLMClient:
    _llm = None
    _model = "open-mistral-7b"

    @classmethod
    def _get_llm(cls):
        if cls._llm is None:
            cls._llm = ChatMistralAI(api_key=Config.MISTRAL_API_KEY, model=cls._model)
        return cls._llm

    @classmethod
    def generate(cls, system_prompt: str, user_input: str) -> str:
        llm = cls._get_llm()
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{input}")]
        )
        chain = prompt | llm | StrOutputParser()
        return chain.invoke({"input": user_input})

    @classmethod
    async def a_generate(cls, system_prompt: str, user_input: str) -> str:
        llm = cls._get_llm()
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{input}")]
        )
        chain = prompt | llm | StrOutputParser()
        return await chain.ainvoke({"input": user_input})
