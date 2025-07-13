from __future__ import annotations

import os

try:
    from langchain.chains import ConversationChain
    from langchain.memory import ConversationBufferMemory
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import PromptTemplate
except Exception:  # pragma: no cover - optional dependency
    ConversationChain = None


class ChatAssistant:
    """Simple conversational assistant using OpenAI chat models."""

    def __init__(self, model_name: str = "gpt-4o", openai_api_key: str | None = None) -> None:
        if ConversationChain is None:
            # Minimal fallback when langchain is unavailable
            self.chain = None
        else:
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
        if self.chain is None:
            return ""
        return self.chain.predict(input=message)
