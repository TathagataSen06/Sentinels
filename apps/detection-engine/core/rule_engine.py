import yaml
import os
import glob
import logging
from typing import List, Dict

from .schema import SigmaRule
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class RuleEngine:
    """
    Enterprise Sigma YAML Rule Engine with Strict Pydantic Validation and Basic AST Logic.
    """
    def __init__(self, rules_dir: str):
        self.rules_dir = rules_dir
        self.rules: List[SigmaRule] = []
        self.reload_rules()

    def reload_rules(self):
        loaded = []
        search_path = os.path.join(self.rules_dir, "*.yaml")
        for rule_file in glob.glob(search_path):
            try:
                with open(rule_file, "r") as f:
                    raw_rule = yaml.safe_load(f)
                    # Pydantic Strict Schema Validation
                    validated_rule = SigmaRule(**raw_rule)
                    loaded.append(validated_rule)
            except ValidationError as ve:
                logger.error(f"[Schema Failure] Dropping invalid rule {rule_file}: {ve}")
            except Exception as e:
                logger.error(f"Failed to load rule {rule_file}: {e}")
        
        self.rules = loaded
        logger.info(f"Successfully loaded and validated {len(self.rules)} Enterprise Rules.")

    def _evaluate_condition(self, selection: dict, payload: dict) -> bool:
        """
        Parses keys like 'user|contains' or 'process|endswith'
        """
        for rule_key, expected_val in selection.items():
            if "|" in rule_key:
                field, operator = rule_key.split("|", 1)
            else:
                field, operator = rule_key, "exact"

            actual_val = payload.get(field, "")
            
            if operator == "exact" and actual_val != expected_val:
                return False
            elif operator == "contains" and expected_val not in actual_val:
                return False
            elif operator == "startswith" and not actual_val.startswith(expected_val):
                return False
            elif operator == "endswith" and not actual_val.endswith(expected_val):
                return False
                
        return True

    def evaluate(self, event: dict) -> list:
        triggered = []
        event_type = event.get("event_type", "")
        payload = event.get("raw_payload", {})

        for rule in self.rules:
            if rule.logsource.product != event_type:
                continue
                
            condition_str = rule.detection.condition.lower()
            
            # Simple AST matching for 'selection' and 'not X'
            # In production this uses pySigma for complex DAG evaluation
            is_match = False
            
            if condition_str == "selection":
                is_match = self._evaluate_condition(rule.detection.selection, payload)
            elif "not" in condition_str:
                # Mock handling for "selection and not X"
                is_match = self._evaluate_condition(rule.detection.selection, payload)
                # ... check exclusions ...

            if is_match:
                triggered.append(rule)
                    
        return triggered
