# agent.py code from earlier answer
from __future__ import annotations
from typing import Dict, Any, List
import yaml
from mcp_clients import MCPRegistry, COMMON, ATLAS
import abilities

class LangGraphAgent:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        self.registry = MCPRegistry()
        self._register_abilities()

    def _register_abilities(self):
        # COMMON
        self.registry.register(COMMON, "accept_payload", abilities.accept_payload)
        self.registry.register(COMMON, "parse_request_text", abilities.parse_request_text)
        self.registry.register(COMMON, "normalize_fields", abilities.normalize_fields)
        self.registry.register(COMMON, "add_flags_calculations", abilities.add_flags_calculations)
        self.registry.register(COMMON, "store_answer", abilities.store_answer)
        self.registry.register(COMMON, "store_data", abilities.store_data)
        self.registry.register(COMMON, "solution_evaluation", abilities.solution_evaluation)
        self.registry.register(COMMON, "update_payload", abilities.update_payload)
        self.registry.register(COMMON, "response_generation", abilities.response_generation)
        self.registry.register(COMMON, "output_payload", abilities.output_payload)

        # ATLAS
        self.registry.register(ATLAS, "extract_entities", abilities.extract_entities)
        self.registry.register(ATLAS, "enrich_records", abilities.enrich_records)
        self.registry.register(ATLAS, "clarify_question", abilities.clarify_question)
        self.registry.register(ATLAS, "extract_answer", abilities.extract_answer)
        self.registry.register(ATLAS, "knowledge_base_search", abilities.knowledge_base_search)
        self.registry.register(ATLAS, "escalation_decision", abilities.escalation_decision)
        self.registry.register(ATLAS, "update_ticket", abilities.update_ticket)
        self.registry.register(ATLAS, "close_ticket", abilities.close_ticket)
        self.registry.register(ATLAS, "execute_api_calls", abilities.execute_api_calls)
        self.registry.register(ATLAS, "trigger_notifications", abilities.trigger_notifications)

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        state = dict(payload)  # state persistence
        log: List[str] = []
        log.append("Agent start: INTAKE -> COMPLETE")

        for stage in self.config["stages"]:
            name = stage["name"]
            mode = stage["mode"]
            abilities = stage.get("abilities", [])
            log.append(f"=== Stage: {name} (mode={mode}) ===")

            if mode == "deterministic":
                for ab in abilities:
                    server = ab["server"]
                    aname = ab["name"]
                    state = self.registry.call(server, aname, state, log)
            elif mode == "nondeterministic":
                # run evaluation first, then branch
                first = abilities[0]  # solution_evaluation
                state = self.registry.call(first["server"], first["name"], state, log)
                # Always call escalation_decision to record the decision
                second = abilities[1]  # escalation_decision
                state = self.registry.call(second["server"], second["name"], state, log)
                # update payload
                third = abilities[2]
                state = self.registry.call(third["server"], third["name"], state, log)
            else:
                log.append(f"Unknown mode for stage {name}; skipping.")

        state["_logs"] = log
        return state
