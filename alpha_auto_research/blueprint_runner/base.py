"""
Abstract base class for experiment launchers (blueprint runners).
"""

from abc import ABC, abstractmethod


class ExperimentSubagent(ABC):
    """
    Base class for launching experiments on different backends.

    Subclass this and implement launch(), monitor(), stop(), scan_jobs(), stop_jobs().
    """

    @abstractmethod
    def launch(self, blueprint_path: str, exp_name: str, **kwargs) -> str:
        """Launch an experiment. Returns a backend-specific job identifier."""
        ...

    @abstractmethod
    def monitor(self, job_id: str) -> str:
        """Block until the job finishes. Returns terminal status."""
        ...

    @abstractmethod
    def stop(self, job_id: str) -> None:
        """Stop a running job."""
        ...

    @abstractmethod
    def delete(self, job_id: str) -> None:
        """Delete a job."""
        ...

    @abstractmethod
    def scan_jobs(self) -> list[dict]:
        """List recent jobs. Returns list of dicts with job_id, display_name, status, create_time."""
        ...


def get_runner() -> ExperimentSubagent:
    """Factory: return the runner configured in research_config.jsonc."""
    from alpha_auto_research.config import config

    runner_type = config.get("runner", "pai")

    if runner_type == "pai":
        from alpha_auto_research.blueprint_runner.pai_runner import PaiExperimentSubagent
        return PaiExperimentSubagent()
    elif runner_type == "ssh":
        from alpha_auto_research.blueprint_runner.ssh_runner import SshExperimentSubagent
        return SshExperimentSubagent()
    else:
        raise ValueError(f"Unknown runner type: {runner_type!r}. Expected 'pai' or 'ssh'.")
