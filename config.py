from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):

    # JIRA
    JIRA_DOMAIN : str 

    # LANGFUSE
    LANGFUSE_PUBLIC_KEY : str
    LANGFUSE_SECRET_KEY : str
    LANGFUSE_BASE_URL : str     
    
    model_config = SettingsConfigDict(env_file=".env")
    
    
    def model_post_init(self, context):
        if self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY:
            os.environ["LANGFUSE_SECRET_KEY"] = self.LANGFUSE_SECRET_KEY
            os.environ["LANGFUSE_PUBLIC_KEY"] = self.LANGFUSE_PUBLIC_KEY
            os.environ["LANGFUSE_BASE_URL"] = self.LANGFUSE_BASE_URL 
        
        return super().model_post_init(context)