import asyncio
from aiohttp import web
import logging
from .base import BasePlugin

logger = logging.getLogger(__name__)

PERSONAS = {
    "jenkins": {
        "title": "Jenkins",
        "html": "<html><head><title>Dashboard [Jenkins]</title></head><body><h2>Jenkins Sign in</h2><form method='POST'>User: <input name='j_username'><br>Password: <input type='password' name='j_password'><br><input type='submit' value='Sign in'></form></body></html>",
    },
    "gitlab": {
        "title": "GitLab",
        "html": "<html><head><title>Sign in · GitLab</title></head><body><h2>GitLab Community Edition</h2><form method='POST'>Username or email: <input name='user[login]'><br>Password: <input type='password' name='user[password]'><br><input type='submit' value='Sign in'></form></body></html>",
    },
    "wordpress": {
        "title": "WordPress",
        "html": "<html><head><title>Log In &lsaquo; WordPress</title></head><body><form method='POST'>Username or Email Address: <input name='log'><br>Password: <input type='password' name='pwd'><br><input type='submit' value='Log In'></form></body></html>",
    },
    "jira": {
        "title": "Jira",
        "html": "<html><head><title>Log in - Jira</title></head><body><h2>Log in to your account</h2><form method='POST'>Email: <input name='username'><br>Password: <input type='password' name='password'><br><input type='submit' value='Log in'></form></body></html>",
    },
    "generic": {
        "title": "Admin Portal",
        "html": "<html><head><title>Admin Portal</title></head><body><h2>Authentication Required</h2><form method='POST'>Username: <input name='username'><br>Password: <input type='password' name='password'><br><input type='submit' value='Login'></form></body></html>",
    }
}

class HTTPHoneypotPlugin(BasePlugin):
    def __init__(self, config: dict, delivery_callback):
        super().__init__(config, delivery_callback)
        self.port = config.get("port", 8080)
        self.template = config.get("template", "generic")
        if self.template not in PERSONAS:
            self.template = "generic"
        
        self.app = web.Application()
        self.setup_routes()
        self.runner = None
        self.site = None

    def setup_routes(self):
        self.app.router.add_get('/', self.handle_get)
        self.app.router.add_get('/{tail:.*}', self.handle_get)
        self.app.router.add_post('/', self.handle_post)
        self.app.router.add_post('/{tail:.*}', self.handle_post)

    async def extract_request_data(self, request):
        peer = request.transport.get_extra_info('peername')
        headers = dict(request.headers)
        return {
            "src_ip": peer[0] if peer else "unknown",
            "method": request.method,
            "path": request.path,
            "user_agent": headers.get("User-Agent", ""),
            "host": headers.get("Host", ""),
            "persona": self.template
        }

    async def handle_get(self, request):
        data = await self.extract_request_data(request)
        self.emit_event("http.access", data)
        
        html = PERSONAS[self.template]["html"]
        return web.Response(text=html, content_type='text/html')

    async def handle_post(self, request):
        data = await self.extract_request_data(request)
        
        try:
            post_data = await request.post()
            data["submitted_data"] = dict(post_data)
        except Exception:
            data["submitted_data"] = "Failed to parse body"

        logger.info(f"HTTP Login Attempt on {self.template} persona: {data['submitted_data']}")
        self.emit_event("http.login.attempt", data)
        
        return web.Response(text="Invalid credentials. Please try again.", status=401)

    async def start(self):
        self.is_running = True
        logger.info(f"Starting HTTP Honeypot on port {self.port} with template '{self.template}'...")
        
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            logger.info("HTTP Honeypot started successfully.")
        except Exception as e:
            logger.error(f"Failed to start HTTP Honeypot: {e}")
            self.is_running = False

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()
        self.is_running = False
        logger.info("HTTP Honeypot stopped.")
