"""
Scan and display running jobs.

Dispatches to the configured backend (PAI or SSH).

Usage:
    python -m alpha_auto_research.blueprint_runner.scan_jobs
"""

import argparse

from alpha_auto_research.blueprint_runner.base import get_runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runner', type=str, required=True, choices=['ssh', 'pai'], help='Backend runner type')
    args = parser.parse_args()

    runner = get_runner(args.runner)
    jobs = runner.scan_jobs()
    for job in jobs:
        print(job)


if __name__ == "__main__":
    main()
