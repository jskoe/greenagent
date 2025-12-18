# Green Agent Demo Script

## Overview

This script demonstrates the green agent's evaluation capabilities, showing task introduction, evaluation of different white agents, reliability testing, and quantitative results.

## What to Say During Demo

### Part 1: Task Introduction (30 seconds)

**What is the task?**
> "The green agent evaluates white agents on web navigation tasks. We have three example tasks: finding the price of the third product, finding the rating of the most expensive product, and counting the total number of products. These tasks require the white agent to understand natural language instructions and interact with web elements."

**What does the environment look like?**
> "The environment is a product catalog page with 5 products. Each product has a price, rating, and description. Products are numbered from product-1 to product-5, and the page is a static HTML page served locally. This controlled environment allows us to test agent capabilities in a reproducible way."

**What actions can each agent take?**
> "White agents can take six types of actions: click to interact with elements, type to enter text, select to choose from dropdowns, scroll to see more content, wait to pause execution, and stop to signal task completion. The green agent orchestrates these actions by extracting observations, calling the white agent, executing actions, and judging outcomes."

### Part 2: Starting Services (15 seconds)

> "Let me start the green agent and a stub white agent. The green agent runs on port 8080, and the white agent runs on port 9000. They communicate via HTTP."

### Part 3: Demonstration - Evaluating Different White Agents (60 seconds)

**Example 1: Stub Agent Evaluation**
> "First, let's evaluate a stub white agent on the task 'Find the price of the third product'. The stub agent uses simple rule-based logic with keyword matching. As you can see from the results, the green agent evaluated this agent and returned metrics including final_success, steps_taken, trace_match_ratio, and wall_time_s."

**What the Green Agent Assesses:**
> "The green agent assesses five key dimensions. First, correctness through final_success, which checks if success criteria are met using URL patterns, text regex, and CSS selectors. Second, efficiency through steps_taken, counting how many actions were needed. Third, alignment through trace_match_ratio, comparing executed actions to the gold standard. Fourth, reliability through timeouts and invalid_actions, measuring robustness. Fifth, performance through wall_time_s, measuring execution speed."

### Part 4: Reliability Testing with Ground Truth (45 seconds)

**Test Case 1: Should Succeed**
> "To verify the green agent evaluates reliably, let's test it on a task that should succeed. We're asking the agent to click on product-3's price, which exists and matches our success criteria. The green agent correctly returns final_success equals 1, confirming it can identify successful task completion."

**Test Case 2: Should Fail**
> "Now let's test on a task that should fail. We're asking the agent to click on a non-existent element. The green agent correctly returns final_success equals 0, demonstrating it can reliably identify task failures. These ground truth tests confirm the green agent's evaluation is deterministic and accurate."

### Part 5: Quantitative Results on Benchmark (60 seconds)

**Running Benchmark Tasks:**
> "Let's run the green agent's evaluation on all three benchmark tasks. For each task, the green agent extracts observations, calls the white agent, executes actions, and computes metrics. As you can see from the results table, we get quantitative metrics for each task showing final_success, steps_taken, trace_match_ratio, and wall_time_s."

**Interpreting Results:**
> "These metrics tell us how well the white agent performed. final_success of 1 means the task was completed successfully. steps_taken shows efficiency - lower is better. trace_match_ratio shows how closely the agent followed the optimal path - 1.0 means perfect alignment. wall_time_s shows execution speed. Together, these metrics provide a comprehensive evaluation of white agent performance."

### Part 6: Artifacts and Evidence (30 seconds)

> "The green agent generates comprehensive artifacts for each evaluation, including events.jsonl with step-by-step execution logs, screenshots showing what the agent saw at each step, Playwright traces for replay, and consolidated logs. These artifacts enable debugging, analysis, and verification of the evaluation process."

## Key Talking Points

1. **Green Agent = Evaluator**: The green agent doesn't perform tasks itself - it evaluates how well white agents perform tasks.

2. **Deterministic Evaluation**: All evaluation is deterministic using exact matching rules (URL patterns, regex, CSS selectors), ensuring reproducible results.

3. **Comprehensive Metrics**: Six metrics provide a multi-dimensional view of white agent performance, not just success/failure.

4. **Reliability**: Ground truth tests confirm the green agent evaluates correctly and consistently.

5. **Artifacts**: Complete evidence is saved for every evaluation, enabling transparency and debugging.

## Timeline

- **0:00-0:30**: Task Introduction
- **0:30-0:45**: Starting Services
- **0:45-1:45**: Demonstration (evaluating different agents)
- **1:45-2:30**: Reliability Testing
- **2:30-3:30**: Quantitative Results
- **3:30-4:00**: Artifacts and Evidence

## Commands to Run

```bash
# Make script executable
chmod +x green_agent_demo.sh

# Run the demo
./green_agent_demo.sh
```

The script will:
1. Print task introduction
2. Start green agent and stub white agent
3. Run example evaluations
4. Run reliability tests
5. Run benchmark tasks
6. Display quantitative results
7. Show artifacts

## What to Show

1. **Terminal output**: Show the script running, displaying results in real-time
2. **Metrics table**: Highlight the quantitative results summary
3. **Artifacts**: Show the events.jsonl file to demonstrate step-by-step evaluation
4. **Logs**: Show green agent logs to demonstrate observation extraction and evaluation

