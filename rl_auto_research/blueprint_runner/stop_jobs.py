"""
Stop (and optionally delete) jobs.

Dispatches to the configured backend (PAI or SSH).

Usage:
    python -m rl_auto_research.blueprint_runner.stop_jobs --stop-job-id=<job_id>
    python -m rl_auto_research.blueprint_runner.stop_jobs --stop-job-id=<id1> --stop-job-id=<id2>
    python -m rl_auto_research.blueprint_runner.stop_jobs --stop-job-id=<job_id> --delete
"""

import argparse
import time

from rl_auto_research.blueprint_runner.base import get_runner


def main():
    parser = argparse.ArgumentParser(
        prog="stop_jobs",
        description="Stop (and optionally delete) jobs.",
    )
    parser.add_argument(
        "--stop-job-id", action="append", required=True,
        help="Job ID to stop. Can be specified multiple times.",
    )
    parser.add_argument(
        "--delete", action="store_true",
        help="Also delete the job(s) after stopping.",
    )
    args = parser.parse_args()

    runner = get_runner()

    for job_id in args.stop_job_id:
        print(f"Stopping job {job_id} ...")
        try:
            runner.stop(job_id)
        except Exception as e:
            print(f"Failed to stop {job_id}: {e}")

    if args.delete:
        time.sleep(3)
        for job_id in args.stop_job_id:
            retry = 3
            for attempt in range(retry):
                try:
                    runner.delete(job_id)
                    print(f"Deleted job {job_id}")
                    break
                except Exception as e:
                    print(f"Failed to delete {job_id}: {e}, retrying in 5s ...")
                    time.sleep(5)


if __name__ == "__main__":
    main()
