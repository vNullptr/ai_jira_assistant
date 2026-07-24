from enum import StrEnum

class JobStatus(StrEnum):
    FAILED = 'failed'
    PENDING = 'pending'
    PROCESSING = 'processing'
    DONE = 'done'
    