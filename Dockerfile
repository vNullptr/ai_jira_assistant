FROM python:3.12-slim

WORKDIR C:\Users\hp\Desktop\PROJECTS\mail_jira_assistant

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 5000

CMD ["fastapi", "run", "api/main.py"]