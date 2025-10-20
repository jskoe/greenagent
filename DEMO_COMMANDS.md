# WebNav Green Agent - Quick Demo Commands

## 🚀 **Start the Service**
```bash
cd webnav
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🌐 **Web Interfaces**
- **Product Catalog**: http://localhost:8000/site/product.html
- **Interactive Dashboard**: http://localhost:8000/site/dashboard.html
- **API Documentation**: http://localhost:8000/docs
- **Service Info**: http://localhost:8000/

## 🎯 **Task Demonstrations**

### **Task 1: Price Extraction**
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_001"}'
```
**Expected**: `$299.99` (Bluetooth Speaker price)

### **Task 2: Rating Analysis**
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_002"}'
```
**Expected**: `★★★★☆` (Tablet rating)

### **Task 3: Product Counting**
```bash
curl -X POST http://localhost:8000/task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"task_003"}'
```
**Expected**: `5` (Total product count)

## 🔧 **Utility Commands**

### **Health Check**
```bash
curl http://localhost:8000/health
```

### **Reset Controller**
```bash
curl -X POST http://localhost:8000/reset
```

### **View Artifacts**
```bash
ls runs/task_001/
cat runs/task_001/report.json
```

## 🎬 **Automated Demo**
```bash
./demo.sh
```

## 📊 **Key Evaluation Metrics**

Each task returns:
- **success**: `true`/`false`
- **metrics**: `duration_sec`, `step_count`, `on_task_domain`
- **evidence**: `matched_text`, `final_url`, `screenshot`
- **logs**: Step-by-step action trace

## 🎯 **Evaluation Criteria**

The Green Agent assesses:
1. **Correctness**: Right information extracted
2. **Accuracy**: Proper CSS selectors and regex patterns
3. **Reliability**: Consistent results across runs
4. **Efficiency**: Performance within limits
5. **Compliance**: Domain and rule adherence
