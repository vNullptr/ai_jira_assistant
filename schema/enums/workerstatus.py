from enum import StrEnum

class WorkerStatus(StrEnum):
    AVAILABLE = 'available'
    PROCESSING = 'processing'
    PAUSED = 'paused' # might be useless 
    