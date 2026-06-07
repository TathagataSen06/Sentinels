import json
import logging
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction

# Note: PyFlink CEP library is experimental/limited in pure Python compared to Java.
# For this MVP representation, we implement a stateful keyed process function 
# that mimics CEP lateral movement detection.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LateralMovementDetector(MapFunction):
    """
    Mocking the Flink CEP logic within a simple MapFunction for demonstration.
    In production, this would use a KeyedProcessFunction with ValueState to track 
    timestamps of HTTP and SSH logins per attacker_ip.
    """
    def __init__(self):
        self.state_store = {} # Mock StateBackend

    def map(self, value):
        try:
            event = json.loads(value)
            attacker_ip = event.get("attacker_ip")
            event_type = event.get("event_type")
            
            if not attacker_ip or attacker_ip == "unknown":
                return None
                
            if attacker_ip not in self.state_store:
                self.state_store[attacker_ip] = set()
                
            self.state_store[attacker_ip].add(event_type)
            history = self.state_store[attacker_ip]
            
            # Complex Event Processing Rule: HTTP followed by SSH
            if "http.login.attempt" in history and "ssh.login.attempt" in history:
                incident = {
                    "incident_id": f"INC-{event['event_id']}",
                    "attacker_ip": attacker_ip,
                    "severity": "CRITICAL",
                    "mitre_tactic": "TA0008: Lateral Movement",
                    "description": "Multi-stage attack detected across HTTP and SSH honeypots."
                }
                
                # Clear state after detection to prevent alert fatigue
                self.state_store[attacker_ip] = set()
                return json.dumps(incident)
                
            return None
        except Exception as e:
            logger.error(f"Error in correlation: {e}")
            return None

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(4)

    kafka_props = {'bootstrap.servers': 'localhost:9092', 'group.id': 'flink_correlator_group'}
    
    # Consume Enriched Events
    kafka_consumer = FlinkKafkaConsumer(
        topics='sentinels-enriched',
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    stream = env.add_source(kafka_consumer)
    
    # Process CEP
    incident_stream = stream.map(LateralMovementDetector(), output_type=Types.STRING()).filter(lambda x: x is not None)
    
    # Publish to Incidents Topic
    kafka_producer = FlinkKafkaProducer(
        topic='sentinels-incidents',
        serialization_schema=SimpleStringSchema(),
        producer_config={'bootstrap.servers': 'localhost:9092'}
    )
    
    incident_stream.add_sink(kafka_producer)
    
    env.execute("Sentinels_CEP_Correlator_Job")

if __name__ == '__main__':
    main()
