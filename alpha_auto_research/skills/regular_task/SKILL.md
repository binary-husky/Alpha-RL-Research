1. Do Not Terminate Without Careful Consideration
2. Run important commands in tmux sessions, and monitor them with `tmux_wait.py` to detect errors early and save time.
3. Always use `python ./tmux_wait.py` instead of `sleep` to wait before checking tmux content, so that you can detect errors early and avoid wasting time.
4. tmux session names must use prefix `ajet_worker_*`

## Service Monitoring Skill

```
    ---
    name: monitor-with-tmux
    description: Monitor training progress by reading tmux content at exponential backoff intervals (30s, 1min, 2min, 4min, 8min, 16min), analyze logs when anomalies occur, and provide fix suggestions
    license: Complete terms in LICENSE.txt
    ---

    # Monitor with Tmux

    Monitor in tmux, detect anomalies, analyze errors, provide fix suggestions.

    ## Step Zero

    Create a sleep script for tmux monitoring:

    1. Create `./tmux_wait.py`

    ```python
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
    ```

    ## Begin Monitoring

    When you need to monitor a tmux window, run:

    ```bash
    python ./tmux_wait.py my_ajet_session_name 30
    ```

    This means:
    1. Monitor the tmux session named my_ajet_session_name
    2. Wait for 30 seconds

    - Exit code 0: Normal timeout (command is still running)
    - Exit code 1: Command finished early or session disappeared

    ## Using SSH

    When using SSH, always use a local tmux window to establish the SSH connection.

    ## When You Want to Delay Before Reading tmux Again

    You must have early-return-on-error capability. Do not use `sleep xxx`; instead use `python ./tmux_wait.py my_ajet_session_name xxx`

    DO NOT USE: `sleep 60 && tmux capture-pane -t my_ajet_session_name -p | tail -80`

    YOU SHOULD USE: `python ./tmux_wait.py my_ajet_session_name 30 && tmux capture-pane -t my_ajet_session_name -p | tail -80`

    - 60 seconds is too long
    - Always use `python ./tmux_wait.py` to wait



    ## Examples:


    ### Without SSH

    0 examples available


    ### With SSH

    1 example available

    ```agent

    --- example user instruction begin ---
    login
    ssh root@localhost -p 8824
    goto
    /foo/bar/venv
    run with venv and monitor
    source .venv/bin/activate && python -m ajet.launcher --conf tests/bench/benchmark_math/benchmark_math.yaml --skip-check-avail-gpu --with-ray
    --- example user instruction end ---

    --- example agent reaction begin ---
    The user wants me to monitor a tmux session while running a training job. Let me break down what they're asking:
    1. SSH into a remote machine (root@localhost -p 8824)
    2. Go to a specific directory
    3. Activate a virtual environment and run a Python command
    4. Monitor the tmux session

    # Write tmux_wait.py
    ....

    # Create tmux session for training (note: session name must contain the keyword `ajet`)
    # note, you are absolutely NOT allowed to attach command in `tmux new-session`, because you need to send commands via `tmux send-keys` in the tmux session after it is created!
    $ tmux new-session -d -s ajet_session -c "/foo/bar/venv" # do not add any command after tmux new-session! Because you need to send commands via `tmux send-keys` !
    ...

    # Send SSH command to tmux session
    $ tmux send-keys -t ajet_session "ssh root@localhost -p 8824" Enter
    ...

    # Wait and check SSH connection
    $ python3 ./tmux_wait.py ajet_session 10 && tmux capture-pane -t ajet_session -p | tail -20
    SSH connected successfully. Now I need to navigate to the directory and run the training command. Let me send the commands to the tmux session.
    ...

    # Navigate to working directory
    $ tmux send-keys -t ajet_session "cd /foo/bar/venv" Enter
    ...

    # Start training with venv and launcher
    $ tmux send-keys -t ajet_session "source .venv/bin/activate && python -m ajet.launcher --conf tests/bench/benchmark_math/benchmark_math.yaml --skip-check-avail-gpu --with-ray" Enter
    ...

    # Capture initial training output
    $ tmux capture-pane -t ajet_session -p | tail -40
    ...

    # Wait 30s and check training progress
    $ python3 ./tmux_wait.py ajet_session 30 && tmux capture-pane -t ajet_session -p | tail -50
    ...
    Training is running. The command is executing properly. Let me continue monitoring at 1 minute intervals.

    # Wait 1min and check training progress
    $ python3 ./tmux_wait.py ajet_session 60 && tmux capture-pane -t ajet_session -p | tail -50
    ...

    # Wait 2min and check training progress
    $ python3 ./tmux_wait.py ajet_session 120 && tmux capture-pane -t ajet_session -p | tail -60
    ...
    Training is progressing well. Checkpoints loaded, vLLM server started, swanlab is tracking the run. No errors so far, just warnings. Let me continue monitoring.

    # Wait 4min and check training progress
    $ python3 ./tmux_wait.py ajet_session 240 && tmux capture-pane -t ajet_session -p | tail -60
    ...

    ... multiple monitoring rounds ...

    --- example agent reaction end ---

    # Destroy tmux session
    tmux kill-session -t ajet_session

    ```
```

- Warning: NEVER USE `tmux kill-server`! That is suicide, it will kill ALL tmux sessions on the server!


## Warning

- You must not edit `research_config.jsonc` in any circumstances!
- when you see **KeyboardInterrupt**, that means I'm **angry** that you ignore **terrible errors** printed in console and let experiment resume and waste time.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.
- Do not use `sleep` ! use `tmux_wait.py` instead.