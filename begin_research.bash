#!/bin/bash

# clone code
git clone https://github.com/modelscope/AgentJet.git codebase/agentjet


## plan -> human review -> experiment (human-in-the-loop)
# alpha-rl-new-planning      = python -m alpha_auto_research.opencode_runner leader --skip-permissions --only-run-planning
# alpha-rl-resume-planning   = python -m alpha_auto_research.opencode_runner leader --skip-permissions --resume --only-run-planning
# alpha-rl-begin-experiments = python -m alpha_auto_research.opencode_runner leader --skip-permissions --resume
# alpha-rl-resume-experiment = python -m alpha_auto_research.opencode_runner leader --skip-permissions --resume

## plan -> experiment (human-less)
# alpha-rl-new-research-no-human = python -m alpha_auto_research.opencode_runner leader --skip-permissions --no-human-in-the-loop

## topic 01
# plan first
alpha-rl-new-planning \
    --research-topic="research_topic/example_01_content_madness_detect.md"
# confirm execution
alpha-rl-begin-experiments \
    --research-topic="research_topic/example_01_content_madness_detect.md" \
    --resume-instruction="permission granted, begin research"



## topic 02
# plan first
alpha-rl-new-planning \
    --research-topic="research_topic/example_02_kl_abl.md"
# polish plan
alpha-rl-resume-planning \
    --research-topic="research_topic/example_02_kl_abl.md" \
    --resume-instruction="study kl_type first, ahead of kl coef, try again"
# confirm execution
alpha-rl-begin-experiments \
    --research-topic="research_topic/example_02_kl_abl.md" \
    --resume-instruction="permission granted, begin research"

# resume from broken (without context)
alpha-rl-new-planning \
    --research-topic="research_topic/example_02_kl_abl.md" \
    --resume-instruction="Look at what you have done!!!  Yaml is all wrong, refer to agentjet/ajet/default_config/ajet_default.yaml, do not use actor_rollout_ref"



## topic 02-resume from blueprints
# resume from broken (without context)
alpha-rl-new-planning \
    --research-topic="research_topic/example_02_kl_abl.md" \
    --resume-instruction="Double check planning, polish current plan."



## topic 03
# plan first
alpha-rl-new-planning \
    --research-topic="research_topic/example_03_appworld.md"
# polish plan
alpha-rl-resume-planning \
    --research-topic="research_topic/example_03_appworld.md" \
    --resume-instruction="polish your plan"
# confirm execution
alpha-rl-begin-experiments \
    --research-topic="research_topic/example_03_appworld.md" \
    --resume-instruction="permission granted, begin research"

# resume from broken (without context)
alpha-rl-new-planning \
    --research-topic="research_topic/example_03_appworld.md" \
    --resume-instruction="Double check planning, revise it."
