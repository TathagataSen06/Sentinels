import json
import logging
import sys
from pathlib import Path

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction

# Add paths for Protobuf and Core modules
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent / "schemas"))
sys.path.append(str(Path(__file__).resolve().parent.parent))

import sensor_event_pb2
from core.rule_engine import RuleEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NormalizeProtobufEvent(MapFunction):
    def __init__(self):
        # We initialize the rule engine here so it loads the YAMLs into memory
        rules_dir = str(Path(__file__).resolve().parent.parent / "rules")
        self.rule_engine = RuleEngine(rules_dir)

    def map(self, value):
        try:
            pb_event = sensor_event_pb2.SensorEvent()
            pb_event.ParseFromString(value.encode('utf-8'))
            
            payload = json.loads(pb_event.payload_json)
            attacker_ip = payload.get("src_ip", "unknown")
            
            normalized = {
                "event_id": pb_event.event_id,
                "sensor_uuid": pb_event.sensor_uuid,
                "tenant_id": pb_event.tenant_id,
                "event_type": pb_event.event_type,
                "attacker_ip": attacker_ip,
                "raw_payload": payload,
                "sigma_rules": [],
                "mitre_tags": [],
                "severity": "low"
            }
            
            # Evaluate against Sigma Rules
            triggered_rules = self.rule_engine.evaluate(normalized)
            if triggered_rules:
                max_risk = 0
                max_conf = 0
                
                for rule in triggered_rules:
                    normalized["sigma_rules"].append(rule.title)
                    normalized["mitre_tags"].extend(rule.mitre.tactic)
                    normalized["mitre_tags"].extend(rule.mitre.technique)
                    if rule.mitre.sub_technique:
                        normalized["mitre_tags"].extend(rule.mitre.sub_technique)
                    
                    if rule.risk_score > max_risk:
                        max_risk = rule.risk_score
                    if rule.confidence > max_conf:
                        max_conf = rule.confidence
                        
                normalized["risk_score"] = max_risk
                normalized["confidence"] = max_conf
                # De-duplicate tags
                normalized["mitre_tags"] = list(set(normalized["mitre_tags"]))
            
            return json.dumps(normalized)
        except Exception as e:
            logger.error(f"Failed to normalize protobuf: {e}")
            return None

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)

    kafka_props = {'bootstrap.servers': 'localhost:9092', 'group.id': 'flink_ingester_group'}
    
    # Consume Raw Protobuf Telemetry
    kafka_consumer = FlinkKafkaConsumer(
        topics='sensor-events',
        deserialization_schema=SimpleStringSchema(), # Using simple schema for MVP structure
        properties=kafka_props
    )
    
    stream = env.add_source(kafka_consumer)
    
    # Normalize
    normalized_stream = stream.map(NormalizeProtobufEvent(), output_type=Types.STRING())
    
    # Publish to Normalized Topic
    kafka_producer = FlinkKafkaProducer(
        topic='sentinels-normalized',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'localhost:9092'}
    )
    
    normalized_stream.add_sink(kafka_producer)
    
    env.execute("Sentinels_Ingester_Job")

if __name__ == '__main__':
    main()
