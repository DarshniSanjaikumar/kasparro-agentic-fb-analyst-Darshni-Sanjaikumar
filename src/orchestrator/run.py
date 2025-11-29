# src/orchestrator/run.py
"""
Full orchestrator for the Kasparro Agentic FB Analyst pipeline.

Features:
- Instantiates a single LLM instance and injects it into agents
- Runs Planner -> Data -> Insight -> Evaluator -> Creative
- Saves: reports/insights.json, reports/creatives.json, reports/report.md
- Writes structured run log to logs/run_<timestamp>.json
- Prints concise colored console output
- Robust error handling and timing for each agent step
"""

import os
import sys
import json
import time
import traceback
from datetime import datetime
from typing import Any, Dict

# config parsing
import yaml

# Ensure repo-root relative behavior works when calling from project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)

# Local imports (match your project structure)
from src.utils.llm import LLM
from src.utils.data_utils import DataUtils
# If you prefer to use config_reader, you can modify this to import it instead.
# from src.utils.config_reader import load_config
DataUtils_instance = DataUtils("./data/cleaned_data.csv")
load_data = DataUtils_instance.load_data

from src.agents.planner import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent

# ---- Helpers ----

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def now_ts() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def pretty_print(msg: str, level: str = "info"):
    """
    Minimal pretty printing using ANSI colors.
    level -> info, success, warn, error
    """
    colors = {
        "info": "\033[94m",     # blue
        "success": "\033[92m",  # green
        "warn": "\033[93m",     # yellow
        "error": "\033[91m",    # red
    }
    end = "\033[0m"
    color = colors.get(level, colors["info"])
    print(f"{color}{msg}{end}")

