# 🚀 Kasparro Agentic FB Ads Performance Analyzer

## 📌 Project Overview
Kasparro Agentic FB Ads Performance Analyzer is an intelligent multi-agent system designed to autonomously analyze Facebook advertising data, extract meaningful performance insights, validate hypotheses using data-driven evaluation, and provide actionable creative recommendations. It follows an agentic workflow model that mimics real-world marketing analytics decision-making.

---

## ⚙️ Technology Stack
**Programming Language**  
- Python 3.10+

**Data Processing & Computation**  
- Pandas, NumPy

**Reporting & Visualization**  
- ReportLab (PDF and Report Generation)

**LLM Integration**  
- Custom LangChain-style architecture  
- Gemini LLM API

**System Utilities**  
- JSON-based agent interfacing  
- Rich for CLI enhancements  
- Structured Logging

---

## 🧠 Agent Architecture & Workflow

```
User Query
   ↓
1️⃣ Planner Agent — Interprets the query and defines the agent sequence  
   ↓
2️⃣ Data Agent — Retrieves and aggregates advertising performance data  
   ↓
3️⃣ Insight Agent — Generates patterns, trends, and hypotheses  
   ↓
4️⃣ Evaluator Agent — Validates insights using data-driven checks  
   ↓
5️⃣ Creative Agent — Suggests campaign improvements and new creative ideas  
   ↓
📄 Final Report — Compiled into marketer-friendly markdown report  
```

---

## 🛠 Setup & Installation

### 🔹 Clone Repository
```bash
git clone https://github.com/DarshniSanjaikumar/kasparro-agentic-fb-analyst-Darshni-Sanjaikumar.git
cd kasparro-agentic-fb-analyst-Darshni-Sanjaikumar
```

### 🔹 Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate        # Windows
```

### 🔹 Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 📂 Folder Structure
```
src/
 ├── agents/
 │   ├── planner.py
 │   ├── data_agent.py
 │   ├── insight_agent.py
 │   ├── evaluator_agent.py
 │   └── creative_agent.py
 ├── utils/
 │   ├── data_utils.py
 │   ├── logging_utils.py
 │   └── llm.py
 ├── orchestrator/
 │   └── run.py
 └── prompts/
     ├── planner_prompt.md
     ├── data_summary_prompt.md
     ├── insight_prompt.md
     ├── evaluator_prompt.md
     └── creative_prompt.md

reports/
 ├── Planner_output.json
 ├── Data_summary.json
 ├── Insight_output.json
 ├── Evaluator_output.json
 ├── Creative_output.json
 └── report.md
```

---

## ▶️ How to Run the Full Pipeline
```bash
python -m src.orchestrator.run "your query here"
```

This will:
✔ Process user query  
✔ Execute agents in the correct sequence using `agent_sequence`  
✔ Generate structured agent outputs (JSON)  
✔ Compile the final report in `reports/report.md`  

---

## 💬 Example Queries

| Query Type | Example |
|------------|---------|
| Performance Overview | *Give me CTR, ROAS, and spend for Men ComfortMax in the last 14 days.* |
| Root Cause Analysis | *Why did the ROAS decline last week for Men ComfortMax?* |
| Campaign Comparison | *Compare performance of Men ComfortMax and Women FlexFit.* |
| Hypothesis Validation | *Is creative fatigue reducing CTR for Men ComfortMax?* |
| Creative Optimization | *Recommend high-engagement ad creative variations.* |

---

## 📁 Output Artifacts

| File Name | Description |
|-----------|-------------|
| `Planner_output.json` | Agent plan and execution route |
| `Data_summary.json` | Processed dataset insights |
| `Insight_output.json` | Generated hypotheses and trend analysis |
| `Evaluator_output.json` | Hypothesis validation and statistical metrics |
| `Creative_output.json` | AI-assisted creative recommendations |
| `report.md` | Final compiled marketing report |

---

## 🧪 Evaluator Logic Overview
Evaluator Agent performs:
- Hypothesis validation using real data trends  
- ROAS/CTR consistency checks  
- Budget-performance correlation analysis  
- Creative fatigue detection  
- Performance fragmentation detection across campaigns  

---

## 📌 Strategic Recommendations (Sample)
✔ Standardize campaign naming conventions  
✔ Monitor ROAS post scaling efficiency  
✔ Refresh creatives when CTR shows progressive decline  
✔ Leverage CreativeAgent outputs for optimized messaging  
✔ Extend system to support automated performance alerts and scheduling  

---

📄 *Generated using Kasparro Agentic FB Ad Intelligence System*
