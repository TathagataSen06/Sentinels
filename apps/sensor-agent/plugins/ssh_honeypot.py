import asyncio
import asyncssh
import logging
import shlex
from .base import BasePlugin

logger = logging.getLogger(__name__)

class FakeShell(asyncssh.SSHServerProcess):
    def __init__(self, emit_callback, username):
        self.emit_callback = emit_callback
        self.username = username
        self.cwd = "/home/" + username
        
    def connection_made(self, process):
        self.process = process
        self.process.stdout.write(f"Welcome to Ubuntu 22.04.2 LTS (GNU/Linux 5.15.0-76-generic x86_64)\n\n")
        self.process.stdout.write(" * Documentation:  https://help.ubuntu.com\n")
        self.process.stdout.write(" * Management:     https://landscape.canonical.com\n")
        self.process.stdout.write(" * Support:        https://ubuntu.com/advantage\n\n")
        self.process.stdout.write("Last login: Wed Oct 11 08:32:11 2023 from 192.168.1.50\n")
        self.prompt()

    def prompt(self):
        self.process.stdout.write(f"{self.username}@prod-web-01:{self.cwd}$ ")

    def data_received(self, data, datatype):
        command = data.strip()
        if not command:
            self.prompt()
            return
            
        self.emit_callback("ssh.command.executed", {
            "username": self.username,
            "command": command
        })
        
        self.process.stdout.write("\n")
        
        # Fake command handling
        args = shlex.split(command)
        cmd = args[0]
        
        if cmd in ["exit", "logout"]:
            self.process.exit(0)
            return
        elif cmd == "pwd":
            self.process.stdout.write(f"{self.cwd}\n")
        elif cmd == "whoami":
            self.process.stdout.write(f"{self.username}\n")
        elif cmd == "ls":
            if self.cwd == "/":
                self.process.stdout.write("bin  boot  dev  etc  home  lib  lib64  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var\n")
            else:
                self.process.stdout.write("backup.tar.gz  config.yaml  scripts\n")
        elif cmd == "ps":
            self.process.stdout.write("  PID TTY          TIME CMD\n")
            self.process.stdout.write("    1 ?        00:00:02 systemd\n")
            self.process.stdout.write("   24 ?        00:00:00 sshd\n")
            self.process.stdout.write("  102 pts/0    00:00:00 bash\n")
        elif cmd == "cat":
            if len(args) > 1 and "shadow" in args[1]:
                self.process.stdout.write("cat: /etc/shadow: Permission denied\n")
            else:
                self.process.stdout.write("Binary file or not found.\n")
        else:
            self.process.stdout.write(f"{cmd}: command not found\n")
            
        self.prompt()

    def eof_received(self):
        self.process.exit(0)

class SSHHoneypotServer(asyncssh.SSHServer):
    def __init__(self, emit_callback):
        self.emit_callback = emit_callback

    def connection_made(self, conn):
        peer = conn.get_extra_info('peername')
        logger.info(f"SSH connection received from {peer}")
        self.emit_callback("ssh.connection.attempt", {
            "src_ip": peer[0],
            "src_port": peer[1]
        })

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        self.emit_callback("ssh.login.attempt", {
            "username": username,
            "password": password
        })
        # Accept any login to drop into interactive shell
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, username, key):
        self.emit_callback("ssh.key.attempt", {
            "username": username,
            "algorithm": key.get_algorithm()
        })
        return True

    def session_requested(self):
        return FakeShell

class SSHHoneypotPlugin(BasePlugin):
    def __init__(self, config: dict, delivery_callback):
        super().__init__(config, delivery_callback)
        self.port = config.get("port", 2222)
        self.host_keys = config.get("host_keys", ['ssh_host_rsa_key'])
        self.server = None

    async def handle_client(self, process):
        # asyncssh process handler
        username = process.channel.get_extra_info('username')
        shell = FakeShell(self.emit_event, username)
        shell.connection_made(process)
        
        while not process.stdin.at_eof():
            try:
                data = await process.stdin.read(1024)
                if data:
                    shell.data_received(data, None)
            except Exception:
                break
        shell.eof_received()

    async def start(self):
        self.is_running = True
        logger.info(f"Starting SSH Interactive Honeypot on port {self.port}...")
        
        for key_path in self.host_keys:
            if not __import__('os').path.exists(key_path):
                asyncssh.generate_private_key('ssh-rsa').write_private_key(key_path)
                
        try:
            self.server = await asyncssh.create_server(
                lambda: SSHHoneypotServer(self.emit_event),
                '', self.port,
                server_host_keys=self.host_keys,
                process_factory=self.handle_client
            )
            logger.info("SSH Honeypot started successfully.")
        except Exception as e:
            logger.error(f"Failed to start SSH Honeypot: {e}")
            self.is_running = False

    async def stop(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        self.is_running = False
        logger.info("SSH Honeypot stopped.")
