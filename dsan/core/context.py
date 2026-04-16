from enum import Enum


class ExecutionMode(Enum):
    ON_CLOUD = "on_cloud"
    OFF_CLOUD = "off_cloud"
    HYBRID = "hybrid"


class ExecutionContext:
    def __init__(self, mode=ExecutionMode.HYBRID):
        self.mode = mode