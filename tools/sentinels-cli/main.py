import argparse
import os
import sys

def create_plugin_scaffold(plugin_name: str):
    """
    Creates the boilerplate directory structure and python files for a new plugin.
    """
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "plugins", plugin_name)
    
    if os.path.exists(base_dir):
        print(f"Error: Plugin directory '{plugin_name}' already exists.")
        sys.exit(1)
        
    os.makedirs(base_dir)
    
    plugin_class_name = "".join([word.capitalize() for word in plugin_name.split("_")]) + "Plugin"
    
    main_file_content = f'''from typing import Dict, Any
from libs.sdk.plugin_base import SentinelsPlugin, PluginEvent
import logging

logger = logging.getLogger(__name__)

class {plugin_class_name}(SentinelsPlugin):
    """
    Auto-generated Sentinels Plugin for {plugin_name}
    """
    
    def init(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.port = config.get("port", 8080)
        self.is_running = False
        logger.info(f"Initialized {plugin_class_name} on port {{self.port}}")

    def start(self) -> None:
        self.is_running = True
        logger.info(f"Starting {plugin_class_name}...")
        # TODO: Implement socket binding and listening logic here
        
        # Example of yielding an event
        # yield PluginEvent(
        #     plugin_name="{plugin_name}",
        #     source_ip="192.168.1.100",
        #     protocol="tcp",
        #     payload={{"action": "connection_attempt"}}
        # )

    def stop(self) -> None:
        self.is_running = False
        logger.info(f"Stopping {plugin_class_name}...")
        # TODO: Implement graceful shutdown logic here

    def health_check(self) -> bool:
        return self.is_running
'''
    
    with open(os.path.join(base_dir, f"{plugin_name}_plugin.py"), "w") as f:
        f.write(main_file_content)
        
    with open(os.path.join(base_dir, "__init__.py"), "w") as f:
        f.write(f"from .{plugin_name}_plugin import {plugin_class_name}\n")
        
    with open(os.path.join(base_dir, "requirements.txt"), "w") as f:
        f.write("# Add plugin-specific dependencies here\n")

    print(f"Successfully generated plugin scaffolding at plugins/{plugin_name}")

def main():
    parser = argparse.ArgumentParser(description="Sentinels CLI - Developer Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # generate command
    generate_parser = subparsers.add_parser("generate", help="Generate code scaffolding")
    generate_parser.add_argument("resource", choices=["plugin"], help="Resource type to generate")
    generate_parser.add_argument("--name", required=True, help="Name of the plugin (e.g., mysql, fake_ssh)")

    args = parser.parse_args()

    if args.command == "generate":
        if args.resource == "plugin":
            create_plugin_scaffold(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
