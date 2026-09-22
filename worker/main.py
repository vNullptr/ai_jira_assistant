from clients.jira import JiraAPIClient
from clients.database import PostgresDatabaseClient
from clients.llm import MistralClient
from worker.worker import Worker
from eval.ragas import RagasEval

from langfuse import get_client
from config import Settings
import asyncio

if __name__ == "__main__":
    settings = Settings()
    lf_client = get_client()

    jac = JiraAPIClient(domain=settings.JIRA_DOMAIN, auth_mail=settings.JIRA_AUTH_MAIL, api_token=settings.JIRA_API_TOKEN)
    pdc = PostgresDatabaseClient(host=settings.POSTGRES_HOST,user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, dbname=settings.POSTGRES_DBNAME)
    mc = MistralClient(langfuse_client=lf_client, temperature=0, base_url=settings.MODEL_BASE_URL)
    re = RagasEval(base_url=settings.MODEL_BASE_URL)

    worker = Worker(database_client=pdc, jira_client=jac, llm_client=mc, evaluator=re)

    runner = asyncio.Runner()
    runner.run(worker.start())