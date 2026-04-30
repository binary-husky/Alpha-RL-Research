"""Enumerated values for agent role and execution backend."""

from enum import Enum


class Role(str, Enum):
    LEADER = "leader"
    WORKER = "worker"

    def __str__(self) -> str:
        return self.value


class Runner(str, Enum):
    SSH = "ssh"
    PAI = "pai"

    def __str__(self) -> str:
        return self.value
