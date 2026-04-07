"""
Unified OpenCode agent runner — supports both leader and worker modes.

Leader mode:  Orchestrates research via a blueprint, manages a running_flag file.
Worker mode:  Runs inside a PAI DLC node, checks tmux session liveness.

Usage:
    python -m rl_auto_research.opencode_runner leader \
        --attach=http://localhost:4096 \
        --blueprint=/path/to/blueprint.md \
        --additional-prompt="..."

    python -m rl_auto_research.opencode_runner worker \
        <opencode args...>
"""

import argparse
import json
import os
import subprocess
import sys
import time


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _get_latest_opencode_session_id() -> str | None:
    result = subprocess.run(
        ["opencode", "session", "list", "--format=json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    sessions = json.loads(result.stdout)
    if not sessions:
        return None
    latest = max(sessions, key=lambda s: s["updated"])
    return latest["id"]


def _prepare_yolo_config():
    """Copy opencode.json to opencode-yolo.json with permissive permissions."""
    config_dir = os.path.expanduser("~/.config/opencode")
    src = os.path.join(config_dir, "opencode.json")
    dst = os.path.join(config_dir, "opencode-yolo.json")

    if os.path.exists(src):
        with open(src, "r") as f:
            config = json.load(f)
    else:
        config = {"$schema": "https://opencode.ai/config.json"}

    config["permission"] = {"*": {"*": "allow"}}

    os.makedirs(config_dir, exist_ok=True)
    with open(dst, "w") as f:
        json.dump(config, f, indent=2)

    return dst


def run_opencode(args: list[str], *, continue_mode=False, session_id=None,
                 need_permission_error_fix=False, resume_instruction="",
                 skip_permissions=False) -> tuple[int, bool]:
    cmd = ["opencode"] + args

    if continue_mode:
        cmd = cmd[:-1]  # drop the original prompt

        if resume_instruction:
            msg = f"Instruction: {resume_instruction}"
        else:
            msg = "continue your job"

        if need_permission_error_fix:
            msg += ", permission error detected, please try some workaround, e.g. tmux command."
        cmd += ["-c", session_id, msg]

    env = None
    if skip_permissions:
        yolo_config = _prepare_yolo_config()
        env = {**os.environ, "OPENCODE_CONFIG": yolo_config}

    print("[controller message]: executing", " ".join(cmd))
    print("[controller message]: using envs", env)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

    terminated_due_to_permission = False
    for stream in (process.stdout, process.stderr):
        if stream:
            for line in stream:
                print(line, end="")
                if "The user rejected permission to use this specific tool call" in line:
                    print("[controller message]: Tool call was rejected by permission settings.")
                    terminated_due_to_permission = True

    process.wait()
    print(f"[controller message]: Return code: {process.returncode}, permission_error={terminated_due_to_permission}")
    return process.returncode, terminated_due_to_permission


def _is_opencode_web_running() -> bool:
    result = subprocess.run(["pgrep", "-f", "opencode web"], capture_output=True, text=True)
    return result.returncode == 0


def _is_kite_client_running() -> bool:
    result = subprocess.run(["pgrep", "-f", "kite-client"], capture_output=True, text=True)
    return result.returncode == 0


def _ensure_opencode_web(skip_permissions=False):
    if not _is_opencode_web_running():
        env = None
        if skip_permissions:
            yolo_config = _prepare_yolo_config()
            env = {**os.environ, "OPENCODE_CONFIG": yolo_config}
        print("[controller message]: Starting opencode web...")
        subprocess.Popen(["opencode", "web"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env)
        time.sleep(2)

    # Start kite-client for remote monitoring if configured
    if not _is_kite_client_running():
        from rl_auto_research.config import config
        remote_cfg = config.get("remote_monitor", {})
        remote_url = remote_cfg.get("remote_url")
        api_key = remote_cfg.get("api_key")
        if remote_url and api_key:
            print(f"[controller message]: Starting kite-client -> {remote_url}")
            subprocess.Popen(   # `pip install kite-strings` to get kite-client CLI tool
                ["kite-client", "--server", remote_url, "--apikey", api_key, "--map", "4096:opencode_web"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(2)
            print("[controller message]: kite-client started for remote monitoring.")
        else:
            time.sleep(2)
            print("[controller message]: remote_monitor config not found, skipping kite-client startup.")


# ---------------------------------------------------------------------------
# Leader mode
# ---------------------------------------------------------------------------

def _should_continue(terminated_due_to_permission: bool, running_flag: str) -> bool:
    if terminated_due_to_permission:
        print("[controller message]: Session terminated due to permission. Will attempt to continue.")
        return True
    if os.path.exists(running_flag):
        return True
    else:
        return False


def run(research_topic: str = "", blueprint:str="", mod: str = "", resume_latest_session: bool = False, resume_instruction: str = "", only_run_planning: bool = False, skip_permissions: bool = False) -> int:

    if only_run_planning:
        assert mod == "leader", "only_run_planning mode is only applicable for leader mode"

    if mod == "leader":
        leader_skill_path = "skills/leader_experiment.md"
        leader_skill_path = os.path.abspath(leader_skill_path)
        assert os.path.exists(leader_skill_path), f"skill not found: {leader_skill_path}"

        if os.path.exists(research_topic):
            running_flag = research_topic + ".running_flag"
            with open(research_topic, "r") as f:
                research_topic = f"Research topic:\n{f.read()}"
        else:
            running_flag = leader_skill_path + ".running_flag"

        with open(running_flag, "w+") as f:
            f.write("Running")

        prompt = (
            "You are the main research agent, the research lead, responsible for designing, evaluating, and dispatching research plans.\n"
            f"Experiment skill: {leader_skill_path}\n"
            f"After all experiments are complete and the final report is written, please delete {running_flag}\n"
            f"{research_topic}\n"
        )

        if only_run_planning:
            prompt += "Only generate the research plan and exit without running the experiments."

    elif mod == "worker":
        worker_skill_path = "skills/worker_experiment.md"
        worker_skill_path = os.path.abspath(worker_skill_path)
        worker_blueprint_path = os.path.abspath(blueprint)
        assert os.path.exists(worker_skill_path), f"skill not found: {worker_skill_path}"
        assert os.path.exists(worker_blueprint_path), f"blueprint not found: {worker_blueprint_path}"
        running_flag = worker_blueprint_path + ".running_flag"

        with open(running_flag, "w+") as f:
            f.write("Running")

        prompt = (
            f"Your task is to follow the instructions in {worker_skill_path} and complete the experiment described in blueprint {worker_blueprint_path}.\n"
            f"After the experiment is finally complete, please delete {running_flag}.\n"
            f"Try everything you can to make the experiment running until reaching the time limit or completing the goal written in the blueprint.\n"
        )

    assert not (resume_latest_session and only_run_planning), "resume_latest_session and only_run_planning cannot be both True"

    _ensure_opencode_web(skip_permissions=skip_permissions)
    run_args = ["run", f"--attach=http://localhost:4096", prompt]

    print("[controller message]: run opencode 1st ...")
    if resume_latest_session:
        terminated_due_to_permission = False
    else:
        returncode, terminated_due_to_permission = run_opencode(run_args, skip_permissions=skip_permissions)
        if only_run_planning:
            return returncode


    # begin opencode agent
    while _should_continue(terminated_due_to_permission, running_flag):
        print("[controller message]: Continuing session ...")
        session_id = _get_latest_opencode_session_id()
        if session_id:
            returncode, terminated_due_to_permission = run_opencode(
                run_args, continue_mode=True, session_id=session_id,
                need_permission_error_fix=terminated_due_to_permission,
                resume_instruction=resume_instruction,
                skip_permissions=skip_permissions,
            )
            resume_instruction = ""  # only apply the resume_instruction for one time

    if mod == "worker":
        still_training = "/still_training"
        if os.path.exists(still_training):
            os.remove(still_training)

    print("[controller message]: finished.")
    return returncode



# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(prog="opencode_runner")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Common arguments
    for sp_name in ("leader", "worker"):
        sp = subparsers.add_parser(sp_name)
        sp.add_argument("--research-topic", default="", help="Extra instruction")
        sp.add_argument("--blueprint", default="", help="Path to research skill .md")
        sp.add_argument("--resume", "--resume-latest-session", action="store_true", dest="resume_latest_session", help="Resume the latest session")
        sp.add_argument("--resume-instruction", default="", help="Instruction for resuming")
        sp.add_argument("--only-run-planning", action="store_true", help="Run once and exit")
        sp.add_argument("--skip-permissions", action="store_true", help="Use permissive opencode config (allow all tools)")
    args = parser.parse_args()

    rc = run(
        research_topic=args.research_topic,
        blueprint=args.blueprint,
        mod=args.mode,
        resume_latest_session=args.resume_latest_session,
        resume_instruction=args.resume_instruction,
        only_run_planning=args.only_run_planning,
        skip_permissions=args.skip_permissions,
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