def safe_write_json(path: str, data: Any):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def safe_read_yaml(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---- Orchestrator ----

def build_report_md(insights_validated, creatives, summary_meta) -> str:
    """
    Build a simple markdown report summarizing key findings.
    """
    lines = []
    lines.append(f"# Automated ROAS Analysis Report")
    lines.append("")
    lines.append(f"- **Run timestamp (UTC):** {summary_meta.get('run_timestamp')}")
    lines.append(f"- **User query:** {summary_meta.get('user_query')}")
    lines.append(f"- **Top ROAS drops (count):** {len(summary_meta.get('top_roas_drops', []))}")
    lines.append("")
    lines.append("## Validated Hypotheses (summary)")
    if not insights_validated:
        lines.append("No validated hypotheses found.")
    else:
        for h in insights_validated:
            hid = h.get("hypothesis_id", "N/A")
            validated = h.get("validated", False)
            conf = h.get("confidence", 0)
            notes = h.get("notes", "")
            lines.append(f"### {hid} — {'✅' if validated else '❌'} (confidence: {conf})")
            lines.append("")
            lines.append(f"- **Notes:** {notes}")
            lines.append("- **Evidence:**")
            ev = h.get("evidence", {})
            if ev:
                for k, v in ev.items():
                    lines.append(f"  - {k}: {v}")
            lines.append("")
    lines.append("## Creative Recommendations")
    if creatives:
        for c in creatives:
            lines.append(f"### Campaign: {c.get('campaign')}")
            for n in c.get("new_creatives", []):
                lines.append(f"- **Headline:** {n.get('headline')}")
                lines.append(f"  - Text: {n.get('text')}")
                lines.append(f"  - CTA: {n.get('cta')}")
                lines.append(f"  - Angle: {n.get('angle')}")
            lines.append("")
    else:
        lines.append("No creatives generated.")
    return "\n".join(lines)

def run_pipeline(user_query: str, config_path: str = "config/config.yaml"):
    run_start = time.perf_counter()
    ts = now_ts()
    run_id = f"run_{ts}"

    # Ensure directories exist
    ensure_dir("reports")
    ensure_dir("logs")

    # Prepare run log skeleton
    run_log = {
        "run_id": run_id,
        "run_timestamp": ts,
        "user_query": user_query,
        "agents": {},
        "errors": [],
        "summary": {}
    }

    try:
        pretty_print("Loading config...", "info")
        config = safe_read_yaml(config_path)

        # Instantiate single LLM instance
        pretty_print("Initializing LLM...", "info")
        try:
            llm_model = config.get("llm", {}).get("model", "llama-3.1-8b-instant")
        except Exception:
            llm_model = "llama-3.1-8b-instant"

        llm = LLM(model=llm_model)

        # Initialize agents
        planner = PlannerAgent(llm, prompt_path=config.get("prompts", {}).get("planner", "prompts/planner_prompt.md"))
        data_agent = DataAgent(config=config, llm=llm, prompt_path=config.get("prompts", {}).get("data_summary", "prompts/data_summary_agent.md"))
        insight_agent = InsightAgent(llm, prompt_path=config.get("prompts", {}).get("insight", "prompts/insight_prompt.md"))

        # Load raw DF for evaluator (the evaluator uses raw metrics to validate)
        pretty_print("Loading raw dataset for evaluator...", "info")
        from src.utils.data_utils import DataUtils

        utils = DataUtils(config["data"]["path"])
        df = utils.load_data()

        evaluator = EvaluatorAgent(df, llm=llm, prompt_path=config.get("prompts", {}).get("evaluator", "prompts/evaluator_prompt.md"))
        creative_agent = CreativeAgent(llm, prompt_path=config.get("prompts", {}).get("creative", "prompts/creative_prompt.md"))

        # 1) Planner
        pretty_print("Running PlannerAgent...", "info")
        t0 = time.perf_counter()
        plan = planner.run(user_query)
        t1 = time.perf_counter()
        run_log["agents"]["planner"] = {
            "duration_s": round(t1 - t0, 3),
            "output_summary": {
                "tasks": plan.get("tasks", []),
                "needs_creatives": plan.get("needs_creatives", False),
                "analysis_window_days": plan.get("analysis_window_days", None)
            }
        }
        pretty_print(f"Planner done — tasks: {plan.get('tasks', [])}", "success")

        # 2) Data agent
        pretty_print("Running DataAgent...", "info")
        t0 = time.perf_counter()
        data_summary = data_agent.run()
        t1 = time.perf_counter()
        run_log["agents"]["data_agent"] = {
            "duration_s": round(t1 - t0, 3),
            "top_roas_drops": data_summary.get("top_roas_drops", [])[:5],
            "low_ctr_campaign_count": len(data_summary.get("low_ctr_campaigns", []))
        }
        pretty_print("DataAgent done.", "success")

        # 3) Insight agent
        pretty_print("Running InsightAgent...", "info")
        t0 = time.perf_counter()
        insights = insight_agent.run(data_summary, user_query)
        t1 = time.perf_counter()
        run_log["agents"]["insight_agent"] = {
            "duration_s": round(t1 - t0, 3),
            "hypotheses_count": len(insights) if isinstance(insights, list) else 0
        }
        pretty_print(f"InsightAgent produced {len(insights)} hypothesis/hypotheses.", "success")

        # 4) Evaluator agent
        pretty_print("Running EvaluatorAgent...", "info")
        t0 = time.perf_counter()
        validated = evaluator.run(insights)
        t1 = time.perf_counter()
        run_log["agents"]["evaluator_agent"] = {
            "duration_s": round(t1 - t0, 3),
            "validated_count": len(validated)
        }
        pretty_print("EvaluatorAgent done.", "success")

        # 5) Creative agent (if planner says so OR if low-ctr list non-empty)
        creatives = None
        needs_creatives = bool(plan.get("needs_creatives", False))
        low_ctr_list = data_summary.get("low_ctr_campaigns", [])
        if needs_creatives or low_ctr_list:
            pretty_print("Running CreativeAgent...", "info")
            t0 = time.perf_counter()
            creatives = creative_agent.run(low_ctr_list)
            t1 = time.perf_counter()
            run_log["agents"]["creative_agent"] = {
                "duration_s": round(t1 - t0, 3),
                "generated_for": len(creatives)
            }
            pretty_print(f"CreativeAgent generated creatives for {len(creatives)} campaigns.", "success")
        else:
            pretty_print("Creative generation skipped (not requested and no low-CTR campaigns).", "warn")

        # Save artifacts
        pretty_print("Saving outputs to reports/ ...", "info")
        insights_path = os.path.join("reports", f"insights_{ts}.json")
        creatives_path = os.path.join("reports", f"creatives_{ts}.json")
        report_md_path = os.path.join("reports", f"report_{ts}.md")

        safe_write_json(insights_path, validated)
        if creatives is not None:
            safe_write_json(creatives_path, creatives)
        # Create the final markdown report
        report_md = build_report_md(validated, creatives, {
            "run_timestamp": ts,
            "user_query": user_query,
            "top_roas_drops": data_summary.get("top_roas_drops", [])
        })
        with open(report_md_path, "w", encoding="utf-8") as f:
            f.write(report_md)

        # Populate run summary
        run_log["summary"] = {
            "insights_path": insights_path,
            "creatives_path": creatives_path if creatives is not None else None,
            "report_md_path": report_md_path,
            "total_duration_s": round(time.perf_counter() - run_start, 3)
        }

        # Save run log
        run_log_path = os.path.join("logs", f"{run_id}.json")
        safe_write_json(run_log_path, run_log)

        pretty_print(f"Run complete. Artifacts saved to reports/ and logs/ ({run_id}).", "success")
        pretty_print(f"Insights file: {insights_path}", "info")
        if creatives is not None:
            pretty_print(f"Creatives file: {creatives_path}", "info")
        pretty_print(f"Report: {report_md_path}", "info")
        pretty_print(f"Run log: {run_log_path}", "info")

        return True

    except Exception as err:
        err_trace = traceback.format_exc()
        run_log["errors"].append({
            "error": str(err),
            "traceback": err_trace
        })
        # Ensure we still write the run log for debugging
        run_log_path = os.path.join("logs", f"{run_id}_error.json")
        safe_write_json(run_log_path, run_log)
        pretty_print("Pipeline failed — see logs for details.", "error")
        pretty_print(str(err), "error")
        return False

# ---- CLI ----
if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_q = " ".join(sys.argv[1:])
    else:
        user_q = "Analyze ROAS drop and propose creatives"

    cfg_path = "config/config.yaml"
    if not os.path.exists(cfg_path):
        pretty_print(f"Config file not found at {cfg_path}. Please add config/config.yaml", "error")
        sys.exit(1)

    success = run_pipeline(user_q, config_path=cfg_path)
    if success:
        sys.exit(0)
    else:
        sys.exit(2)
