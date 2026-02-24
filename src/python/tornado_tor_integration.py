#!/usr/bin/env python3
"""
Tornado + Tor Integration for SPECTOR Admin Console
Provides Tor-enabled web requests with circuit management UI.
"""

import json
import logging
from typing import Optional, Dict, Any
import tornado.web
import tornado.websocket
import tornado.ioloop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from datetime import datetime

from tor_manager import TorManager

logger = logging.getLogger(__name__)


class TorProxyMixin:
    """Mixin to add Tor proxy support to Tornado request handlers."""
    
    tor_manager: Optional[TorManager] = None
    
    @classmethod
    def set_tor_manager(cls, tor_manager: TorManager):
        """Set global Tor manager instance."""
        cls.tor_manager = tor_manager
    
    async def fetch_via_tor(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Fetch URL through Tor proxy.
        
        Args:
            url: Target URL
            method: HTTP method
            headers: Request headers
            body: Request body
            **kwargs: Additional HTTPRequest arguments
        
        Returns:
            Response object
        """
        if not self.tor_manager or not self.tor_manager.is_running():
            raise RuntimeError("Tor not available")
        
        # Configure proxy
        proxy_host = "127.0.0.1"
        proxy_port = self.tor_manager.socks_port
        
        # Build request
        request = HTTPRequest(
            url,
            method=method,
            headers=headers or {},
            body=body,
            proxy_host=proxy_host,
            proxy_port=proxy_port,
            **kwargs
        )
        
        # Execute async request
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(request)
        
        return response


class TorStatusHandler(tornado.web.RequestHandler, TorProxyMixin):
    """API endpoint for Tor status."""
    
    def get(self):
        """Get current Tor status."""
        if not self.tor_manager:
            self.set_status(503)
            self.write({"error": "Tor manager not initialized"})
            return
        
        status = self.tor_manager.get_status()
        self.write(status)


class TorControlHandler(tornado.web.RequestHandler, TorProxyMixin):
    """API endpoint for Tor control operations."""
    
    async def post(self):
        """Execute Tor control command."""
        if not self.tor_manager:
            self.set_status(503)
            self.write({"error": "Tor manager not initialized"})
            return
        
        try:
            data = json.loads(self.request.body)
            action = data.get('action')
            
            if action == 'start':
                success = self.tor_manager.start()
                self.write({"success": success, "message": "Tor started" if success else "Failed to start Tor"})
            
            elif action == 'stop':
                success = self.tor_manager.stop()
                self.write({"success": success, "message": "Tor stopped" if success else "Failed to stop Tor"})
            
            elif action == 'renew_circuit':
                success = self.tor_manager.renew_circuit()
                new_ip = self.tor_manager.get_current_ip() if success else None
                self.write({"success": success, "new_ip": new_ip, "message": "Circuit renewed" if success else "Failed to renew circuit"})
            
            elif action == 'get_ip':
                ip = self.tor_manager.get_current_ip()
                self.write({"success": True, "ip": ip})
            
            else:
                self.set_status(400)
                self.write({"error": f"Unknown action: {action}"})
        
        except Exception as e:
            logger.error(f"Tor control error: {e}")
            self.set_status(500)
            self.write({"error": str(e)})


class TorCircuitHandler(tornado.web.RequestHandler, TorProxyMixin):
    """API endpoint for Tor circuit information."""
    
    def get(self):
        """Get circuit information."""
        if not self.tor_manager:
            self.set_status(503)
            self.write({"error": "Tor manager not initialized"})
            return
        
        circuit_info = self.tor_manager.get_circuit_info()
        self.write(circuit_info)


class TorWebSocketHandler(tornado.websocket.WebSocketHandler, TorProxyMixin):
    """WebSocket handler for real-time Tor status updates."""
    
    clients = set()
    
    def open(self):
        """Client connected."""
        self.clients.add(self)
        logger.info(f"Tor WebSocket client connected (total: {len(self.clients)})")
    
    def on_close(self):
        """Client disconnected."""
        self.clients.discard(self)
        logger.info(f"Tor WebSocket client disconnected (total: {len(self.clients)})")
    
    def on_message(self, message):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'get_status':
                if self.tor_manager:
                    status = self.tor_manager.get_status()
                    self.write_message(json.dumps({
                        'type': 'status',
                        'data': status,
                        'timestamp': datetime.utcnow().isoformat()
                    }))
        except Exception as e:
            logger.error(f"WebSocket message error: {e}")
            self.write_message(json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @classmethod
    def broadcast_status(cls, status: Dict[str, Any]):
        """Broadcast status to all connected clients."""
        message = json.dumps({
            'type': 'status_update',
            'data': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        for client in cls.clients:
            try:
                client.write_message(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to client: {e}")


class TorDashboardHandler(tornado.web.RequestHandler):
    """Render Tor dashboard UI."""
    
    def get(self):
        """Render dashboard HTML."""
        self.render("tor_dashboard.html")


def create_tor_routes(tor_manager: TorManager) -> list:
    """
    Create Tornado routes for Tor integration.
    
    Args:
        tor_manager: TorManager instance
    
    Returns:
        List of Tornado route tuples
    """
    # Set global Tor manager
    TorProxyMixin.set_tor_manager(tor_manager)
    
    return [
        (r"/api/tor/status", TorStatusHandler),
        (r"/api/tor/control", TorControlHandler),
        (r"/api/tor/circuits", TorCircuitHandler),
        (r"/ws/tor", TorWebSocketHandler),
        (r"/tor/dashboard", TorDashboardHandler),
    ]


# Periodic status broadcast
async def broadcast_tor_status(tor_manager: TorManager):
    """Periodically broadcast Tor status to WebSocket clients."""
    while True:
        try:
            await tornado.gen.sleep(5)  # Every 5 seconds
            
            if tor_manager and tor_manager.is_running():
                status = tor_manager.get_status()
                TorWebSocketHandler.broadcast_status(status)
        except Exception as e:
            logger.error(f"Error broadcasting Tor status: {e}")


if __name__ == "__main__":
    # Example Tornado app with Tor integration
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Tor
    tor = TorManager(auto_start=True)
    tor.start()
    
    # Create Tornado app
    app = tornado.web.Application(
        create_tor_routes(tor) + [
            (r"/", tornado.web.RedirectHandler, {"url": "/tor/dashboard"})
        ],
        template_path="templates",
        static_path="static",
        debug=True
    )
    
    # Start server
    port = 8889
    app.listen(port)
    print(f"Tor-enabled Tornado server running on http://localhost:{port}")
    
    # Start periodic status broadcast
    tornado.ioloop.IOLoop.current().spawn_callback(broadcast_tor_status, tor)
    
    # Start event loop
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        tor.stop()
