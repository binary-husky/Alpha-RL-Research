#!/bin/bash

# clone code
git clone https://github.com/modelscope/AgentJet.git codebase/agentjet





## topic 01
# plan first
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_01_content_madness_detect.md" --only-run-planning --skip-permissions
# confirm execution
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_01_content_madness_detect.md" --resume --skip-permissions

## topic 02
# plan first
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" --only-run-planning --skip-permissions
# polish plan
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" \
    --resume \
    --only-run-planning --skip-permissions \
    --resume-instruction="study kl_type first, ahead of kl coef, try again"
# confirm execution
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" --resume --resume-instruction="permission granted, begin research" --skip-permissions


# resume from broken (without context)
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" \
    --only-run-planning --skip-permissions \
    --resume-instruction="yaml is all wrong, refer to \`agentjet/ajet/default_config/ajet_default.yaml\`, do not use \`actor_rollout_ref\`"

python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" \
    --resume \
    --only-run-planning --skip-permissions \
    --resume-instruction="add --skip-check-avail-gpu"