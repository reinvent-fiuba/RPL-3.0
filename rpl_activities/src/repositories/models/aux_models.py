from enum import Enum


class Language(str, Enum):
    C = "C"
    PYTHON = "python"
    GO = "go"

class LanguageWithVersion(str, Enum):
    C = "c_std11"
    PYTHON = "python_3.7"
    GO = "go_1.19"


class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    ENQUEUED = "ENQUEUED"
    PROCESSING = "PROCESSING"
    BUILD_ERROR = "BUILD_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    FAILURE = "FAILURE"
    SUCCESS = "SUCCESS"
    TIME_OUT = "TIME_OUT"


class RPLFileType(str, Enum):
    GZIP = "application/gzip"
    TEXT = "text"
