from langchain_core.prompts import ChatPromptTemplate
from langfuse import get_client
from config import Settings

settings = Settings()
langfuse = get_client()

extraction_prompt = ChatPromptTemplate(langfuse.get_prompt("mail-extraction-classification", label="production").get_langchain_prompt())