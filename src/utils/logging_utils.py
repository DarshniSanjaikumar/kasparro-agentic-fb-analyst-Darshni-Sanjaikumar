import json
import os
import time
from datetime import datetime

class Logger:
    def __init__(self, log_folder="logs"):
        self.log_folder = log_folder
        os.makedirs(log_folder, exist_ok=True)

    def start(self, agent_name):
        self.start_time = time.time()
        self.agent_name = agent_name
        return {"agent": agent_name, "start_time": datetime.utcnow().isoformat()}

    def end(self, status="success", extra=None):
        duration = time.time() - self.start_time
        log_data = {
            "agent": self.agent_name,
            "status": status,
            "duration_sec": duration,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if extra:
            log_data.update(extra)

        self._write_log_file(log_data)
        return log_data

    def _write_log_file(self, data):
        filename = datetime.utcnow().strftime("%Y%m%d_%H%M%S") + ".json"
        filepath = os.path.join(self.log_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
