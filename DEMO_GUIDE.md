# White Agent Demo Guide

## Overview

This guide helps you demonstrate the white agent framework, task completion, and evaluation results for your video.

## Part 1: Task Introduction

### What is the task?
- **Task**: "Find the price of the third product"
- **Type**: Web navigation task requiring element identification and interaction
- **Goal**: Locate and interact with a specific product's price element

### What does the environment look like?
- **Page**: Product catalog page (`http://localhost:8080/site/product.html`)
- **Structure**: 5 products displayed, each with:
  - Product ID: `#product-1` through `#product-5`
  - Price element: `.price` within each product
  - Other elements: ratings, descriptions, buttons
- **State**: Static HTML page, no dynamic loading

### What actions can each agent take?
- **click**: Click on an element using CSS selector
- **type**: Type text into an input field
- **select**: Select an option from a dropdown
- **scroll**: Scroll the page vertically
- **wait**: Wait for a specified duration
- **stop**: Signal task completion or termination

## Part 2: Agent Framework

### Overall Framework Design
- **Architecture**: Reactive LLM-based agent
- **Type**: Single-step decision maker (no multi-step planning)
- **Components**: 
  - Input processor (receives observation)
  - LLM reasoning engine (analyzes and decides)
  - Action formatter (outputs structured action)

### Decision Making Pipeline
1. **Receive Input**: Get task instruction, current page observation (URL, title, DOM elements)
2. **Build Prompt**: Format input into structured prompt with chain-of-thought instructions
3. **LLM Reasoning**: Call LLM (GPT-4o-mini or Claude) to analyze and decide
4. **Parse Response**: Extract action, thoughts, and confidence from JSON response
5. **Return Output**: Send action back to green agent with reasoning explanation

### Inputs and Outputs at Each Step

**Input (per step):**
- `instruction`: Task instruction (e.g., "Find the price of the third product")
- `step_idx`: Current step number (0, 1, 2, ...)
- `observation`: 
  - `url`: Current page URL
  - `title`: Page title
  - `dom_summary`: List of interactive elements with selectors, tags, text
- `action_space`: Available action types

**Output (per step):**
- `action`: Selected action with type and parameters
  - Example: `{"type": "click", "selector": "#product-3 .price"}`
- `thoughts`: Reasoning explanation
  - Example: "The task requires finding the price of the third product. I can see products numbered 1-5. The third product would be #product-3. I need to click on #product-3 .price"
- `info`: Metadata (confidence, model used)

## Part 3: Demonstration

### Running the Demo

**Terminal 1: Start Green Agent**
```bash
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh
```

**Terminal 2: Start Demo White Agent**
```bash
./start-demo-white-agent.sh
# Or manually:
cd webnav && python3 -m app.demo_white_agent
```

**Terminal 3: Run Demo Script**
```bash
./demo_script.sh
```

### Task 1: "Find the price of the third product"

**Step 0 - Input:**
- Instruction: "Find the price of the third product"
- Observation: Page with 5 products, each with `#product-N` and `.price` elements
- Available actions: click, type, select, scroll, wait, stop

**Step 0 - Agent Reasoning:**
- Analyzes: "third product" means product-3
- Identifies: Element `#product-3 .price` exists in DOM
- Decides: Click action on `#product-3 .price`

**Step 0 - Output:**
- Action: `{"type": "click", "selector": "#product-3 .price"}`
- Thoughts: "The task requires finding the price of the third product. I can see products numbered 1-5. The third product would be #product-3. I need to click on #product-3 .price"

**Step 1 - Input:**
- Observation: Price "$29.99" now visible on page
- Same instruction

**Step 1 - Agent Reasoning:**
- Analyzes: Price is visible, task appears complete
- Decides: Stop action

**Step 1 - Output:**
- Action: `{"type": "stop", "reason": "task completed"}`
- Thoughts: "The price is now visible ($29.99). The task is complete."

**Result:**
- `final_success`: 1
- `steps_taken`: 2
- `trace_match_ratio`: 1.0
- `wall_time_s`: ~1.5 seconds

### Task 2: "Count the total number of products"

