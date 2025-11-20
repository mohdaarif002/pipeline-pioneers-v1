import os
import streamlit as st
from typing import Optional, List, Mapping, Any

GROQ_AVAILABLE = False
try:
    from groq import Groq as GroqClient
    GROQ_AVAILABLE = True
except Exception as e:
    GROQ_IMPORT_ERROR = e

# A small, defensive wrapper similar to the monolith version
class GroqLangChainFallback:
    def __init__(self, api_key: str, model: str = "compound-beta", temperature: float = 0.0, max_tokens: int = 1500):
        try:
            self.client = GroqClient(api_key=api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Groq client: {e}")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate_text(self, prompt: str) -> str:
        msgs = [{"role": "system", "content": "You are a helpful assistant that outputs executable python code only."},
                {"role": "user", "content": prompt}]
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=msgs,
                temperature=float(self.temperature),
                max_tokens=int(self.max_tokens),
            )
        except Exception as e:
            st.exception(e)
            return ""

        text = None
        try:
            if resp and getattr(resp, "choices", None):
                first = resp.choices[0]
                try:
                    text = first.message.content
                except Exception:
                    msg = None
                    try:
                        msg = first.get("message")
                    except Exception:
                        pass
                    if isinstance(msg, dict):
                        text = msg.get("content")
                    else:
                        text = str(first)
        except Exception:
            text = None

        if not text:
            try:
                st.write(resp)
            except Exception:
                st.write(str(resp))
        return text or ""

    def __call__(self, prompt: str) -> str:
        return self.generate_text(prompt)

# prefer the LangChain-compatible wrapper when available in the app
GroqLangChain = GroqLangChainFallback