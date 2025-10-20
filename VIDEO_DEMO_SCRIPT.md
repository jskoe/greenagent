# WebNav Green Agent Demo Video Script

## 🎬 **Video Structure: "Green Agent Evaluation in Action"**

### **📋 Pre-Demo Setup (30 seconds)**
- **Screen**: Show terminal with WebNav service running
- **Narration**: "Today I'll demonstrate WebNav, a Green Agent that evaluates White Agents performing web navigation tasks. Let me start the service..."

```bash
cd webnav
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## **🎯 Part 1: Task Introduction (2 minutes)**

### **What is the Task?**
- **Screen**: Show product catalog at `http://localhost:8000/site/product.html`
- **Narration**: "Our task environment is an e-commerce product catalog with 5 electronics products. Each product has a unique ID, price, rating, and features."

- **Screen**: Highlight products with mouse cursor
- **Narration**: "The White Agent's job is to extract specific information from this page using web navigation techniques."

### **What Does the Environment Look Like?**
- **Screen**: Show the beautiful product catalog UI
- **Narration**: "The environment is a modern, responsive web page with:
  - 5 products (headphones, smartwatch, speaker, tablet, mouse)
  - Prices ranging from $79.99 to $449.99
  - Star ratings (★★★★☆ format)
  - Product categories and features"

### **What Actions Can Each Agent Take?**
- **Screen**: Show API documentation at `http://localhost:8000/docs`
- **Narration**: "White Agents can:
  - Navigate to the start URL
  - Extract text using CSS selectors
  - Count elements on the page
  - Return structured data

The Green Agent evaluates these actions by:
  - Checking if the correct element was found
  - Validating the extracted text matches expected patterns
  - Verifying the agent stayed on the correct domain
  - Measuring execution time and step count"

---

## **🔍 Part 2: Demonstration (4 minutes)**

### **Test Case 1: Price Extraction Task**
- **Screen**: Terminal showing task execution
- **Narration**: "Let's start with Task 1: Find the price of the third product."

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```

- **Screen**: Show JSON response
- **Narration**: "The Green Agent evaluates:
  - ✅ **Correctness**: Found `$299.99` (Bluetooth Speaker price)
  - ✅ **Selector Accuracy**: Used `#product-3 .price` correctly
  - ✅ **Pattern Match**: Matched regex `\$\\d+\.\\d{2}`
  - ✅ **Domain Compliance**: Stayed on localhost:8000
  - ✅ **Performance**: Completed in 0.67 seconds with 5 steps"

### **Test Case 2: Rating Analysis Task**
- **Screen**: Execute task_002
- **Narration**: "Task 2: Find the rating of the most expensive product (the tablet)."

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_002"}'
```

- **Screen**: Show response with `★★★★☆`
- **Narration**: "Evaluation results:
  - ✅ **Correctness**: Found `★★★★☆` (4 stars + 1 empty star)
  - ✅ **Unicode Handling**: Properly matched star characters
  - ✅ **Target Accuracy**: Correctly identified most expensive product
  - ✅ **Pattern Match**: Matched regex `★{4}☆`"

### **Test Case 3: Element Counting Task**
- **Screen**: Execute task_003
- **Narration**: "Task 3: Count the total number of products."

```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_003"}'
```

- **Screen**: Show response with `5`
- **Narration**: "Evaluation results:
  - ✅ **Correctness**: Counted exactly 5 products
  - ✅ **Logic Accuracy**: Used element counting, not text extraction
  - ✅ **Selector Precision**: Used `.product` to count individual items
  - ✅ **Task Understanding**: Recognized 'count' instruction"

### **Test Case 4: Failure Scenario**
- **Screen**: Show dashboard at `http://localhost:8000/site/dashboard.html`
- **Narration**: "Let's see how the Green Agent handles different White Agent behaviors. The dashboard shows real-time evaluation metrics."

- **Screen**: Click "Execute Task" button multiple times
- **Narration**: "Notice how each execution:
  - Creates a fresh browser context (no state leakage)
  - Produces identical results (deterministic evaluation)
  - Saves complete artifacts for debugging"

---

## **📊 Part 3: Evaluation Criteria Deep Dive (2 minutes)**

### **What the Green Agent is Assessing**
- **Screen**: Show artifact files in `runs/task_001/`
- **Narration**: "The Green Agent evaluates multiple dimensions:

