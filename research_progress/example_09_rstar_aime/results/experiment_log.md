# Experiment Log - example_09_rstar_aime

## Experiment Purpose
Train AIME math agent using swarm mode with Qwen3-14B model.

## Configuration
- **Model**: Qwen3-14B (at /mnt/data_cpfs/xielipeng.xlp/models/Qwen3-14B)
- **Algorithm**: GRPO
- **Batch Size**: 128
- **Num Repeat**: 8
- **GPUs**: 8
- **Swarm URL**: http://localhost:10086

## Training Command
```bash
export REMOTE_MODEL_PATH="/mnt/data_cpfs/xielipeng.xlp/models/Qwen3-14B"
cd /mnt/data_cpfs/qingxu.fu/alpha_auto_research/agentjet_codebase
source .venv/bin/activate
python -m tutorial.opencode_build_aime.agent_roll
```

## Experiment Timeline

### Start Time
Training started at: 2026-04-16 16:20

### Status Update
- 16:20: Training script started
- 16:21-16:26: Engine BOOTING (loading Qwen3-14B model - took ~5 minutes)
- 16:26: Engine ROLLING - evaluation at step 0 started

### Issues and Resolutions
(N/A)
