# Kasparro Agentic FB Ads Analyst
## 🚀 Objective
An agentic AI system that analyzes Facebook ad performance, detects ROAS fluctuations, and generates creative improvement suggestions.

## 📂 Project Structure
```txt
kasparro-agentic-fb-analyst-yourname/
│   README.md
│   requirements.txt
│   run.py
│
├───config
│       config.yaml
│
├───data
│       README.md
│       synthetic_fb_ads_undergarments.csv
│
├───logs
├───prompts
│       creative_prompt.md
│       evaluator_prompt.md
│       insight_prompt.md
│       planner_prompt.md
│
├───reports
│       creatives.json
│       insights.json
│       report.md
│
├───src
│   ├───agents
│   │       creative_agent.py
│   │       data_agent.py
│   │       evaluator_agent.py
│   │       insight_agent.py
│   │       planner.py
│   │
│   ├───orchestrator
│   │       run.py
│   │
│   └───utils
│           config_reader.py
│           data_loader.py
│           logger.py
│           prompt_templates.py
│
└───tests
        test_data_agent.py
        test_evaluator.py


## ⚙️ Setup
```bash
pip install -r requirements.txt