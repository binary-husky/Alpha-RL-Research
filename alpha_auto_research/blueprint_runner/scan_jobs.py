"""
Scan and display running jobs.

Dispatches to the configured backend (PAI or SSH).

Usage:
    python -m alpha_auto_research.blueprint_runner.scan_jobs
"""

from alpha_auto_research.blueprint_runner.base import get_runner


def main():
    runner = get_runner()
    jobs = runner.scan_jobs()
    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()
