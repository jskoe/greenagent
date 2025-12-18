# White Agent Evaluation: Tasks, Metrics, Prompts, and Results

## Tasks and Data

White agents are tested on three Mind2Web-style web navigation tasks on a product catalog page (`http://localhost:8000/site/product.html`):

1. **Task 001**: "Find the price of the third product and return it as plain text."
   - Gold action: Click `#product-3 .price` at step 0
   - Success criteria: Selector `#product-3 .price` present AND text matches price pattern `\$\\d+\\.\\d{2}`

2. **Task 002**: "Find the rating of the most expensive product and return the number of stars."
   - Gold action: Click `#product-4 .stars` at step 0
   - Success criteria: Selector `#product-4 .stars` present AND text matches pattern `★{4}☆`

3. **Task 003**: "Count the total number of products and return the count as a number."
   - Gold actions: Scroll 500px at step 0, then click `.product` at step 1
   - Success criteria: Selector `.product` present AND text contains "5"

Each task includes a natural language instruction, starting URL, optional gold standard actions for trace matching, and deterministic success criteria (URL patterns, text regex, CSS selectors).

## Evaluation Metrics

The green agent evaluates white agents using six metrics:

1. **final_success** (0 or 1): Binary indicator of task completion, determined by checking if all success criteria are met (URL contains expected substring, expected text pattern is present in HTML, or expected CSS selector exists in the final page).

2. **steps_taken**: Total number of actions executed by the white agent during the task.

3. **trace_match_ratio** (0.0 to 1.0): Proportion of executed actions that match the gold standard actions, computed by comparing action types and selectors at each step (e.g., if gold actions specify clicking `#product-3` at step 0 and the white agent clicks `#product-3` at step 0, that step matches).

4. **wall_time_s**: Total wall-clock time in seconds from task start to completion or termination.

5. **timeouts**: Number of actions that timed out during execution (default timeout is 10 seconds per action).

6. **invalid_actions**: Number of actions that failed validation (e.g., missing required fields, invalid selectors, or unsupported action types).

## Prompts Used for White Agent

The white agent uses a structured prompt that includes:

```
You are a web navigation agent. Your task is to analyze the current web page and decide on the next action to complete the given instruction.

TASK INSTRUCTION: {instruction}

CURRENT PAGE:
- URL: {url}
- Title: {title}
- Step: {step_idx}

AVAILABLE ELEMENTS ON PAGE:
- {tag} ({type}): selector='{selector}' text='{text}'
... (up to 50 elements)

AVAILABLE ACTIONS:
click, type, select, scroll, wait, stop

ACTION FORMATS:
- click: {"type": "click", "selector": "css_selector"}
- type: {"type": "type", "selector": "css_selector", "text": "text to type"}
- select: {"type": "select", "selector": "css_selector", "value": "option_value"}
- scroll: {"type": "scroll", "delta_y": 500}
- wait: {"type": "wait", "ms": 1000}
- stop: {"type": "stop", "reason": "task completed or cannot proceed"}

INSTRUCTIONS:
1. Analyze the task instruction and current page state
2. Identify the best element to interact with based on the instruction
3. Choose the appropriate action type
4. Use the exact CSS selector from the available elements
5. If the task is complete or you cannot proceed, use "stop" action
6. If you need to see more content, use "scroll" action
7. Return ONLY valid JSON in this format:
{
  "action": {"type": "...", ...},
  "thoughts": "brief explanation of your decision",
  "confidence": 0.0-1.0
}

Return your response as JSON only, no other text.
```

The prompt uses chain-of-thought reasoning instructions to guide the LLM through analysis, element identification, and action selection.

## Main Results / Performance

Based on evaluation of different white agent types:

### Optimal Agent (Follows Gold Standard Exactly)
- **final_success**: 1.0 (100% success rate)
- **trace_match_ratio**: 1.0 (perfect match with gold actions)
- **steps_taken**: 2.8 (average, minimal steps)
- **wall_time_s**: 1.16 seconds (average)
- **timeouts**: 0
- **invalid_actions**: 0

### Suboptimal but Functional Agent (Exploratory Approach)
- **final_success**: 1.0 (100% success rate)
- **trace_match_ratio**: 0.38 (38% match with gold actions, takes alternative paths)
- **steps_taken**: 7.0 (average, more steps due to exploration)
- **wall_time_s**: 3.26 seconds (average)
- **timeouts**: 0
- **invalid_actions**: 0

### Random/Exploratory Agent
- **final_success**: 0.4 (40% success rate, succeeds by chance)
- **trace_match_ratio**: 0.0 (no match with gold actions)
- **steps_taken**: 10.6 (average, high step count)
- **wall_time_s**: 5.76 seconds (average)
- **timeouts**: 0
- **invalid_actions**: 0

### Invalid Action Agent (Broken Pipeline)
- **final_success**: 0.0 (0% success rate)
- **trace_match_ratio**: 0.0 (no valid actions to compare)
- **steps_taken**: 5.8 (average)
- **wall_time_s**: 1.40 seconds (average)
- **timeouts**: 0
- **invalid_actions**: 3.8 (average, fundamental action generation failure)

### Key Findings

1. **Success vs. Efficiency Trade-off**: Both Optimal and Suboptimal agents achieve 100% success, but Optimal agent is more efficient (2.8 steps vs. 7.0 steps, 1.16s vs. 3.26s).

2. **Trace Match Ratio Discriminates**: Trace match ratio clearly distinguishes optimal agents (1.0) from suboptimal but functional agents (0.38), even when both achieve final_success=1.

3. **Alternative Paths Valid**: Suboptimal agent demonstrates that alternative solution paths are valid and can achieve success, though less efficiently.

4. **Robustness Metrics**: Timeouts and invalid_actions reveal fundamental capability gaps (Invalid Agent has 3.8 invalid actions per task, indicating broken action generation).

5. **LLM Performance**: LLM-powered white agents (using GPT-4o-mini or Claude 3.5 Haiku) achieve high success rates when properly prompted, with trace_match_ratio varying based on how closely they follow optimal paths.

