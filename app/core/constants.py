from enum import StrEnum


class CaseStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskNames:
    ANALYSE_CASE = "analyse_case_job"
