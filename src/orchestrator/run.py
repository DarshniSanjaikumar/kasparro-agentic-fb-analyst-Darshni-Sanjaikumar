import json
import os
from datetime import datetime
from src.agents.planner_agent import PlannerAgent
from src.agents.data_agent import DataAgent
from src.agents.insight_agent import InsightAgent
from src.agents.evaluator_agent import EvaluatorAgent
from src.agents.creative_agent import CreativeAgent
from src.utils.logging_utils import Logger, log_info, log_error


def save_output(filename, content, folder="reports"):
    """Save agent outputs to /reports folder."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    with open(path, "w", encoding="utf-8") as f:
        if filename.endswith(".json"):
            json.dump(content, f, indent=4)
        else:
            f.write(content)

    print(f"📁 Saved: {path}")
    return path


def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(r"""                                         
            ▄▄▄   ▄▄▄                                           
            ███ ▄███▀                                           
            ███████    ▀▀█▄ ▄█▀▀▀ ████▄  ▀▀█▄ ████▄ ████▄ ▄███▄ 
            ███▀███▄  ▄█▀██ ▀███▄ ██ ██ ▄█▀██ ██ ▀▀ ██ ▀▀ ██ ██ 
            ███  ▀███ ▀█▄██ ▄▄▄█▀ ████▀ ▀█▄██ ██    ██    ▀███▀ 
                                  ██                            
                                  ▀▀                            
          """)
    print(" 📊 Kasparro Agentic FB Ad Performance Analyzer")
    print(" 🤖 Multi-Agent Reasoning System")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def main():
    display_banner()
    logger = Logger(log_folder="logs")

    # User input
    user_query = input("\n💬 Enter your analysis request:\n> ").strip()

    outputs = {}

    try:
        # 🧠 Planner Agent
        logger.start("PlannerAgent")
        planner_agent = PlannerAgent()
        print("🧠 Planner Agent Initialized...")
        planner_output = planner_agent.run(user_query)
        logger.end(extra={"output_preview": planner_output})
        save_output("planner_output.json", planner_output)
        outputs["planner"] = planner_output

        # Determine agent execution flow
        agent_flow = planner_output.get("agent_flow", ["data_agent"])
        print(f"\n🔀 Pipeline: {agent_flow}")

        # 📊 Data Agent
        logger.start("DataAgent")
        data_agent = DataAgent()
        data_output = data_agent.run(planner_output)
        logger.end(extra={"output_preview": list(data_output.keys())})
        save_output("data_output.json", data_output)
        outputs["data"] = data_output

        insight_output, eval_output, creative_output = None, None, None

        # 🔁 Process remaining agents sequentially
        for agent in agent_flow[1:]:
            
            if agent == "insight_agent":
                logger.start("InsightAgent")
                insight_agent = InsightAgent()
                insight_output = insight_agent.run(
                    data_agent_output=data_output,
                    objective=planner_output.get("objective")
                )
                logger.end(extra={"hypotheses_count": len(insight_output) if insight_output else 0})
                save_output("insights.json", insight_output)
                outputs["insight"] = insight_output

            elif agent == "evaluator_agent":
                if not insight_output:
                    log_error("EvaluatorAgent skipped — No insights to evaluate.")
                    continue
                logger.start("EvaluatorAgent")
                evaluator_agent = EvaluatorAgent()
                eval_output = evaluator_agent.run(
                    objective=planner_output.get("objective"),
                    data_agent_output=data_output,
                    insight_output=insight_output
                )
                logger.end(extra={"validated_hypotheses": len(eval_output) if eval_output else 0})
                save_output("evaluation.json", eval_output)
                outputs["evaluator"] = eval_output

            elif agent == "creative_agent":
                if not insight_output:
                    log_error("CreativeAgent skipped — No validated insights available.")
                    continue
                logger.start("CreativeAgent")
                creative_agent = CreativeAgent()
                creative_output = creative_agent.run(
                    objective=planner_output.get("objective"),
                    insight_output=insight_output,
                    data_agent_output=data_output
                )
                logger.end(extra={"recommendation_count": len(creative_output) if creative_output else 0})
                save_output("creatives.json", creative_output)
                outputs["creative"] = creative_output

        # 📝 Generate Final Report
        report_path = os.path.join("reports", "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# 📊 Facebook Ads Performance Analysis Report\n\n")
            f.write(f"🕒 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"💬 Query: {user_query}\n\n---\n")

            for agent_name, output in outputs.items():
                f.write(f"## 🔹 {agent_name.capitalize()} Output\n")
                f.write("```json\n")
                f.write(json.dumps(output, indent=4))
                f.write("\n```\n")

        save_output("final_complete_output.json", outputs)
        print("\n🎯 Analysis completed successfully!")

    except Exception as e:
        log_error(f"❌ Orchestrator failure: {e}")
        save_output("orchestrator_error.json", {"error": str(e)})


if __name__ == "__main__":
    main()