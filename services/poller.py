from pydantic import BaseModel, Field
from clients.mail import MailClient

class Poller(BaseModel):
    mail_client : MailClient = Field(description="Mail client used to continuousely poll mails.")
    interval : int = Field(description="Polling interval, not used with some MailClients. Default 0")
    
    async def poll(self):
        pass
    
    async def pause(self):
        pass
    
    async def stop(self):
        pass