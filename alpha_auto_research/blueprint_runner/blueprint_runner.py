"""
Blueprint runner CLI entry point.

Dispatches to the configured backend (PAI or SSH).

Usage:
    python -m alpha_auto_research.blueprint_runner.blueprint_runner --blueprint=<path>
"""

import argparse

from alpha_auto_research.blueprint_runner.base import get_runner


def run_blueprint():
    parser = argparse.ArgumentParser()
    parser.add_argument('--blueprint', type=str, required=True, help='Path to the blueprint to run')
    parser.add_argument('--runner', type=str, required=True, choices=['ssh', 'pai'], help='Backend runner type')
    parser.add_argument('--acknowledge-max-parallel-capacity', type=int, required=True, help='Acknowledge the maximum parallel capacity before running the blueprint')
    args = parser.parse_args()

    runner = get_runner(args.runner)
    job_id = runner.launch(blueprint_path=args.blueprint, exp_name="")
    print(f"Job submitted: {job_id}")


if __name__ == "__main__":
    run_blueprint()
