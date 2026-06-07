import pytest
import json
import os
import sys
from pathlib import Path

# Setup paths to import core modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from core.rule_engine import RuleEngine

@pytest.fixture
def rule_engine():
    # Load rules from the actual rules directory
    rules_dir = str(Path(__file__).resolve().parent.parent / "rules")
    return RuleEngine(rules_dir)

def test_rule_loading_and_validation(rule_engine):
    # Ensure rules were parsed and validated by Pydantic successfully
    assert len(rule_engine.rules) > 0
    # Check if the specific SSH rule exists
    ssh_rule = next((r for r in rule_engine.rules if str(r.id) == "5c6a1e3b-9b4c-4e8d-a0f1-3c7d6e5f4a2b"), None)
    assert ssh_rule is not None
    assert ssh_rule.mitre.tactic == ["Credential Access"]
    assert ssh_rule.confidence == 90

def test_ssh_login_positive_fixture(rule_engine):
    fixture_path = str(Path(__file__).resolve().parent / "fixtures" / "ssh_brute_force_positive.json")
    with open(fixture_path, "r") as f:
        event = json.load(f)
        
    triggered_rules = rule_engine.evaluate(event)
    
    # We expect the rule to trigger because username contains "root"
    assert len(triggered_rules) == 1
    assert str(triggered_rules[0].id) == "5c6a1e3b-9b4c-4e8d-a0f1-3c7d6e5f4a2b"

def test_ssh_login_negative_fixture(rule_engine):
    fixture_path = str(Path(__file__).resolve().parent / "fixtures" / "ssh_brute_force_negative.json")
    with open(fixture_path, "r") as f:
        event = json.load(f)
        
    triggered_rules = rule_engine.evaluate(event)
    
    # We expect the rule NOT to trigger because username is "guest", and the selection requires "root"
    assert len(triggered_rules) == 0
