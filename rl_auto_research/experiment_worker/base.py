"""
Base class for experiment subagents.
"""

from abc import ABC, abstractmethod


class ExperimentSubagent(ABC):
    """Abstract base class for experiment execution backends."""

    @abstractmethod
    def launch(self, blueprint_path: str, exp_name: str) -> str:
        """Launch an experiment from a blueprint. Returns job_id."""
        pass

    @abstractmethod
    def monitor(self, job_id: str) -> str:
        """Monitor a running job. Returns final status."""
        pass

    @abstractmethod
    def stop(self, job_id: str) -> None:
        """Stop a running job."""
        pass
