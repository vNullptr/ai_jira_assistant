from enum import Enum

class JobStatus(Enum):
    FAILED = 'failed'
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'
    