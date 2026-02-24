#!/usr/bin/env python3
"""
SPECTOR Tornado Admin Console

A web-based administration interface for SPECTOR with real-time monitoring,
job queue management, configuration, and system health metrics.

Features:
- Real-time system health monitoring
- Job queue status and management  
- Configuration management interface
- WebSocket support for live updates
- Basic authentication
- RESTful API endpoints

Usage:
    python -m spector.admin_console --port 8888 --host localhost
    
    Or via CLI:
    spector admin --port 8888 --host localhost
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("spector.admin")

# Define options
define("port", default=8888, help="Port to run admin console on", type=int)
define("host", default="localhost", help="Host to bind to", type=str)
define("debug", default=False, help="Enable debug mode", type=bool)
define("username", default="admin", help="Admin username", type=str)
define("password", default="spector", help="Admin password", type=str)


class BaseHandler(tornado.web.RequestHandler):
    """Base handler with authentication support."""
    
    def get_current_user(self):
        """Get current authenticated user from secure cookie."""
        return self.get_secure_cookie("user")
    
    def set_default_headers(self):
        """Set CORS and security headers."""
        self.set_header("X-Content-Type-Options", "nosniff")
        self.set_header("X-Frame-Options", "DENY")
        self.set_header("X-XSS-Protection", "1; mode=block")


class LoginHandler(BaseHandler):
    """Handle user authentication."""
    
    def get(self):
        """Show login page."""
        self.render("admin_login.html", error=None)
    
    def post(self):
        """Process login credentials."""
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        
        if username == options.username and password == options.password:
            self.set_secure_cookie("user", username)
            self.redirect("/")
        else:
            self.render("admin_login.html", error="Invalid credentials")


class LogoutHandler(BaseHandler):
    """Handle user logout."""
    
    def get(self):
        """Clear authentication and redirect to login."""
        self.clear_cookie("user")
        self.redirect("/login")


class DashboardHandler(BaseHandler):
    """Main dashboard view."""
    
    @tornado.web.authenticated
    def get(self):
        """Render admin dashboard."""
        self.render("templates/admin_dashboard.html")


class HealthAPIHandler(BaseHandler):
    """API endpoint for system health metrics."""
    
    @tornado.web.authenticated
    def get(self):
        """Return current system health status."""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": self.application.get_uptime(),
            "memory_usage_mb": self._get_memory_usage(),
            "cpu_percent": self._get_cpu_usage(),
            "active_connections": len(self.application.websocket_connections),
        }
        self.write(health_data)
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0


class JobsAPIHandler(BaseHandler):
    """API endpoint for job queue management."""
    
    @tornado.web.authenticated
    def get(self):
        """Get current job queue status."""
        jobs_data = {
            "total_jobs": 0,
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "jobs": []
        }
        
        # TODO: Integrate with actual SPECTOR job queue
        # For now, return sample data
        jobs_data["jobs"] = [
            {
                "id": "job-001",
                "type": "document_indexing",
                "status": "running",
                "progress": 45,
                "started_at": datetime.utcnow().isoformat()
            }
        ]
        
        self.write(jobs_data)


class ConfigAPIHandler(BaseHandler):
    """API endpoint for configuration management."""
    
    @tornado.web.authenticated
    def get(self):
        """Get current configuration."""
        config_data = {
            "spector_version": "1.0.0",
            "python_version": sys.version,
            "admin_console": {
                "host": options.host,
                "port": options.port,
                "debug": options.debug
            },
            "capabilities": self._get_capabilities()
        }
        self.write(config_data)
    
    def _get_capabilities(self) -> Dict:
        """Get system capabilities."""
        import importlib.util
        
        return {
            "cuda_available": importlib.util.find_spec("cupy") is not None,
            "neo4j_available": importlib.util.find_spec("neo4j") is not None,
            "qdrant_available": importlib.util.find_spec("qdrant_client") is not None,
        }


class MetricsAPIHandler(BaseHandler):
    """API endpoint for system metrics."""
    
    @tornado.web.authenticated
    def get(self):
        """Get system metrics over time."""
        metrics_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "requests_total": self.application.request_count,
                "requests_per_second": 0,  # TODO: Calculate
                "avg_response_time_ms": 0,  # TODO: Calculate
                "error_rate": 0  # TODO: Calculate
            }
        }
        self.write(metrics_data)


class MetricsWebSocket(tornado.websocket.WebSocketHandler):
    """WebSocket handler for real-time metrics streaming."""
    
    def open(self):
        """Handle new WebSocket connection."""
        logger.info("WebSocket connection opened")
        self.application.websocket_connections.add(self)
        self.set_nodelay(True)
    
    def on_close(self):
        """Handle WebSocket disconnection."""
        logger.info("WebSocket connection closed")
        self.application.websocket_connections.discard(self)
    
    async def on_message(self, message):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(message)
            command = data.get("command")
            
            if command == "subscribe":
                # Client subscribing to updates
                await self.send_update()
            elif command == "ping":
                # Heartbeat
                await self.write_message(json.dumps({"type": "pong"}))
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
    
    async def send_update(self):
        """Send metrics update to client."""
        update = {
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "active_jobs": 0,
                "requests_total": self.application.request_count,
                "connections": len(self.application.websocket_connections)
            }
        }
        await self.write_message(json.dumps(update))


class TornadoAdminServer(tornado.web.Application):
    """Main Tornado admin console application."""
    
    def __init__(self, host: str = "localhost", port: int = 8888, **kwargs):
        """
        Initialize the admin server.
        
        Args:
            host: Host to bind to
            port: Port to listen on
            **kwargs: Additional Tornado application settings
        """
        self.host = host
        self.port = port
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.websocket_connections = set()
        
        # Configure templates path
        templates_path = Path(__file__).parent.parent.parent / "docs"
        if not templates_path.exists():
            # Try alternative path
            templates_path = Path(__file__).parent / "templates"
        if not templates_path.exists():
            logger.warning("Templates directory not found, using embedded templates")
        
        settings = {
            "cookie_secret": self._generate_cookie_secret(),
            "login_url": "/login",
            "template_path": str(templates_path) if templates_path else None,
            "static_path": None,  # No static files for now
            "debug": options.debug,
            "autoreload": options.debug,
            **kwargs
        }
        
        handlers = [
            (r"/", DashboardHandler),
            (r"/login", LoginHandler),
            (r"/logout", LogoutHandler),
            (r"/api/health", HealthAPIHandler),
            (r"/api/jobs", JobsAPIHandler),
            (r"/api/config", ConfigAPIHandler),
            (r"/api/metrics", MetricsAPIHandler),
            (r"/ws/metrics", MetricsWebSocket),
        ]
        
        super().__init__(handlers, **settings)
        
        logger.info(f"Admin console initialized on {host}:{port}")
    
    def _generate_cookie_secret(self) -> str:
        """Generate a secure cookie secret."""
        import secrets
        return secrets.token_hex(32)
    
    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()
    
    def start(self):
        """Start the admin console server."""
        try:
            self.listen(self.port, address=self.host)
            logger.info(f"🚀 SPECTOR Admin Console started")
            logger.info(f"📊 Dashboard: http://{self.host}:{self.port}")
            logger.info(f"🔑 Login: admin / spector (default credentials)")
            logger.info(f"Press Ctrl+C to stop")
            
            # Start periodic tasks
            self._start_periodic_tasks()
            
            # Start IO loop
            tornado.ioloop.IOLoop.current().start()
        except KeyboardInterrupt:
            logger.info("Shutting down admin console...")
            self.stop()
        except Exception as e:
            logger.error(f"Failed to start admin console: {e}")
            raise
    
    def stop(self):
        """Stop the admin console server."""
        logger.info("Stopping admin console...")
        tornado.ioloop.IOLoop.current().stop()
    
    def _start_periodic_tasks(self):
        """Start periodic background tasks."""
        # Broadcast metrics to WebSocket clients every 5 seconds
        tornado.ioloop.PeriodicCallback(
            self._broadcast_metrics, 5000
        ).start()
    
    async def _broadcast_metrics(self):
        """Broadcast metrics to all connected WebSocket clients."""
        if not self.websocket_connections:
            return
        
        update = {
            "type": "metrics_update",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "uptime": self.get_uptime(),
                "requests": self.request_count,
                "connections": len(self.websocket_connections)
            }
        }
        
        message = json.dumps(update)
        for ws in self.websocket_connections:
            try:
                await ws.write_message(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")


def main():
    """Main entry point for standalone execution."""
    tornado.options.parse_command_line()
    
    server = TornadoAdminServer(
        host=options.host,
        port=options.port
    )
    
    server.start()


if __name__ == "__main__":
    main()