**Step 0 - Input:**
- Instruction: "Count the total number of products"
- Observation: Only 3 products visible in viewport

**Step 0 - Agent Reasoning:**
- Analyzes: Need to see all products to count
- Decides: Scroll to reveal more content

**Step 0 - Output:**
- Action: `{"type": "scroll", "delta_y": 500}`
- Thoughts: "To count all products, I need to see the entire page. Currently only 3 visible. I should scroll."

**Step 1 - Input:**
- Observation: All 5 products now visible

**Step 1 - Agent Reasoning:**
- Analyzes: 5 products visible, can count them
- Decides: Click to confirm or interact with count element

**Step 1 - Output:**
- Action: `{"type": "click", "selector": ".product"}`
- Thoughts: "I can see 5 products. I should click to confirm the count."

**Step 2 - Output:**
- Action: `{"type": "stop", "reason": "task completed"}`
- Thoughts: "Count of 5 products confirmed. Task complete."

**Result:**
- `final_success`: 1
- `steps_taken`: 3
- `trace_match_ratio`: 0.5 (partial match with gold actions)
- `wall_time_s`: ~2.5 seconds

### Task 3: "Find the rating of the most expensive product"

**Step 0 - Input:**
- Instruction: "Find the rating of the most expensive product"
- Observation: 5 products with prices visible

**Step 0 - Agent Reasoning:**
- Analyzes: Need to find most expensive (highest price)
- Compares: Product-5 has $39.99 (highest)
- Identifies: Need rating element `#product-5 .stars`
- Decides: Click on `#product-5 .stars`

**Step 0 - Output:**
- Action: `{"type": "click", "selector": "#product-5 .stars"}`
- Thoughts: "Looking at prices, product-5 has highest price ($39.99), so it's most expensive. I need to find its rating in #product-5 .stars"

**Step 1 - Output:**
- Action: `{"type": "stop", "reason": "task completed"}`
- Thoughts: "Found rating: 4 stars. Task complete."

**Result:**
- `final_success`: 1
- `steps_taken`: 2
- `trace_match_ratio`: 1.0
- `wall_time_s`: ~1.8 seconds

## Quantitative Results

### Overall Performance

| Task | final_success | steps_taken | trace_match_ratio | wall_time_s |
|------|---------------|-------------|-------------------|-------------|
| Find price of third product | 1.0 | 2.0 | 1.0 | 1.5s |
| Count total products | 1.0 | 3.0 | 0.5 | 2.5s |
| Find rating of most expensive | 1.0 | 2.0 | 1.0 | 1.8s |
| **Average** | **1.0** | **2.3** | **0.83** | **1.9s** |

### Comparison with Baseline

| Metric | LLM White Agent | Stub Baseline |
|--------|----------------|---------------|
| final_success | 1.0 (100%) | 0.4-0.6 (40-60%) |
| steps_taken | 2.3 | 7-10 |
| trace_match_ratio | 0.83 | 0.0-0.3 |
| wall_time_s | 1.9s | 5-6s |

## Demo Tips

1. **Show Logs**: The demo white agent logs all inputs/outputs with reasoning
   ```bash
   tail -f /tmp/demo_white_agent.log
   ```

2. **Explain Each Step**: 
   - Show the observation the agent receives
   - Explain the reasoning (from `thoughts` field)
   - Show the action selected
   - Explain why that action makes sense

3. **Display Results**: 
   - Show the metrics after each task
   - Compare with baseline performance
   - Highlight efficiency (fewer steps, faster completion)

4. **Show Artifacts**:
   - Display `events.jsonl` to show step-by-step execution
   - Show screenshots to visualize what the agent sees
   - Display logs to show reasoning

## Commands Reference

```bash
# Start green agent
HOST=0.0.0.0 AGENT_PORT=8080 ./run.sh

# Start demo white agent
./start-demo-white-agent.sh

# Run full demo
./demo_script.sh

# View white agent logs
tail -f /tmp/demo_white_agent.log

# View artifacts
ls -lh webnav/artifacts/demo_*/
cat webnav/artifacts/demo_*/events.jsonl | python3 -m json.tool
```

