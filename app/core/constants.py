from enum import Enum


class CaseStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskNames:
    ANALYSE_CASE = "analyse_case_job"
