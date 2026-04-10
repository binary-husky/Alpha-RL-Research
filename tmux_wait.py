import argparse
import subprocess
import time

SHELLS = {"bash", "zsh", "sh", "fish", "csh", "tcsh", "ksh", "dash", "ash"}

def smart_sleep(session: str, seconds: float, check_every: float = 2.0) -> bool:
    end_time = time.time() + seconds
    while time.time() < end_time:
        try:
            r = subprocess.run(
                ["tmux", "list-panes", "-F", "#{pane_current_command}", "-t", session],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode != 0:
                return False
            cmds = [l.strip().lower() for l in r.stdout.splitlines() if l.strip()]
            if not any(c not in SHELLS for c in cmds):
                return False
        except Exception:
            return False
        time.sleep(min(check_every, end_time - time.time()))
    return True

def print_tmux_window(session: str, lines: int = 100):
    try:
        r = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", session],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            output_lines = r.stdout.splitlines()
            print("\n\n--- tmux pane output (last {} lines) ---".format(lines))
            print("\n".join(output_lines[-lines:]))
            print("--- tmux pane output ends ---\n\n")
    except Exception as e:
        print(f"Failed to capture tmux pane: {e}")

def main():
    parser = argparse.ArgumentParser(description="Wait for a tmux session with smart early-exit.")
    parser.add_argument("session", help="tmux session name")
    parser.add_argument("seconds", type=float, help="total seconds to wait")
    args = parser.parse_args()
    timed_out = smart_sleep(args.session, args.seconds, 2)
    print_tmux_window(args.session, 100)
    raise SystemExit(0 if timed_out else 1)

if __name__ == "__main__":
    main()
