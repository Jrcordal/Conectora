from langchain_google_genai import ChatGoogleGenerativeAI
from django.conf import settings

llm_08_temperature = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        temperature=0.8,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key = settings.GOOGLE_API_KEY

    )
llm_01_temperature = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.1,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        google_api_key = settings.GOOGLE_API_KEY
        )
llm_06_temperature = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.6,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    google_api_key = settings.GOOGLE_API_KEY
)