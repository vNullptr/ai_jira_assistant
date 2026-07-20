from langchain_core.prompts import ChatPromptTemplate


basePrompt = ChatPromptTemplate(
    [
        ("human", "test prompt mistral.")
    ]
)