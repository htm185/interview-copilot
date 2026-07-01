from typing import Dict, Any
import time

def basic_scores(output: Dict[str, Any], started_at: float, pii_flag: bool, schema_ok: bool) -> Dict[str, Any]:
    latency_ms = max(1, int((time.time() - started_at) * 1000))

    faithfulness_score = 1.0 if schema_ok else 0.4
    relevance_score = 0.5 if "limited evidence" in output.get("final_report", "").lower() else 0.9
    return {
        "schema_pass": schema_ok,
        "faithfulness_score": faithfulness_score,
        "relevance_score": relevance_score,
        "pii_leak_flag": pii_flag,
        "latency_ms": latency_ms,
        "token_cost_est": None
    }