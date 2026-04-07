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
# confirm execution
python -m rl_auto_research.opencode_runner leader --research-topic="research_topic/example_02_kl_abl.md" --resume --skip-permissions