1. **Correctness**: Did the White Agent find the right information?
   - CSS selector exists in final HTML
   - Extracted text matches expected pattern

2. **Reliability**: Did the agent behave consistently?
   - Same task produces identical results
   - No browser context leakage

3. **Efficiency**: How well did the agent perform?
   - Execution time under limits
   - Step count within bounds

4. **Compliance**: Did the agent follow rules?
   - Stayed on expected domain
   - Used correct selectors"

### **Evidence Trail**
- **Screen**: Open `runs/task_001/report.json`
- **Narration**: "Every evaluation creates a complete evidence trail:
  - **Report**: Success/failure with metrics
  - **Screenshot**: Visual proof of final state
  - **HTML Snapshot**: DOM state for debugging
  - **Action Log**: Step-by-step execution trace"

---

## **🔬 Part 4: Design Notes (1.5 minutes)**

### **Test Case Generation**
- **Screen**: Show `data/tasks.json`
- **Narration**: "I designed these test cases to cover different evaluation scenarios:

1. **Text Extraction**: Tests basic DOM navigation and regex matching
2. **Pattern Recognition**: Tests Unicode handling and complex patterns  
3. **Element Counting**: Tests logical reasoning and selector usage

Each case targets specific failure modes:
- Wrong CSS selectors
- Incorrect regex patterns
- Domain navigation errors
- Performance issues"

### **Why These Cases Test Reliability**
- **Screen**: Show multiple task executions with identical results
- **Narration**: "These test cases are suitable because they:

1. **Cover Core Web Tasks**: Price extraction, rating analysis, counting
2. **Test Different Skills**: Text parsing, pattern matching, logic
3. **Include Edge Cases**: Unicode characters, complex selectors
4. **Enable Reproducibility**: Deterministic results every time
5. **Provide Clear Pass/Fail**: Binary success criteria with evidence"

### **Scalability for Real Agents**
- **Screen**: Show API endpoints
- **Narration**: "The Green Agent is designed to evaluate any White Agent that can:
- Make HTTP requests to our API
- Return structured JSON responses
- Handle CSS selectors and regex patterns

This makes it suitable for evaluating real web navigation agents in production environments."

---

## **🎯 Part 5: Live Demo Summary (30 seconds)**

- **Screen**: Run the enhanced demo script
- **Narration**: "Let me show you the complete evaluation pipeline in action..."

```bash
./demo.sh
```

- **Screen**: Watch the automated demo run
- **Narration**: "As you can see, the WebNav Green Agent provides:
- Deterministic evaluation of web navigation tasks
- Complete evidence trails for debugging
- Support for multiple task types
- Production-ready API for real agent integration

This demonstrates how Green Agents can reliably evaluate White Agents performing complex web tasks."

---

## **📝 Key Talking Points**

### **What Makes This Evaluation Reliable:**
1. **Isolated Browser Contexts** - No state leakage between evaluations
2. **Deterministic Judging** - CSS + regex validation, not subjective LLM evaluation
3. **Complete Artifacts** - Screenshots, HTML, logs for debugging
4. **Multiple Task Types** - Text extraction, pattern matching, counting
5. **Performance Metrics** - Duration, step count, domain compliance

### **Evaluation Criteria Demonstrated:**
- ✅ **Correctness**: Right information extracted
- ✅ **Accuracy**: Proper CSS selectors and regex patterns
- ✅ **Reliability**: Consistent results across runs
- ✅ **Efficiency**: Performance within limits
- ✅ **Compliance**: Domain and rule adherence

### **Production Readiness:**
- Clean API for external agent integration
- Comprehensive documentation and examples
- Artifact tracking for debugging and validation
- Scalable architecture for multiple task types

---

## **🎬 Video Production Notes**

### **Screen Recording Setup:**
- Terminal with dark theme for better visibility
- Browser windows for web interface demos
- Code editor for showing configuration files
- Split screen for simultaneous terminal/browser views

### **Narration Style:**
- Professional, clear, and enthusiastic
- Pause for viewers to read terminal output
- Highlight key points with cursor movements
- Use consistent terminology throughout

### **Timing:**
- Total video length: ~10 minutes
- Allow time for viewers to see results
- Include brief pauses between sections
- End with clear call-to-action for trying the demo
