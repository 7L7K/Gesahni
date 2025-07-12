from __future__ import annotations

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
import os
from langchain.prompts import PromptTemplate


class ChatAssistant:
    """Simple conversational assistant using OpenAI chat models."""

    def __init__(self, model_name: str = "gpt-4o", openai_api_key: str | None = None) -> None:
        self.memory = ConversationBufferMemory()
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY", "sk-test")
        self.model = ChatOpenAI(model_name=model_name, openai_api_key=api_key)
        template = (
            "You are a friendly assistant with a playful attitude.\n"
            "{history}\nHuman: {input}\nAssistant:"
        )
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template,
        )
        self.chain = ConversationChain(llm=self.model, memory=self.memory, prompt=prompt)

    def chat(self, message: str) -> str:
        """Return a reply for ``message`` preserving conversation history."""
        return self.chain.predict(input=message)
