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

    print(
        "[Tip From User's Ghost]: Running for a while now? You can check [exp_result_dir] to see what has been completed, "
        "if there are already many results, you can try to take advantage the waiting time to:\n"
        "   - analyze the results\n"
        "   - **draw figures using seaborn**\n"
        "   - write a `progress_report.md`.\n"
        "   - web search to obtain academic background knowledge about this research.\n"
        "But remember, whatever you do, `progress_report.md` is not the end, do NOT delete the running flag file until all jobs are done."
    )


if __name__ == "__main__":
    main()
