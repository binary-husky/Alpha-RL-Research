import argparse
import subprocess
import time

SHELLS = {"bash", "zsh", "sh", "fish", "csh", "tcsh", "ksh", "dash", "ash"}

def smart_sleep(session: str, seconds: float, check_every: float = 2.0) -> bool:
    """
    Replacement for time.sleep() that returns early when the command finishes.

    Returns:
        True  - Normal timeout (command is still running)
        False - Early return (command finished or session is gone)
    """
    end_time = time.time() + seconds
    while time.time() < end_time:
        try:
            r = subprocess.run(
                ["tmux", "list-panes", "-F", "#{pane_current_command}", "-t", session],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode != 0:
                return False  # session is gone
            cmds = [l.strip().lower() for l in r.stdout.splitlines() if l.strip()]
            if not any(c not in SHELLS for c in cmds):
                return False  # command finished, back to shell
        except Exception:
            return False

        time.sleep(min(check_every, end_time - time.time()))

    return True


def main():
    parser = argparse.ArgumentParser(description="Wait for a tmux session with smart early-exit.")
    parser.add_argument("session", help="tmux session name")
    parser.add_argument("seconds", type=float, help="total seconds to wait")
    args = parser.parse_args()

    timed_out = smart_sleep(args.session, args.seconds, 2)
    raise SystemExit(0 if timed_out else 1)


if __name__ == "__main__":
    main()