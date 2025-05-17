from enum import Enum


DEFAULT_GCC_FLAGS = "-g -O2 -std=c99 -Wall -Wformat=2 -Wshadow -Wpointer-arith -Wunreachable-code -Wconversion -Wno-sign-conversion -Wbad-function-cast"

class Language(str, Enum):
    C = "C"
    PYTHON = "python"
    GO = "go"
    def with_version(self):
        if self == Language.C:
            return LanguageWithVersion.C
        elif self == Language.PYTHON:
            return LanguageWithVersion.PYTHON
        elif self == Language.GO:
            return LanguageWithVersion.GO
        else:
            raise ValueError(f"Unsupported language: {self}")

class LanguageWithVersion(str, Enum):
    C = "c_std11"
    PYTHON = "python_3.7"
    GO = "go_1.19"
    def without_version(self):
        if self == LanguageWithVersion.C:
            return Language.C
        elif self == LanguageWithVersion.PYTHON:
            return Language.PYTHON
        elif self == LanguageWithVersion.GO:
            return Language.GO
        else:
            raise ValueError(f"Unsupported language: {self}")


class SubmissionStatus(str, Enum):
    NO_SUBMISSIONS = ""
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
